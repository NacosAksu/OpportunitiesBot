import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

from db.database import SessionLocal  # noqa: E402
from db.crud import is_seen, make_hash, mark_seen, save_listing  # noqa: E402
from pipeline.classify import classify  # noqa: E402
from sources.arbeitnow import ArbeitnowSource  # noqa: E402
from sources.myjobmag import MyJobMagSource  # noqa: E402
from sources.remotive import RemotiveSource  # noqa: E402

# Add new sources here as you build them
SOURCES = [RemotiveSource(), ArbeitnowSource(), MyJobMagSource()]

# Sources that are structurally 100% Nigeria-based — don't leave this to the
# LLM's judgment (short/truncated listing text can miss it), force the flag.
NIGERIA_SOURCES = {"myjobmag"}

# Cheap keyword pre-filter: skip the LLM call entirely for listings that are
# obviously unrelated to tech/digital work (HR, sales, accounting, etc. show
# up a lot on Arbeitnow). This is what actually saves time — Groq's free tier
# throttles sustained request volume server-side (confirmed: classify() is
# fast in isolation but a 135-listing run stays slow with or without
# concurrency), so cutting how many listings reach the LLM matters far more
# than parallelizing the calls.
RELEVANT_KEYWORDS = [
    "software", "developer", "engineer", "engineering", "programmer", "programming",
    "frontend", "front-end", "backend", "back-end", "full stack", "fullstack",
    "web design", "web developer", " ui ", " ux ", "graphic design", "designer",
    "video edit", "content creator", "social media", "influencer",
    "digital marketing", "marketing", "seo",
    "data scientist", "data analyst", "machine learning", "artificial intelligence", " ai ",
    "devops", "cloud", "aws", "azure", "kubernetes", "docker",
    "cybersecurity", "cyber security", "penetration test",
    "product manager", "project manager", " qa ", "quality assurance", "tester",
    "mobile developer", "android", "ios developer", "flutter", "react native",
    "python", "javascript", "typescript", "react", "node.js", "django", "sql",
    "information technology", "app development", "app developer",
    "content writer", "copywriter", "technical writer",
]


def is_worth_classifying(listing) -> bool:
    text = f" {listing.title} {listing.description[:500]} ".lower()
    return any(keyword in text for keyword in RELEVANT_KEYWORDS)


async def fetch_all():
    all_listings = []
    for source in SOURCES:
        try:
            listings = await source.fetch()
            print(f"{source.name}: fetched {len(listings)} listings")
            all_listings.extend(listings)
        except Exception as e:
            print(f"{source.name} failed: {e}")
    return all_listings


def process(listings):
    db = SessionLocal()
    saved_count = 0
    already_seen_count = 0
    skipped_count = 0
    try:
        for listing in listings:
            hash_key = make_hash(listing.title, listing.company, listing.url)
            if is_seen(db, hash_key):
                already_seen_count += 1
                continue

            if not is_worth_classifying(listing):
                mark_seen(db, hash_key)
                skipped_count += 1
                continue

            classification = classify(listing)
            mark_seen(db, hash_key)
            if not classification.get("relevant"):
                continue
            if listing.source in NIGERIA_SOURCES:
                classification["nigeria_relevant"] = True
            saved = save_listing(db, listing, classification)
            if saved:
                saved_count += 1
                print(f"Saved: {listing.title} @ {listing.company}")
    finally:
        db.close()
    print(f"\nAlready seen in a previous run: {already_seen_count}")
    print(f"Skipped (obviously unrelated, no LLM call): {skipped_count}")
    print(f"Done. {saved_count} new listing(s) saved.")


async def main():
    listings = await fetch_all()
    process(listings)


if __name__ == "__main__":
    asyncio.run(main())
