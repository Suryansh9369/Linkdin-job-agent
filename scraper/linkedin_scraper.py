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

    async def search_jobs(self, email, password, keywords, location, max_results=50) -> list:
        jobs = []
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir="linkedin_session",
                headless=False,
                slow_mo=500,
                args=[
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto("https://www.linkedin.com/feed/")
            
            await asyncio.sleep(15)
            
            print(page.url)
            await page.screenshot(path="jobs_page.png")
            
            # IF NOT LOGGED IN
            # if "login" in page.url:
            #     raise Exception(
            #         "LinkedIn session expired. Please login again."
            #     )
                
            # await page.goto("https://www.linkedin.com/login")
            
            page.set_default_timeout(60000)

            # await self._login(page, email, password)

            for keyword in keywords:
                log.info(f"  Searching: '{keyword}' in '{location}'")
                try:
                    keyword_jobs = await self._scrape_jobs(page, keyword, location, max_results // len(keywords))
                    jobs.extend(keyword_jobs)
                except Exception as e:
                    log.warning(f"  Keyword '{keyword}' failed: {e}")
                await asyncio.sleep(random.uniform(2, 5))

            await context.close()

        # Deduplicate
        seen = set()
        unique = []
        for j in jobs:
            if j["job_id"] not in seen:
                seen.add(j["job_id"])
                unique.append(j)

        return unique

    async def _login(self, page, email, password):

        await page.goto(
            "https://www.linkedin.com/login",
            wait_until="domcontentloaded"
        )

        await asyncio.sleep(10)

        print("CURRENT URL:", page.url)

        content = await page.content()

        with open("debug_linkedin.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("Saved page HTML")

        await page.screenshot(path="linkedin_debug.png")

        print("Screenshot saved")

        await page.wait_for_selector(
            'input[name="session_key"]',
            timeout=60000
        )

        await page.fill(
            'input[name="session_key"]',
            email
        )

        await page.fill(
            'input[name="session_password"]',
            password
        )

        await page.click('button[type="submit"]')

        await asyncio.sleep(10)

        print("After login:", page.url)

    async def _scrape_jobs(self, page, keyword: str, location: str, limit: int) -> list:
        jobs = []

        search_url = (
            f"{self.BASE_URL}/jobs/search/"
            f"?keywords={keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_WT=2"
            f"&sortBy=DD"
        )

        await page.goto(search_url)
        await page.wait_for_load_state("domcontentloaded") Exception
        await page.wait_for_timeout(8000)

        # Confirmed working selector from debug output
        job_cards = await page.query_selector_all(
            "div.job-search-card, li.scaffold-layout__list-item"
        )
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