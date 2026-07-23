from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from db.crud import get_active_listings, get_session  # noqa: E402

app = FastAPI(title="NACOS FCIT Opportunities API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.fcitaksu.com.ng",
        "https://fcitaksu.com.ng",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

SCOPE_LABELS = {
    "all": "All Jobs",
    "local": "Local (NG)",
    "global": "Global Remote",
}

CATEGORY_LABELS = {
    "all": "All",
    "frontend": "Frontend Development",
    "backend": "Backend Development",
    "fullstack": "Full-Stack Development",
    "mobile": "Mobile Development",
    "design": "Graphic/Web Design",
    "video_editing": "Video Editing",
    "social_media": "Social Media Management",
    "digital_marketing": "Digital Marketing",
    "data_ai": "Data Science / AI",
    "devops_cloud": "DevOps / Cloud",
    "cybersecurity": "Cybersecurity",
    "product_management": "Product / Project Management",
    "content_writing": "Content Writing",
    "qa_testing": "QA / Testing",
    "other": "Other",
}


@app.get("/api/opportunities")
def opportunities(
    scope: str = Query(default="all", description="all | local | global — see /api/meta"),
    category: str = Query(default="all"),
    q: str = Query(default=None, description="Free-text search across title, company, and skills"),
    db: Session = Depends(get_session),
):
    listings = get_active_listings(db, scope=scope, category=category, q=q)
    return [
        {
            "id": l.id,
            "title": l.title,
            "company": l.company,
            "location": l.location,
            "work_type": l.work_type,
            "category": l.category,
            "nigeria_relevant": l.nigeria_relevant,
            "apply_url": l.apply_url,
            "skills": l.skills.split(", ") if l.skills else [],
            "relevance_score": l.relevance_score,
            "source": l.source,
            "posted_at": l.posted_at,
        }
        for l in listings
    ]


@app.get("/api/meta")
def meta():
    """Filter options for the frontend — scope tabs and category buckets with display labels."""
    return {
        "scopes": [{"value": k, "label": v} for k, v in SCOPE_LABELS.items()],
        "categories": [{"value": k, "label": v} for k, v in CATEGORY_LABELS.items()],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
