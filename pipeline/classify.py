import json
import os
import time

from groq import Groq

from db.models import CATEGORIES

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"
MAX_ATTEMPTS = 3


def classify(listing) -> dict:
    """Ask the LLM whether this listing is relevant to a Nigerian CS/tech
    student audience, and extract structured tags: work type, category,
    Nigeria-relevance, skills, and a relevance score."""

    prompt = f"""Classify this job/internship/gig listing for a Nigerian computer science / tech student audience. Relevant roles include software development, design, video editing, social media management, digital marketing, and similar digital/tech work.

Title: {listing.title}
Company: {listing.company}
Location: {listing.location}
Description: {listing.description[:600]}

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "relevant": true or false,
  "work_type": "remote" or "onsite" or "hybrid",
  "category": one of {CATEGORIES},
  "nigeria_relevant": true if the listing is based in Nigeria, targets Nigerian/African candidates, or explicitly welcomes applicants from Nigeria/Africa, otherwise false,
  "skills": ["skill1", "skill2"],
  "relevance_score": integer between 0 and 100
}}"""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                max_tokens=150,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content.strip()
            data = json.loads(text)
            if data.get("category") not in CATEGORIES:
                data["category"] = "other"
            return data
        except Exception as e:
            if "429" in str(e) and attempt < MAX_ATTEMPTS:
                time.sleep(2 * attempt)  # brief backoff, then retry the rate-limited call
                continue
            print(f"Classification failed for '{listing.title}': {e}")
            return {
                "relevant": False,
                "work_type": "remote",
                "category": "other",
                "nigeria_relevant": False,
                "skills": [],
                "relevance_score": 0,
            }
