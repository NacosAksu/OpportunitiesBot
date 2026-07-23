from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class RawListing:
    title: str
    company: str
    location: str
    url: str
    description: str
    posted_at: str
    source: str


class JobSource(ABC):
    """Every job source (API or scraper) implements this same contract,
    so the rest of the pipeline never needs to know where a listing came from."""

    name: str = "unknown"

    @abstractmethod
    async def fetch(self) -> List[RawListing]:
        ...
