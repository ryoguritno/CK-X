import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.scheduler import _send_morning, _send_evening, setup_scheduler


def make_state(task=None, step=None, completed_today=0):
    state = MagicMock()
    state.get_current_task.return_value = task
    state.get_current_step.return_value = step
    state.get_steps_completed_today.return_value = completed_today
    return state


@pytest.mark.asyncio
async def test_morning_sends_task_and_step():
    bot = AsyncMock()
    state = make_state(
        task={"id": 1, "title": "Task 1: Setup", "phase": 1},
        step={"content": "Step 1: Do thing A"},
    )
    await _send_morning(bot, state, "12345")
    bot.send_message.assert_called_once()
    text = bot.send_message.call_args.kwargs["text"]
    assert "Task 1: Setup" in text
    assert "Step 1: Do thing A" in text


@pytest.mark.asyncio
async def test_morning_all_tasks_complete():
    bot = AsyncMock()
    state = make_state(task=None, step=None)
    await _send_morning(bot, state, "12345")
    text = bot.send_message.call_args.kwargs["text"]
    assert "All tasks complete" in text


@pytest.mark.asyncio
async def test_evening_nudge_when_no_progress():
    bot = AsyncMock()
    state = make_state(
        task={"id": 1, "title": "Task 1: Setup", "phase": 1},
        step={"content": "Step 1: Do thing A"},
        completed_today=0,
    )
    await _send_evening(bot, state, "12345")
    text = bot.send_message.call_args.kwargs["text"]
    assert "no progress" in text
    assert "Step 1: Do thing A" in text


@pytest.mark.asyncio
async def test_evening_praise_when_progress():
    bot = AsyncMock()
    state = make_state(
        task={"id": 1, "title": "Task 1: Setup", "phase": 1},
        completed_today=2,
    )
    await _send_evening(bot, state, "12345")
    text = bot.send_message.call_args.kwargs["text"]
    assert "2 step(s)" in text
    assert "Nice work" in text


def test_setup_scheduler_returns_scheduler():
    bot = MagicMock()
    state = MagicMock()
    scheduler = setup_scheduler(
        bot=bot,
        state_manager=state,
        chat_id="12345",
        morning_time="07:00",
        evening_time="19:00",
        timezone="Asia/Jakarta",
    )
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    job_ids = {j.id for j in jobs}
    assert "morning_notification" in job_ids
    assert "evening_notification" in job_ids
