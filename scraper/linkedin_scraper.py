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
                    keyword_jobs = await self._scrape_jobs(page, keyword, location, max_results)
                    jobs.extend(keyword_jobs)
                except Exception as e:
                    log.warning(f"  Keyword '{keyword}' failed: {e}")
                await asyncio.sleep(random.uniform(2, 5))

            # await context.close()

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
            f"&sortBy=DD"
        )

        print("SEARCH URL:", search_url)

        await page.goto(
            search_url,
            wait_until="domcontentloaded"
        )

        # wait for linkedin lazy loading
        await page.wait_for_timeout(10000)

        # debug screenshot
        await page.screenshot(
            path=f"debug_{keyword.replace(' ', '_')}.png"
        )

        # scroll to trigger lazy loading
        await page.mouse.wheel(0, 3000)

        await page.wait_for_timeout(5000)

        # UPDATED SELECTORS
        selectors = [
            "li.jobs-search-results__list-item",
            "div.job-search-card",
            "li.scaffold-layout__list-item"
        ]

        job_cards = []

        for selector in selectors:

            cards = await page.query_selector_all(selector)

            if cards:
                print(f"WORKING SELECTOR: {selector}")
                job_cards = cards
                break

        print("TOTAL JOB CARDS:", len(job_cards))

        log.info(f"  Job cards found: {len(job_cards)}")

        if not job_cards:

            html = await page.content()

            with open("debug_jobs_page.html", "w", encoding="utf-8") as f:
                f.write(html)

            log.warning(f"  No cards found — URL: {page.url}")

            return []

        collected = 0

        for card in job_cards[:limit]:

            try:

                job = await self._extract_job(page, card)
                
                print("EXTRACTED JOB:", job)

                if job:

                    jobs.append(job)

                    collected += 1

                    log.info(
                        f"  [{collected}] "
                        f"{job['title']} @ {job['company']}"
                    )

            except Exception as e:

                log.debug(f"  Card error: {e}")

            await asyncio.sleep(random.uniform(1, 2))

        log.info(
            f"  Total collected for '{keyword}': {len(jobs)}"
        )

        return jobs

    async def _extract_job(self, page, card) -> dict | None:

        try:

            # JOB TITLE
            title_el = await card.query_selector(
                "a.job-card-container__link, "
                "a[href*='/jobs/view/'], "
                "strong"
            )

            title = ""

            if title_el:
                title = (await title_el.inner_text()).strip()

            # COMPANY
            company_el = await card.query_selector(
                ".artdeco-entity-lockup__subtitle, "
                ".job-card-container__company-name, "
                "div.artdeco-entity-lockup__subtitle"
            )

            company = ""

            if company_el:
                company = (await company_el.inner_text()).strip()

            # LOCATION
            location_el = await card.query_selector(
                ".job-card-container__metadata-item, "
                ".artdeco-entity-lockup__caption"
            )

            location = ""

            if location_el:
                location = (await location_el.inner_text()).strip()

            # JOB URL
            link_el = await card.query_selector(
                "a[href*='/jobs/view/']"
            )

            job_url = ""

            if link_el:
                job_url = await link_el.get_attribute("href")

            # CLICK CARD
            try:
                await card.click()
                await asyncio.sleep(3)
            except:
                pass

            # DESCRIPTION
            description = ""

            desc_selectors = [
                ".jobs-description-content__text",
                ".jobs-box__html-content",
                ".jobs-description",
                ".job-view-layout",
                "div#job-details"
            ]

            for selector in desc_selectors:

                try:

                    desc_el = await page.query_selector(selector)

                    if desc_el:

                        text = await desc_el.inner_text()

                        if text.strip():

                            description = text.strip()

                            break

                except:
                    continue

            if not title:

                return None

            return {
                "job_id": job_url or title,
                "title": title,
                "company": company,
                "location": location,
                "description": description[:3000],
                "posted": "",
                "contact_email": self._extract_email(description),
                "url": job_url or page.url,
            }

        except Exception as e:

            print("EXTRACTION ERROR:", e)

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