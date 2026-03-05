"""
ai/email_writer.py
Uses Claude to compose a personalized outreach email for each job
"""

import json
import logging
import anthropic
from config import CONFIG

log = logging.getLogger(__name__)


class EmailWriter:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CONFIG.get("anthropic_api_key"))

    async def compose(self, job: dict, your_name: str, your_background: str) -> dict:
        """
        Returns a dict with 'subject' and 'body' for the email.
        """
        prompt = f"""
You are a professional career coach helping write job application emails.

Write a concise, personalized outreach email for this job. The email should:
- Be professional but warm and genuine
- Mention 2-3 specific things from the job description that match the candidate
- Be under 200 words in the body
- NOT sound like a template or ChatGPT output
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
Match Score: {job.get('match_score', 'N/A')}/10
Why it's a good match: {job.get('match_reason', '')}

Respond ONLY in this JSON format (no markdown):
{{
  "subject": "<email subject line>",
  "body": "<full email body, use \\n for line breaks>"
}}
"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text.strip()
            data = json.loads(text)
            log.info(f"  ✍️  Email composed: '{data['subject']}'")
            return data
        except Exception as e:
            log.error(f"  Email composition failed: {e}")
            # Fallback template
            return {
                "subject": f"Application for {job['title']} at {job['company']}",
                "body": (
                    f"Hi,\n\nI came across the {job['title']} role at {job['company']} "
                    f"and I'm very interested. I've attached my resume for your consideration.\n\n"
                    f"Best,\n{your_name}"
                )
            }