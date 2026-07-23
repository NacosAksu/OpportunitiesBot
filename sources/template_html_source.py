"""
Template for a source that has no public API and needs HTML scraping instead.
Copy this file, rename the class, fill in the selectors for the site you're
targeting, and add an instance to SOURCES in run_scraper.py.

Before scraping any site:
- Check its /robots.txt for disallowed paths
- Add a short delay between requests (see asyncio.sleep below)
- Only scrape public listing pages, never pages behind a login
"""

import asyncio

import httpx
from bs4 import BeautifulSoup

from .base import JobSource, RawListing


class TemplateHtmlSource(JobSource):
    name = "template"
    listing_page_url = "https://example.com/jobs"

    async def fetch(self):
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "NACOS-FCIT-Bot/1.0"}) as client:
            resp = await client.get(self.listing_page_url)
            resp.raise_for_status()
            await asyncio.sleep(1)  # be polite between requests

        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        # Replace these selectors with the actual ones for the target site
        for card in soup.select(".job-card"):
            title = card.select_one(".job-title")
            company = card.select_one(".job-company")
            link = card.select_one("a")

            if not (title and company and link):
                continue

            listings.append(
                RawListing(
                    title=title.get_text(strip=True),
                    company=company.get_text(strip=True),
                    location=card.select_one(".job-location").get_text(strip=True)
                    if card.select_one(".job-location")
                    else "Nigeria",
                    url=link.get("href", ""),
                    description=card.get_text(" ", strip=True),
                    posted_at="",
                    source=self.name,
                )
            )
        return listings
