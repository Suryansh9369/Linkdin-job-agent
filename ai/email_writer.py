"""
ai/email_writer.py
Uses Groq (free) to compose a personalized outreach email for each job
"""

import json
import logging
from groq import Groq
from config import CONFIG

log = logging.getLogger(__name__)


class EmailWriter:
    def __init__(self):
        self.client = Groq(api_key=CONFIG.get("groq_api_key"))

    async def compose(self, job: dict, your_name: str, your_background: str) -> dict:
        prompt = f"""
You are a professional career coach helping write job application emails.

Write a concise, personalized outreach email for this job. The email should:
- Be professional but warm and genuine
- Mention 2-3 specific things from the job description that match the candidate
- Be under 200 words in the body
- NOT sound like a template or AI output
- NOT use generic phrases like "I am writing to express my interest"
- End with a clear call to action (reply, schedule a call)

CANDIDATE:
Name: {your_name}
Background: {your_background.strip()}

JOB:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description'][:1500]}
Why it's a good match: {job.get('match_reason', '')}

Respond ONLY in this JSON format (no markdown, no extra text):
{{"subject": "<email subject line>", "body": "<full email body, use \\n for line breaks>"}}
"""
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            log.info(f"  Email composed: '{data['subject']}'")
            return data
        except Exception as e:
            log.error(f"  Email composition failed: {e}")
            return {
                "subject": f"Application for {job['title']} at {job['company']}",
                "body": (
                    f"Hi,\n\nI came across the {job['title']} role at {job['company']} "
                    f"and I'm very interested. I've attached my resume for your consideration.\n\n"
                    f"Best,\n{your_name}"
                )
            }