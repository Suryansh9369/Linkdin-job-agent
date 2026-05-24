"""
view_jobs.py — Run anytime to see all jobs the agent found and applied to
Usage: python view_jobs.py
"""

from storage.db import JobDatabase

db = JobDatabase()
jobs = db.get_all_applied()
stats = db.stats()

print("\n" + "="*55)
print("  JOB HUNTER — APPLICATION TRACKER")
print("="*55)
print(f"  Total applied : {stats['total_applied']}")
print(f"  Emails sent   : {stats['emails_sent']}")
print("="*55)

if not jobs:
    print("\n  No jobs yet — agent hasn't finished running.\n")
else:
    for i, job in enumerate(jobs, 1):
        status = "SENT" if job["email_sent"] else "FAILED"
        print(f"\n  {i}. {job['title']}")
        print(f"     Company  : {job['company']}")
        print(f"     Applied  : {job['applied_at'][:16]}")
        print(f"     Email    : {status}")

print("\n" + "="*55 + "\n")