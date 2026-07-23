import hashlib

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Listing, SeenListing

Base.metadata.create_all(bind=engine)


def make_hash(title: str, company: str, url: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_duplicate(db: Session, hash_key: str) -> bool:
    return db.query(Listing).filter(Listing.hash_key == hash_key).first() is not None


def is_seen(db: Session, hash_key: str) -> bool:
    """True if this listing has already been through classify() before,
    whether or not it turned out relevant."""
    return db.query(SeenListing).filter(SeenListing.hash_key == hash_key).first() is not None


def mark_seen(db: Session, hash_key: str):
    if is_seen(db, hash_key):
        return
    db.add(SeenListing(hash_key=hash_key))
    db.commit()


def save_listing(db: Session, raw_listing, classification: dict):
    hash_key = make_hash(raw_listing.title, raw_listing.company, raw_listing.url)
    if is_duplicate(db, hash_key):
        return None

    listing = Listing(
        hash_key=hash_key,
        title=raw_listing.title,
        company=raw_listing.company,
        location=raw_listing.location,
        work_type=classification.get("work_type", "remote"),
        category=classification.get("category", "other"),
        nigeria_relevant=bool(classification.get("nigeria_relevant", False)),
        apply_url=raw_listing.url,
        skills=", ".join(classification.get("skills", [])),
        relevance_score=classification.get("relevance_score", 0),
        source=raw_listing.source,
        posted_at=raw_listing.posted_at,
        approved=True,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def get_active_listings(db: Session, scope: str = "all", category: str = "all", q: str = None):
    query = db.query(Listing).filter(Listing.approved == True)  # noqa: E712

    if scope == "local":
        query = query.filter(Listing.nigeria_relevant == True)  # noqa: E712
    elif scope == "global":
        query = query.filter(Listing.nigeria_relevant == False)  # noqa: E712

    if category and category != "all":
        query = query.filter(Listing.category == category)

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Listing.title.ilike(pattern),
                Listing.company.ilike(pattern),
                Listing.skills.ilike(pattern),
            )
        )

    return query.order_by(
        Listing.nigeria_relevant.desc(),
        Listing.relevance_score.desc(),
        Listing.created_at.desc(),
    ).all()


def get_session():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
