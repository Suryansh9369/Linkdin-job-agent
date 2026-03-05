# 🤖 LinkedIn Job Hunter Agent

An AI agent that crawls LinkedIn for jobs, filters them using Claude AI,
and sends personalized outreach emails with your resume attached.

---

## ⚙️ Setup (5 minutes)

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Add your resume
```
attachments/resume.pdf   ← Put your resume here
```

### 3. Edit `config.py`
Fill in:
- `your_name`, `your_email`, `your_background`
- `job_keywords` and `location`
- `preferences` (must_have, avoid, etc.)
- `smtp_user` + `smtp_password` (use Gmail App Password)
- `linkedin_email` + `linkedin_password`
- `anthropic_api_key`

### 4. Get a Gmail App Password
1. Go to myaccount.google.com → Security → 2-Step Verification → App Passwords
2. Create one for "Mail"
3. Paste it into `config.py` as `smtp_password`

### 5. Get Anthropic API key
1. Go to console.anthropic.com
2. Create an API key
3. Paste into `config.py` as `anthropic_api_key`

---

## 🚀 Run

### One-time run
```bash
python main.py
```

### Scheduled (every weekday at 9am)
```bash
python scheduler.py
```

---

## 📁 Project Structure

```
job-agent/
├── main.py              # Orchestrator
├── config.py            # ← EDIT THIS
├── scheduler.py         # Auto-run daily (every weekday 9am)
├── requirements.txt
├── scraper/
│   └── linkedin_scraper.py   # Playwright scraper
├── ai/
│   ├── job_filter.py         # Claude job scoring
│   └── email_writer.py       # Claude email composer
├── mailer/
│   └── email_sender.py       # SMTP sender
├── storage/
│   ├── db.py                 # SQLite tracker
│   └── jobs.db               # Created on first run
└── attachments/
    └── resume.pdf            # ← PUT YOUR RESUME HERE
```

---

## ⚠️ Notes

- LinkedIn's ToS prohibits automated scraping — use responsibly, keep volumes low
- Set `max_emails_per_run` to 5–10 to avoid spam flags
- The agent tracks applied jobs in `storage/jobs.db` to never double-apply
- All sent emails are logged to `agent.log`