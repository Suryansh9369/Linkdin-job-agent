"""
scraper/linkedin_scraper.py
Crawls LinkedIn job listings using Playwright (headless browser)
"""

import asyncio
import random
import logging
from playwright.async_api import async_playwright
from config import CONFIG

log = logging.getLogger(__name__)


class LinkedInScraper:
    BASE_URL = "https://www.linkedin.com"

    async def search_jobs(self, keywords: list, location: str, max_results: int = 50) -> list:
        """Main entry: logs in and scrapes job listings."""
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            # Login
            await self._login(page)

            # Search for each keyword
            for keyword in keywords:
                log.info(f"  Searching: '{keyword}' in '{location}'")
                keyword_jobs = await self._scrape_jobs(page, keyword, location, max_results // len(keywords))
                jobs.extend(keyword_jobs)
                await asyncio.sleep(random.uniform(2, 5))  # polite delay

            await browser.close()

        # Deduplicate by job_id
        seen = set()
        unique = []
        for j in jobs:
            if j["job_id"] not in seen:
                seen.add(j["job_id"])
                unique.append(j)

        return unique

    async def _login(self, page):
        """Log into LinkedIn."""
        await page.goto(f"{self.BASE_URL}/login")
        await page.fill("#username", CONFIG["linkedin_email"])
        await page.fill("#password", CONFIG["linkedin_password"])
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        log.info("  ✅ Logged into LinkedIn")

    async def _scrape_jobs(self, page, keyword: str, location: str, limit: int) -> list:
        """Search and scrape job listings."""
        jobs = []
        search_url = (
            f"{self.BASE_URL}/jobs/search/?"
            f"keywords={keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_TPR=r86400"  # Last 24 hours
            f"&sortBy=DD"     # Sort by date
        )

        await page.goto(search_url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        collected = 0
        scroll_attempts = 0

        while collected < limit and scroll_attempts < 20:
            # Get all job cards on current page
            job_cards = await page.query_selector_all(".job-card-container")

            for card in job_cards[collected:]:
                if collected >= limit:
                    break
                try:
                    job = await self._extract_job_card(page, card)
                    if job:
                        jobs.append(job)
                        collected += 1
                except Exception as e:
                    log.debug(f"    Card extraction error: {e}")

            # Scroll to load more
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(random.uniform(1.5, 3))
            scroll_attempts += 1

        return jobs

    async def _extract_job_card(self, page, card) -> dict | None:
        """Extract data from a single job card."""
        try:
            # Click to open job details
            await card.click()
            await asyncio.sleep(1.5)

            # Extract from detail panel
            job_id = await card.get_attribute("data-job-id") or ""
            title = await self._safe_text(page, ".job-details-jobs-unified-top-card__job-title")
            company = await self._safe_text(page, ".job-details-jobs-unified-top-card__company-name")
            location = await self._safe_text(page, ".job-details-jobs-unified-top-card__bullet")
            description = await self._safe_text(page, ".jobs-description__content")
            posted = await self._safe_text(page, ".job-details-jobs-unified-top-card__posted-date")

            # Try to find contact email in description
            contact_email = self._extract_email(description)

            # Job URL
            job_url = page.url

            if not title or not company:
                return None

            return {
                "job_id": job_id,
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "description": description[:3000] if description else "",
                "posted": posted.strip() if posted else "",
                "contact_email": contact_email,
                "url": job_url,
            }

        except Exception as e:
            log.debug(f"    Error extracting job: {e}")
            return None

    async def _safe_text(self, page, selector: str) -> str:
        """Safe text extraction that won't throw."""
        try:
            el = await page.query_selector(selector)
            return await el.inner_text() if el else ""
        except:
            return ""

    def _extract_email(self, text: str) -> str | None:
        """Find email addresses in job description text."""
        import re
        if not text:
            return None
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None