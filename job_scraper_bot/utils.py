import re
from itertools import chain
from job_scraper_bot.config import DEFAULT_RESUME_KEYWORDS, PRIMARY_TARGET_TERMS, SECONDARY_TARGET_TERMS


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def extract_resume_keywords(text):
    normalized = normalize_text(text)
    keywords = set()

    for phrase in chain(PRIMARY_TARGET_TERMS, SECONDARY_TARGET_TERMS, DEFAULT_RESUME_KEYWORDS):
        phrase_lower = phrase.lower()
        if phrase_lower in normalized:
            keywords.add(phrase_lower)

    tokens = set(re.findall(r"\b[a-z]{3,}\b", normalized))
    support_tokens = {
        "python",
        "wrf",
        "hpc",
        "gis",
        "noaa",
        "nws",
        "forecast",
        "assimilation",
        "spatial",
        "visualization",
        "climate",
        "risk",
        "insurance",
        "emergency",
        "management",
        "data",
        "analysis",
        "modeling",
        "operational",
    }

    keywords.update(tokens & support_tokens)
    return sorted(keywords)


def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    # remove query params and fragments
    parts = url.split("?")[0].split('#')[0]
    # remove trailing slash
    if parts.endswith("/"):
        parts = parts[:-1]
    return parts.lower()


def job_fingerprint(job: dict) -> str:
    """Create a stable fingerprint for a job using URL when available,
    otherwise fall back to title|company|location normalized."""
    url = job.get("url") or job.get("id")
    norm = normalize_url(url) if url else ""
    if norm:
        return norm
    title = (job.get("title") or "").strip().lower()
    company = (job.get("company") or "").strip().lower()
    location = (job.get("location") or "").strip().lower()
    return "|".join([title, company, location])
