import httpx

from .base import JobSource, RawListing


class RemotiveSource(JobSource):
    name = "remotive"

    async def fetch(self):
        url = "https://remotive.com/api/remote-jobs"
        params = {"category": "software-dev"}

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json().get("jobs", [])

        listings = []
        for j in data:
            listings.append(
                RawListing(
                    title=j.get("title", ""),
                    company=j.get("company_name", ""),
                    location=j.get("candidate_required_location", "Remote"),
                    url=j.get("url", ""),
                    description=j.get("description", ""),
                    posted_at=j.get("publication_date", ""),
                    source=self.name,
                )
            )
        return listings
