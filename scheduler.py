"""
scheduler.py
Run the agent automatically on a schedule (e.g., every morning at 9am)
"""

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from main import run_agent

log = logging.getLogger(__name__)


async def scheduled_run():
    log.info("⏰ Scheduled job run triggered")
    try:
        await run_agent()
    except Exception as e:
        log.error(f"Agent run failed: {e}")


async def main():
    scheduler = AsyncIOScheduler()

    # Run every weekday at 9:00 AM
    scheduler.add_job(
        scheduled_run,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=0),
        id="job_hunt",
        name="LinkedIn Job Hunter"
    )

    scheduler.start()
    log.info("🕘 Scheduler started — running every weekday at 9:00 AM")
    log.info("   Press Ctrl+C to stop\n")

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())