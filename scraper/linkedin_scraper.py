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
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            page.set_default_timeout(60000)

            await self._login(page)

            for keyword in keywords:
                log.info(f"  Searching: '{keyword}' in '{location}'")
                try:
                    keyword_jobs = await self._scrape_jobs(page, keyword, location, max_results // len(keywords))
                    jobs.extend(keyword_jobs)
                except Exception as e:
                    log.warning(f"  Keyword '{keyword}' failed: {e}")
                await asyncio.sleep(random.uniform(2, 5))

            await browser.close()

        # Deduplicate
        seen = set()
        unique = []
        for j in jobs:
            if j["job_id"] not in seen:
                seen.add(j["job_id"])
                unique.append(j)

        return unique

    async def _login(self, page):
        await page.goto(f"{self.BASE_URL}/login")
        await page.wait_for_selector("#username", timeout=15000)
        await page.fill("#username", CONFIG["linkedin_email"])
        await page.fill("#password", CONFIG["linkedin_password"])
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        log.info("  Logged into LinkedIn")

    async def _scrape_jobs(self, page, keyword: str, location: str, limit: int) -> list:
        jobs = []

        search_url = (
            f"{self.BASE_URL}/jobs/search/?"
            f"keywords={keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_TPR=r86400"
            f"&sortBy=DD"
        )

        await page.goto(search_url)
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(4)

        # Confirmed working selector from debug output
        job_cards = await page.query_selector_all(".job-search-card")
        log.info(f"  Job cards found: {len(job_cards)}")

        if not job_cards:
            log.warning(f"  No cards found — URL: {page.url}")
            return []

        collected = 0
        for card in job_cards[:limit]:
            try:
                job = await self._extract_job(page, card)
                if job:
                    jobs.append(job)
                    collected += 1
                    log.info(f"  [{collected}] {job['title']} @ {job['company']}")
            except Exception as e:
                log.debug(f"  Card error: {e}")
            await asyncio.sleep(random.uniform(0.8, 1.5))

        log.info(f"  Total collected for '{keyword}': {len(jobs)}")
        return jobs

    async def _extract_job(self, page, card) -> dict | None:
        try:
            # Get job ID and URL directly from the card (no click needed)
            job_id = await card.get_attribute("data-entity-urn") or ""

            # Get basic info directly from card elements (no detail panel click)
            title = await self._try_selectors(card, [
                ".job-search-card__title",
                "h3.base-search-card__title",
                "h3",
            ])

            company = await self._try_selectors(card, [
                ".job-search-card__company-name",
                "h4.base-search-card__subtitle",
                "h4",
            ])

            location = await self._try_selectors(card, [
                ".job-search-card__location",
                "span.job-search-card__location",
            ])

            # Get job link
            link_el = await card.query_selector("a.base-card__full-link, a[class*='card']")
            job_url = await link_el.get_attribute("href") if link_el else page.url

            # Click to load description in detail panel
            await card.click()
            await asyncio.sleep(2)

            description = await self._try_selectors(page, [
                ".description__text",
                ".show-more-less-html__markup",
                "#job-details",
                ".jobs-description__content",
                "div[class*='description']",
            ])

            contact_email = self._extract_email(description)

            if not title or not company:
                return None

            return {
                "job_id": job_id or f"{title}-{company}",
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip() if location else "",
                "description": description[:3000] if description else "",
                "posted": "",
                "contact_email": contact_email,
                "url": job_url or page.url,
            }

        except Exception as e:
            log.debug(f"  Extraction error: {e}")
            return None

    async def _try_selectors(self, context, selectors: list) -> str:
        """Works on both page and element contexts."""
        for selector in selectors:
            try:
                el = await context.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text.strip():
                        return text.strip()
            except:
                continue
        return ""

    def _extract_email(self, text: str) -> str | None:
        import re
        if not text:
            return None
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None