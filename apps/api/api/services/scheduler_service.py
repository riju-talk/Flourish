from datetime import datetime, date
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..db.firestore import FirestoreDB
from .email_service import EmailService

_scheduler: Optional[AsyncIOScheduler] = None

async def _streak_risk_sweep() -> None:
    """Every hour: warn users whose streak is 20-24h from lapsing."""
    try:
        profiles = await FirestoreDB.get_all_profiles()
        now = datetime.now()
        for profile in profiles:
            user_id = profile.get("id")
            streak_days = profile.get("streak_days", 0)
            last_activity = profile.get("last_activity")
            if not streak_days or not last_activity:
                continue
            try:
                last_dt = datetime.fromisoformat(str(last_activity).replace('Z', '+00:00')).replace(tzinfo=None)
            except (ValueError, TypeError):
                continue

            hours_since = (now - last_dt).total_seconds() / 3600
            if 20 <= hours_since < 24:
                title = "Your streak is at risk! 🔥"
                message = f"Complete a care task today to keep your {streak_days}-day streak alive."
                await FirestoreDB.create_notification({
                    "user_id": user_id,
                    "type": "streak_risk",
                    "title": title,
                    "message": message,
                    "read": False
                })
                await EmailService.send_for_notification(user_id, "streak_risk", title, message, trigger="scheduled")
    except Exception as e:
        print(f"Streak-risk sweep error: {e}")

async def _task_due_digest() -> None:
    """Daily at 08:00: notify users who have tasks due today."""
    try:
        profiles = await FirestoreDB.get_all_profiles()
        today = date.today()
        for profile in profiles:
            user_id = profile.get("id")
            tasks = await FirestoreDB.get_user_tasks(user_id, completed=False)
            due_today = []
            for task in tasks:
                due_date = task.get("due_date")
                if not due_date:
                    continue
                try:
                    task_date = datetime.fromisoformat(str(due_date).replace('Z', '+00:00')).date()
                except (ValueError, TypeError):
                    continue
                if task_date == today:
                    due_today.append(task)

            if due_today:
                title = "Today's care tasks 🌿"
                message = f"You have {len(due_today)} task(s) due today."
                await FirestoreDB.create_notification({
                    "user_id": user_id,
                    "type": "task_due",
                    "title": title,
                    "message": message,
                    "read": False
                })
                await EmailService.send_for_notification(user_id, "task_due", title, message, trigger="scheduled")
    except Exception as e:
        print(f"Task-due digest error: {e}")

async def _weekly_summary() -> None:
    """Weekly on Monday 09:00: send an engagement summary email."""
    try:
        profiles = await FirestoreDB.get_all_profiles()
        for profile in profiles:
            user_id = profile.get("id")
            subject = "Your week in the garden 🌿"
            html = (
                f"<p>Level {profile.get('level', 1)} · {profile.get('total_score', 0)} points · "
                f"{profile.get('streak_days', 0)}-day streak.</p>"
                f"<p>{profile.get('tasks_completed', 0)} tasks completed all-time. Keep it up!</p>"
            )
            await EmailService.send_digest(user_id, subject, html)
    except Exception as e:
        print(f"Weekly summary error: {e}")

def start_scheduler() -> AsyncIOScheduler:
    """
    Start the in-process job scheduler. Only reliable because the deployed backend is
    kept warm by the keep-alive CI ping - see docs/02-Tech-Stack-Architecture.md §2.
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = AsyncIOScheduler()
    scheduler.add_job(_streak_risk_sweep, CronTrigger(minute=0), id="streak_risk_sweep", replace_existing=True)
    scheduler.add_job(_task_due_digest, CronTrigger(hour=8, minute=0), id="task_due_digest", replace_existing=True)
    scheduler.add_job(_weekly_summary, CronTrigger(day_of_week="mon", hour=9, minute=0), id="weekly_summary", replace_existing=True)
    scheduler.start()
    _scheduler = scheduler
    return scheduler

def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
