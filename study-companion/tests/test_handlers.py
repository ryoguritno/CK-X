import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, Chat
from telegram.ext import ContextTypes
from bot.handlers import (
    cmd_today, cmd_done, cmd_progress, cmd_session,
    cmd_explain, cmd_hint, cmd_quiz, cmd_skip
)


def make_update():
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


def make_context(state=None, mentor=None, args=None):
    ctx = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.bot_data = {"state": state or MagicMock(), "mentor": mentor or AsyncMock()}
    ctx.args = args or []
    return ctx


# --- /today ---

@pytest.mark.asyncio
async def test_today_shows_task_and_steps():
    state = MagicMock()
    state.get_current_task.return_value = {"id": 1, "title": "Task 1: Setup", "phase": 1}
    state.get_task_steps.return_value = [
        {"content": "Step A", "status": "completed"},
        {"content": "Step B", "status": "pending"},
    ]
    update = make_update()
    ctx = make_context(state=state)
    await cmd_today(update, ctx)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Task 1: Setup" in text
    assert "✅" in text
    assert "⬜" in text


@pytest.mark.asyncio
async def test_today_no_task():
    state = MagicMock()
    state.get_current_task.return_value = None
    update = make_update()
    ctx = make_context(state=state)
    await cmd_today(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "All tasks completed" in text


# --- /done ---

@pytest.mark.asyncio
async def test_done_completes_step_and_shows_next():
    state = MagicMock()
    state.get_current_step.return_value = {"id": 1, "content": "Step A"}
    state.complete_step.return_value = {"id": 2, "content": "Step B"}
    update = make_update()
    ctx = make_context(state=state)
    await cmd_done(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "Step A" in text
    assert "Step B" in text


@pytest.mark.asyncio
async def test_done_no_step():
    state = MagicMock()
    state.get_current_step.return_value = None
    update = make_update()
    ctx = make_context(state=state)
    await cmd_done(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "No pending step" in text


# --- /progress ---

@pytest.mark.asyncio
async def test_progress_shows_stats():
    state = MagicMock()
    state.get_progress.return_value = {
        "pct": 25, "done_steps": 5, "total_steps": 20,
        "phase": 1, "current_task": {"title": "Task 1: Setup"},
        "total_sessions": 3, "streak": 2,
    }
    update = make_update()
    ctx = make_context(state=state)
    await cmd_progress(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "25%" in text
    assert "streak" in text.lower()


# --- /session ---

@pytest.mark.asyncio
async def test_session_start():
    state = MagicMock()
    state.get_active_session.return_value = None
    state.get_current_task.return_value = {"id": 1, "title": "Task 1", "phase": 1}
    update = make_update()
    ctx = make_context(state=state, args=["start"])
    await cmd_session(update, ctx)
    state.start_session.assert_called_once_with(1)
    text = update.message.reply_text.call_args[0][0]
    assert "Session started" in text


@pytest.mark.asyncio
async def test_session_end():
    state = MagicMock()
    state.get_active_session.return_value = {"id": 5}
    state.end_session.return_value = 30
    update = make_update()
    ctx = make_context(state=state, args=["end", "studied", "iptables"])
    await cmd_session(update, ctx)
    state.end_session.assert_called_once_with(5, "studied iptables")
    text = update.message.reply_text.call_args[0][0]
    assert "30 minute(s)" in text


# --- /explain ---

@pytest.mark.asyncio
async def test_explain_calls_mentor():
    mentor = AsyncMock()
    mentor.is_reachable = AsyncMock(return_value=True)
    mentor.explain = AsyncMock(return_value="NetworkPolicy controls pod traffic.")
    state = MagicMock()
    state.get_current_task.return_value = {"id": 1, "title": "Task 10", "phase": 2}
    update = make_update()
    ctx = make_context(state=state, mentor=mentor, args=["NetworkPolicy"])
    await cmd_explain(update, ctx)
    mentor.explain.assert_called_once_with("NetworkPolicy", "Task 10", 2)


@pytest.mark.asyncio
async def test_explain_ollama_offline():
    mentor = AsyncMock()
    mentor.is_reachable = AsyncMock(return_value=False)
    update = make_update()
    ctx = make_context(mentor=mentor, args=["NetworkPolicy"])
    await cmd_explain(update, ctx)
    text = update.message.reply_text.call_args[0][0]
    assert "offline" in text.lower()


# --- /hint ---

@pytest.mark.asyncio
async def test_hint_calls_mentor():
    mentor = AsyncMock()
    mentor.is_reachable = AsyncMock(return_value=True)
    mentor.hint = AsyncMock(return_value="Think about packet flow.")
    state = MagicMock()
    state.get_current_step.return_value = {"id": 1, "content": "Step 2: iptables"}
    state.get_current_task.return_value = {"id": 1, "title": "Task 10", "phase": 2}
    update = make_update()
    ctx = make_context(state=state, mentor=mentor)
    await cmd_hint(update, ctx)
    mentor.hint.assert_called_once_with("Step 2: iptables", "Task 10")


# --- /skip ---

@pytest.mark.asyncio
async def test_skip_with_reason():
    state = MagicMock()
    state.get_current_step.return_value = {"id": 1, "content": "Step A"}
    state.skip_step.return_value = {"id": 2, "content": "Step B"}
    update = make_update()
    ctx = make_context(state=state, args=["already", "know", "this"])
    await cmd_skip(update, ctx)
    state.skip_step.assert_called_once_with(1, "already know this")
    text = update.message.reply_text.call_args[0][0]
    assert "Step A" in text
    assert "Step B" in text
