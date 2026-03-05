"""
ai/job_filter.py
Uses Claude to evaluate each job against your preferences and score/filter them
"""

import json
import logging
import anthropic
from config import CONFIG

log = logging.getLogger(__name__)


class JobFilter:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CONFIG.get("anthropic_api_key"))

    async def filter_jobs(self, jobs: list, preferences: dict) -> list:
        """
        Run all jobs through Claude to get a relevance score.
        Returns only jobs that score >= 7/10.
        """
        matched = []

        for job in jobs:
            score, reason = await self._score_job(job, preferences)
            job["match_score"] = score
            job["match_reason"] = reason

            if score >= 7:
                log.info(f"  ✅ Match ({score}/10): {job['title']} @ {job['company']}")
                log.info(f"     Reason: {reason}")
                matched.append(job)
            else:
                log.debug(f"  ❌ Skip ({score}/10): {job['title']} @ {job['company']}")

        # Sort by score descending
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        return matched

    async def _score_job(self, job: dict, preferences: dict) -> tuple[int, str]:
        """Ask Claude to score a single job 1-10."""
        prompt = f"""
You are a job matching assistant. Score this job listing 1-10 based on how well it matches the candidate's preferences.

JOB LISTING:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description'][:1500]}

CANDIDATE PREFERENCES:
Must Have: {', '.join(preferences.get('must_have', []))}
Nice to Have: {', '.join(preferences.get('nice_to_have', []))}
Avoid: {', '.join(preferences.get('avoid', []))}
Min Salary: ${preferences.get('min_salary', 'not specified')}
Preferred Company Size: {', '.join(preferences.get('company_size', ['any']))}

Respond ONLY in this JSON format (no markdown):
{{
  "score": <1-10 integer>,
  "reason": "<one sentence explanation>"
}}
"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text.strip()
            data = json.loads(text)
            return data["score"], data["reason"]
        except Exception as e:
            log.warning(f"  Job scoring failed: {e}")
            return 0, "Scoring error"