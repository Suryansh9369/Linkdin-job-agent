# 🤖 AI Job Agent

![License](https://img.shields.io/badge/license-MIT-blue.svg)

An autonomous AI-powered job hunting system that scrapes LinkedIn jobs, filters opportunities using LLM-based relevance scoring, generates personalized outreach emails, and automates the application workflow.

Designed for students, freshers, and professionals looking to streamline job discovery and outreach using AI automation.

---

# 🚀 Features

## 🔎 LinkedIn Job Scraping
- Automated LinkedIn job crawling using Playwright
- Keyword-based search
- Location filtering
- Multi-page job extraction
- Duplicate job prevention

## 🧠 AI Job Relevance Filtering
- Uses Claude AI to evaluate job relevance
- Matches jobs against:
  - skills
  - experience
  - preferences
  - avoid conditions
- Intelligent scoring system

## ✉️ AI-Powered Personalized Emails
- Generates customized outreach emails
- Tailors messages based on:
  - job role
  - recruiter/company
  - user background
- Automatically attaches resume

## 📬 Automated Email Sending
- SMTP-based email delivery
- Gmail App Password integration
- Email tracking and logging

## ⏰ Scheduler Automation
- Daily automated execution
- Configurable run timing
- Weekday-only scheduling support

## 💾 Job Tracking Database
- SQLite database integration
- Prevents duplicate applications
- Stores processed job metadata

---

# 🏗️ System Architecture

```text
LinkedIn Jobs
      ↓
Playwright Scraper
      ↓
AI Relevance Filtering
      ↓
Email Generation
      ↓
SMTP Mail Sender
      ↓
SQLite Tracking Database
```

---

# 📁 Project Structure

```bash
job-agent/
│
├── ai/
│   ├── email_writer.py        # AI-generated email composer
│   └── job_filter.py          # AI-based job relevance scoring
│
├── attachments/
│   └── resume.pdf             # Your resume attachment
│
├── mailer/
│   └── email_sender.py        # SMTP email sender
│
├── scraper/
│   └── linkedin_scraper.py    # LinkedIn scraping logic
│
├── storage/
│   ├── db.py                  # SQLite database operations
│   └── jobs.db                # Generated database
│
├── .env                       # Environment variables
├── .gitignore
├── config.py                  # User configuration
├── main.py                    # Main orchestration pipeline
├── scheduler.py               # Scheduled automation
├── view_jobs.py               # Database job viewer
├── debug_page.html            # Debug/testing interface
├── requirements.txt
├── readme.md
└── agent.log                  # Execution logs
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-job-agent.git
cd ai-job-agent
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

---

# 🔐 Configuration

Edit `config.py`

## Fill Your Information

```python
your_name = "Your Name"
your_email = "your_email@gmail.com"
your_background = "AI/ML Student with robotics experience"
```

---

## Job Preferences

```python
job_keywords = [
    "AI Engineer",
    "Machine Learning Intern",
    "Python Developer"
]

location = "India"

preferences = {
    "must_have": [],
    "avoid": []
}
```

---

## LinkedIn Credentials

```python
linkedin_email = "your_email"
linkedin_password = "your_password"
```

---

## SMTP Configuration

```python
smtp_user = "your_email@gmail.com"
smtp_password = "gmail_app_password"
```

---

## Anthropic API Key

```python
anthropic_api_key = "your_api_key"
```

---

# 📎 Add Resume

Place your resume inside:

```bash
attachments/resume.pdf
```

---

# 🔑 Gmail App Password Setup

1. Open Google Account Security
2. Enable 2-Step Verification
3. Open:
   `Security → App Passwords`
4. Generate Mail App Password
5. Paste into:

```python
smtp_password
```

---

# 🧠 Anthropic API Setup

1. Create account on Anthropic Console
2. Generate API key
3. Add key in:

```python
anthropic_api_key
```

---

# ▶️ Running the Project

## Manual Run

```bash
python main.py
```

---

## Automated Scheduled Run

```bash
python scheduler.py
```

Default:
- Every weekday
- 9:00 AM execution

---

# 📊 Workflow

```text
1. Scrape LinkedIn Jobs
2. Extract Job Information
3. Filter Relevant Opportunities Using AI
4. Generate Personalized Emails
5. Send Emails with Resume
6. Store Results in Database
7. Log Execution Details
```

---

# 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Automation | Playwright |
| AI/LLM | Claude AI (Anthropic) |
| Database | SQLite |
| Email Service | SMTP |
| Scheduling | schedule / cron logic |
| Logging | Python logging |

---

# 📌 Future Improvements

- Web dashboard
- Resume optimization using AI
- Multi-platform scraping (Indeed, Naukri, Wellfound)
- AI cover letter generation
- Recruiter contact extraction
- Docker deployment
- FastAPI backend
- Streamlit frontend
- Vector database for job matching
- RAG-based personalized applications

---

# ⚠️ Important Notes

- LinkedIn discourages aggressive automated scraping.
- Keep request volume low.
- Recommended:
  - `max_emails_per_run = 5–10`
- Use responsibly and ethically.

---

# 🧾 Logs & Tracking

## Application Logs

```bash
agent.log
```

## Stored Jobs Database

```bash
storage/jobs.db
```

---

# 🤝 Contribution

Contributions, improvements, and feature suggestions are welcome.

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

Built by Suryansh  
AI/ML Student | Robotics Enthusiast | Agentic AI Builder