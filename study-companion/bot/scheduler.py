import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


def setup_scheduler(
    bot,
    state_manager,
    chat_id: str,
    morning_time: str,
    evening_time: str,
    timezone: str,
) -> AsyncIOScheduler:
    tz = pytz.timezone(timezone)
    scheduler = AsyncIOScheduler(timezone=tz)

    morning_h, morning_m = map(int, morning_time.split(":"))
    evening_h, evening_m = map(int, evening_time.split(":"))

    scheduler.add_job(
        _send_morning,
        CronTrigger(hour=morning_h, minute=morning_m, timezone=tz),
        args=[bot, state_manager, chat_id],
        id="morning_notification",
        replace_existing=True,
    )
    scheduler.add_job(
        _send_evening,
        CronTrigger(hour=evening_h, minute=evening_m, timezone=tz),
        args=[bot, state_manager, chat_id],
        id="evening_notification",
        replace_existing=True,
    )

    return scheduler


async def _send_morning(bot, state, chat_id: str) -> None:
    task = state.get_current_task()
    step = state.get_current_step()
    if not task:
        await bot.send_message(chat_id=chat_id, text="All tasks complete! Check /progress.")
        return
    step_text = (
        f"▸ {step['content']}" if step
        else "All steps in this task done — use /done to confirm."
    )
    msg = (
        f"Good morning!\n\n"
        f"Today's task: {task['title']}\n"
        f"Phase: {task['phase']}\n\n"
        f"Your next step:\n{step_text}\n\n"
        f"Type /hint if you need a nudge. Type /session start when you begin."
    )
    await bot.send_message(chat_id=chat_id, text=msg)


async def _send_evening(bot, state, chat_id: str) -> None:
    completed_today = state.get_steps_completed_today()
    task = state.get_current_task()
    step = state.get_current_step()

    if completed_today == 0:
        step_text = (
            f"▸ {step['content']}" if step
            else "check /today for your next step"
        )
        msg = (
            f"Hey — no progress logged today.\n\n"
            f"Your next step:\n{step_text}\n\n"
            f"Even 15 minutes counts. Type /session start to begin."
        )
    else:
        task_title = task["title"] if task else "roadmap complete"
        msg = (
            f"Nice work today — you completed {completed_today} step(s).\n\n"
            f"Current task: {task_title}\n\n"
            f"See you tomorrow."
        )
    await bot.send_message(chat_id=chat_id, text=msg)
