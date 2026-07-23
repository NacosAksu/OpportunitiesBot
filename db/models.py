from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base

# Fixed category taxonomy — classify.py assigns one of these per listing,
# api/main.py exposes them (with display labels) via /api/meta for filter UI.
CATEGORIES = [
    "frontend",
    "backend",
    "fullstack",
    "mobile",
    "design",
    "video_editing",
    "social_media",
    "digital_marketing",
    "data_ai",
    "devops_cloud",
    "cybersecurity",
    "product_management",
    "content_writing",
    "qa_testing",
    "other",
]

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    hash_key = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(300), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    work_type = Column(String(20))  # remote | onsite | hybrid
    category = Column(String(30))  # see CATEGORIES above
    nigeria_relevant = Column(Boolean, default=False)
    apply_url = Column(Text, nullable=False)
    skills = Column(Text)  # comma-separated tags
    relevance_score = Column(Integer, default=0)
    source = Column(String(50))
    posted_at = Column(String(50))
    approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SeenListing(Base):
    """Every listing the LLM has ever been asked to classify, whether or not
    it turned out relevant. Lets run_scraper.py skip re-classifying the same
    duplicate postings on every run — only Listing rows (the relevant ones)
    used to be remembered, so irrelevant duplicates burned an LLM call again
    and again on every single scrape."""

    __tablename__ = "seen_listings"

    id = Column(Integer, primary_key=True, index=True)
    hash_key = Column(String(64), unique=True, index=True, nullable=False)
    seen_at = Column(DateTime(timezone=True), server_default=func.now())
