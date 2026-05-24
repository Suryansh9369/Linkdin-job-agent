"""
LinkedIn Job Hunter Agent
Crawls LinkedIn → Filters jobs via AI → Sends personalized emails
"""

import sys
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime
from config import CONFIG
from scraper.linkedin_scraper import LinkedInScraper
from ai.job_filter import JobFilter
from ai.email_writer import EmailWriter
from mailer.email_sender import EmailSender
from storage.db import JobDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


async def run_agent():
    log.info("🤖 Job Hunter Agent starting...")

    db = JobDatabase()
    scraper = LinkedInScraper()
    job_filter = JobFilter()
    email_writer = EmailWriter()
    sender = EmailSender()

    # 1. Scrape LinkedIn jobs
    log.info("🔍 Scraping LinkedIn for jobs...")
    raw_jobs = await scraper.search_jobs(
        keywords=CONFIG["job_keywords"],
        location=CONFIG["location"],
        max_results=CONFIG["max_jobs_per_run"]
    )
    log.info(f"   Found {len(raw_jobs)} raw jobs")

    # 2. Filter out already-applied jobs
    new_jobs = [j for j in raw_jobs if not db.already_applied(j["job_id"])]
    log.info(f"   {len(new_jobs)} new (not yet applied)")

    # 3. AI-filter jobs by preference
    log.info("🧠 AI filtering jobs by your preferences...")
    matched_jobs = await job_filter.filter_jobs(new_jobs, CONFIG["preferences"])
    log.info(f"   {len(matched_jobs)} jobs matched your profile")

    if not matched_jobs:
        log.info("No matching jobs found this run. Try again later!")
        return

    # 4. For each match: write email + send
    results = []
    for job in matched_jobs[:CONFIG["max_emails_per_run"]]:
        log.info(f"\n📧 Processing: {job['title']} at {job['company']}")

        # Write personalized email
        email_content = await email_writer.compose(
            job=job,
            your_name=CONFIG["your_name"],
            your_background=CONFIG["your_background"]
        )

        # Send email with resume attached
        success = sender.send(
            to_email=job.get("contact_email") or CONFIG["fallback_email"],
            subject=email_content["subject"],
            body=email_content["body"],
            attachments=CONFIG["attachments"]
        )

        status = "✅ Sent" if success else "❌ Failed"
        log.info(f"   {status} → {job.get('contact_email', 'fallback')}")

        # Save to DB to avoid re-applying
        db.mark_applied(job["job_id"], job["title"], job["company"], success)
        results.append({"job": job, "success": success})

    # Summary
    sent = sum(1 for r in results if r["success"])
    log.info(f"\n🎯 Run complete: {sent}/{len(results)} emails sent successfully")
    log.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(run_agent())