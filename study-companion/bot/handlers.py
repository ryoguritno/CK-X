import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    task = state.get_current_task()
    if not task:
        await update.message.reply_text(
            "All tasks completed! Use /progress to review your journey."
        )
        return

    steps = state.get_task_steps(task["id"])
    lines = [f"Task: {task['title']}\nPhase {task['phase']}\n"]
    for s in steps:
        if s["status"] == "completed":
            icon = "✅"
        elif s["status"] == "skipped":
            icon = "⏭"
        else:
            icon = "⬜"
        lines.append(f"{icon} {s['content']}")

    await update.message.reply_text("\n".join(lines))


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    step = state.get_current_step()
    if not step:
        await update.message.reply_text(
            "No pending step found. Use /today to check your task."
        )
        return

    next_step = state.complete_step(step["id"])
    if next_step:
        await update.message.reply_text(
            f"✅ Completed: {step['content']}\n\n"
            f"Next step:\n▸ {next_step['content']}"
        )
    else:
        task = state.get_current_task()
        if task:
            await update.message.reply_text(
                f"✅ Completed: {step['content']}\n\n"
                f"All steps done! Next task: {task['title']}"
            )
        else:
            await update.message.reply_text("✅ All tasks complete! Amazing work.")


async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    p = state.get_progress()
    task_title = p["current_task"]["title"] if p["current_task"] else "All complete!"
    msg = (
        f"Progress: {p['pct']}% ({p['done_steps']}/{p['total_steps']} steps)\n"
        f"Phase: {p['phase']}\n"
        f"Current task: {task_title}\n"
        f"Sessions completed: {p['total_sessions']}\n"
        f"Study streak: {p['streak']} day(s)"
    )
    await update.message.reply_text(msg)


async def cmd_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    args = context.args or []

    if not args:
        await update.message.reply_text(
            "Usage:\n/session start\n/session end [optional notes]"
        )
        return

    action = args[0].lower()

    if action == "start":
        active = state.get_active_session()
        if active:
            await update.message.reply_text(
                "Session already active. Use /session end first."
            )
            return
        task = state.get_current_task()
        task_id = task["id"] if task else 0
        state.start_session(task_id)
        await update.message.reply_text(
            "Session started. Good luck! Use /session end [notes] when done."
        )

    elif action == "end":
        active = state.get_active_session()
        if not active:
            await update.message.reply_text(
                "No active session. Use /session start first."
            )
            return
        notes = " ".join(args[1:]) if len(args) > 1 else ""
        duration = state.end_session(active["id"], notes)
        reply = f"Session ended. Duration: {duration} minute(s)."
        if notes:
            reply += f"\nNotes: {notes}"
        await update.message.reply_text(reply)

    else:
        await update.message.reply_text(
            "Usage:\n/session start\n/session end [optional notes]"
        )


async def cmd_explain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not context.args:
        await update.message.reply_text(
            "Usage: /explain <topic>\nExample: /explain NetworkPolicy"
        )
        return

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    topic = " ".join(context.args)
    task = state.get_current_task()
    task_title = task["title"] if task else "general DevOps"
    phase = task["phase"] if task else 1

    await update.message.reply_text("Thinking...")
    answer = await mentor.explain(topic, task_title, phase)
    await update.message.reply_text(answer)


async def cmd_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    step = state.get_current_step()
    if not step:
        await update.message.reply_text(
            "No active step. Use /today to check your task."
        )
        return

    task = state.get_current_task()
    task_title = task["title"] if task else "current task"

    await update.message.reply_text("Thinking...")
    hint = await mentor.hint(step["content"], task_title)
    await update.message.reply_text(hint)


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    task = state.get_current_task()
    if not task:
        await update.message.reply_text(
            "No active task. Use /progress to check your state."
        )
        return

    await update.message.reply_text("Generating quiz question...")
    question = await mentor.quiz(task["title"], task["phase"])
    await update.message.reply_text(question)


async def cmd_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    step = state.get_current_step()
    if not step:
        await update.message.reply_text("No pending step to skip.")
        return

    reason = " ".join(context.args) if context.args else "no reason given"
    next_step = state.skip_step(step["id"], reason)

    msg = f"⏭ Skipped: {step['content']}\nReason: {reason}\n\n"
    if next_step:
        msg += f"Next step:\n▸ {next_step['content']}"
    else:
        msg += "No more steps in current task."
    await update.message.reply_text(msg)
