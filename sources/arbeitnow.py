import httpx

from .base import JobSource, RawListing


class ArbeitnowSource(JobSource):
    name = "arbeitnow"

    async def fetch(self):
        url = "https://www.arbeitnow.com/api/job-board-api"

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json().get("data", [])

        listings = []
        for j in data:
            listings.append(
                RawListing(
                    title=j.get("title", ""),
                    company=j.get("company_name", ""),
                    location=j.get("location") or "Remote",
                    url=j.get("url", ""),
                    description=j.get("description", ""),
                    posted_at=str(j.get("created_at", "")),
                    source=self.name,
                )
            )
        return listings
