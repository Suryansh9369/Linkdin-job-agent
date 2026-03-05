"""
storage/db.py
SQLite database to track which jobs you've already applied to
"""

import sqlite3
import logging
from datetime import datetime

log = logging.getLogger(__name__)
DB_PATH = "storage/jobs.db"


class JobDatabase:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applied_jobs (
                    job_id      TEXT PRIMARY KEY,
                    title       TEXT,
                    company     TEXT,
                    applied_at  TEXT,
                    email_sent  INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def already_applied(self, job_id: str) -> bool:
        """Check if we've already applied to this job."""
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT 1 FROM applied_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        return row is not None

    def mark_applied(self, job_id: str, title: str, company: str, email_sent: bool):
        """Record that we've applied to a job."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """INSERT OR IGNORE INTO applied_jobs 
                   (job_id, title, company, applied_at, email_sent) 
                   VALUES (?, ?, ?, ?, ?)""",
                (job_id, title, company, datetime.now().isoformat(), int(email_sent))
            )
            conn.commit()
        log.debug(f"  Saved: {title} @ {company}")

    def get_all_applied(self) -> list:
        """Return all applied jobs for review."""
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT job_id, title, company, applied_at, email_sent FROM applied_jobs ORDER BY applied_at DESC"
            ).fetchall()
        return [
            {"job_id": r[0], "title": r[1], "company": r[2], "applied_at": r[3], "email_sent": bool(r[4])}
            for r in rows
        ]

    def stats(self) -> dict:
        """Return stats about your job hunt."""
        with sqlite3.connect(DB_PATH) as conn:
            total = conn.execute("SELECT COUNT(*) FROM applied_jobs").fetchone()[0]
            sent = conn.execute("SELECT COUNT(*) FROM applied_jobs WHERE email_sent=1").fetchone()[0]
        return {"total_applied": total, "emails_sent": sent}