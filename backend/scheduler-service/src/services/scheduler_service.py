import logging
from typing import Any, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger

from src.services.desk_service import DeskService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled desk operations."""

    def __init__(self) -> None:
        # In-memory scheduler by default (no jobstore).
        # You can swap to a DB jobstore later.
        self.scheduler = BackgroundScheduler()
        logger.info("Scheduler service initialized (not started yet)")

    # -------- lifecycle --------
    def start(self) -> None:
        """Start the scheduler if not already running."""
        if self.scheduler.state != STATE_RUNNING:
            self.scheduler.start()
            logger.info("Scheduler started")
        else:
            logger.info("Scheduler already running; start() skipped")

    def shutdown(self) -> None:
        """Shutdown the scheduler if running."""
        if self.scheduler.state == STATE_RUNNING:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler service shut down")
        else:
            logger.info("Scheduler not running; shutdown() skipped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.scheduler.state == STATE_RUNNING

    # -------- info --------
    def get_jobs_count(self) -> int:
        """Get the number of scheduled jobs."""
        return len(self.scheduler.get_jobs())

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat()
                if job.next_run_time
                else None,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]

    # -------- actions --------
    def add_schedule(  # noqa: PLR0913
        self,
        job_id: str,
        name: str,
        action: str,
        position_mm: int,
        hour: int,
        minute: int,
        day_of_week: str = "*",
    ) -> Dict[str, Any]:
        """Add a new scheduled job.

        Returns:
            {"job_id": <str>, "next_run": <iso8601 or None>}

        """
        action_norm = (action or "").strip().lower()
        if action_norm not in {"raise", "lower"}:
            raise ValueError(f"Invalid action: {action}. Use 'raise' or 'lower'.")

        if not isinstance(position_mm, int) or position_mm <= 0:
            raise ValueError("position_mm must be a positive integer (millimeters).")

        # Map action -> callable
        def _job_func() -> None:
            context = {
                "trigger": "schedule",
                "job_id": job_id,
                "job_name": name,
            }

            if action_norm == "raise":
                DeskService.raise_all_desks(position_mm, context=context)
            else:
                DeskService.lower_all_desks(position_mm, context=context)

        # Build cron trigger
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,  # e.g. '*', 'mon-fri', '0-6'
        )

        # Add (or replace) job
        job = self.scheduler.add_job(
            _job_func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True,
            coalesce=True,  # optional: collapse missed runs into one
            max_instances=1,  # optional: avoid overlapping same job
        )

        logger.info(
            "Added/updated schedule: id=%s name=%s action=%s pos=%s cron=%s next=%s",
            job.id,
            name,
            action_norm,
            position_mm,
            str(trigger),
            job.next_run_time.isoformat() if job.next_run_time else None,
        )

        return {
            "job_id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }

    def remove_schedule(self, job_id: str) -> None:
        """Remove a scheduled job."""
        self.scheduler.remove_job(job_id)
        logger.info("Removed schedule: %s", job_id)

    # -------- defaults --------
    def setup_default_schedules(self) -> None:
        """Set up default schedules (idempotent via replace_existing=True)."""
        try:
            # Cleaning mode: raise desks at 20:00 every day
            self.add_schedule(
                job_id="cleaning_start",
                name="Start Cleaning Mode",
                action="raise",
                position_mm=1200,
                hour=20,
                minute=0,
                day_of_week="*",
            )

            # End cleaning mode: lower desks at 21:00 every day
            self.add_schedule(
                job_id="cleaning_end",
                name="End Cleaning Mode",
                action="lower",
                position_mm=680,
                hour=21,
                minute=0,
                day_of_week="*",
            )

            # Morning standup on weekdays
            self.add_schedule(
                job_id="morning_standup",
                name="Morning Standup",
                action="raise",
                position_mm=1100,
                hour=9,
                minute=0,
                day_of_week="mon-fri",
            )

            logger.info("Default schedules initialized")
        except Exception as e:
            logger.exception("Error setting up default schedules: %s", e)


# Global scheduler instance
scheduler_service = SchedulerService()
