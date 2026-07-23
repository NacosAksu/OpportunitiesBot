import asyncio

import httpx
from bs4 import BeautifulSoup

from .base import JobSource, RawListing

BASE_URL = "https://www.myjobmag.com"


class MyJobMagSource(JobSource):
    """MyJobMag Nigeria job listings. robots.txt disallows any URL with a
    '?' query string, so pagination uses the plain /jobs/page/N path."""

    name = "myjobmag"
    pages_to_fetch = 2  # keep volume modest — see CLASSIFY_CONCURRENCY note in run_scraper.py

    async def fetch(self):
        listings = []
        async with httpx.AsyncClient(
            timeout=20, headers={"User-Agent": "NACOS-FCIT-Bot/1.0"}
        ) as client:
            for page in range(1, self.pages_to_fetch + 1):
                url = f"{BASE_URL}/jobs" if page == 1 else f"{BASE_URL}/jobs/page/{page}"
                resp = await client.get(url)
                resp.raise_for_status()
                listings.extend(self._parse(resp.text))
                if page < self.pages_to_fetch:
                    await asyncio.sleep(1)  # be polite between requests
        return listings

    def _parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        for card in soup.select("li.job-list-li"):
            title_link = card.select_one("li.job-info h2 a")
            logo_link = card.select_one("li.job-logo a img")
            desc_tag = card.select_one("li.job-desc")
            if not title_link:
                continue  # ad slots and other non-job cards have no title link

            href = title_link.get("href", "")
            company = logo_link.get("alt", "").strip() if logo_link else "Unknown"

            listings.append(
                RawListing(
                    title=title_link.get_text(strip=True),
                    company=company,
                    location="Nigeria",
                    url=href if href.startswith("http") else f"{BASE_URL}{href}",
                    description=desc_tag.get_text(strip=True) if desc_tag else "",
                    posted_at="",
                    source=self.name,
                )
            )
        return listings
