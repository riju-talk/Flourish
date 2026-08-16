from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from ..core.config import settings
from ..services.scheduler_service import (
    run_streak_risk_sweep,
    run_task_due_digest,
    run_weekly_summary,
)

router = APIRouter()


def _require_cron_secret(authorization: Optional[str]) -> None:
    """
    Stand-in for verify_firebase_token on these routes: called by an external
    scheduler (GitHub Actions cron), not a signed-in user, so it checks a shared
    secret instead of a Firebase ID token. See scheduler_service.start_scheduler's
    docstring for why this exists at all - Vercel has no persistent process for an
    in-process APScheduler to run in.
    """
    if not settings.CRON_SECRET:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="CRON_SECRET is not configured")
    expected = f"Bearer {settings.CRON_SECRET}"
    if not authorization or authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")


@router.post("/streak-risk-sweep")
async def streak_risk_sweep(authorization: Optional[str] = Header(None)):
    _require_cron_secret(authorization)
    await run_streak_risk_sweep()
    return {"status": "ok", "job": "streak_risk_sweep"}


@router.post("/task-due-digest")
async def task_due_digest(authorization: Optional[str] = Header(None)):
    _require_cron_secret(authorization)
    await run_task_due_digest()
    return {"status": "ok", "job": "task_due_digest"}


@router.post("/weekly-summary")
async def weekly_summary(authorization: Optional[str] = Header(None)):
    _require_cron_secret(authorization)
    await run_weekly_summary()
    return {"status": "ok", "job": "weekly_summary"}
