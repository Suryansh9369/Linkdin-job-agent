"""
config.py — Customize everything here before running the agent
"""
from dotenv import load_dotenv
import os

load_dotenv()  # Reads your .env file automatically

CONFIG = {
    # ─── Your Identity ────────────────────────────────────────────────
    "your_name": "Your Full Name",
    "your_email": os.getenv("SMTP_USER"),            # Your sending email
    "your_background": """
        Senior Software Engineer with 5 years of experience in Python, 
        FastAPI, React, and cloud infrastructure (AWS/GCP). 
        Passionate about building scalable products and developer tooling.
        Previous experience at [Company A] and [Company B].
        Open-source contributor. Looking for backend or full-stack roles.
    """,

    # ─── Job Search Preferences ───────────────────────────────────────
    "job_keywords": ["Software Engineer", "Backend Developer", "Python Developer"],
    "location": "Remote",                   # e.g. "New York", "Remote", "London"
    "max_jobs_per_run": 50,                 # Jobs to scrape per run
    "max_emails_per_run": 10,              # Max emails to send per run (be respectful!)

    "preferences": {
        "must_have": ["Python", "remote", "senior"],
        "nice_to_have": ["FastAPI", "AWS", "startup"],
        "avoid": ["unpaid", "internship", "junior", "PHP"],
        "min_salary": 100000,              # USD (if listed)
        "company_size": ["startup", "mid-size"],  # or "enterprise"
    },

    # ─── Email Settings ───────────────────────────────────────────────
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user":     os.getenv("SMTP_USER"),         # <- from .env
    "smtp_password": os.getenv("SMTP_PASSWORD"),     # <- from .env

    # Fallback if no recruiter email found on LinkedIn
    "fallback_email": None,               # Set to None to skip if no email found

    # ─── Attachments ─────────────────────────────────────────────────
    "attachments": [
        "attachments/resume.pdf",         # Required
        # "attachments/portfolio.pdf",    # Optional
        # "attachments/cover_letter.pdf", # Optional
    ],

    # ─── API Keys (all loaded from .env) ─────────────────────────────
    "groq_api_key": os.getenv("GROQ_API_KEY"),  # <- from .env
    "linkedin_email":    os.getenv("LINKEDIN_EMAIL"),     # <- from .env
    "linkedin_password": os.getenv("LINKEDIN_PASSWORD"),  # <- from .env
}