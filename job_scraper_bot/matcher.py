from collections import Counter
from job_scraper_bot.config import (
    DEFAULT_RESUME_KEYWORDS,
    PRIMARY_TARGET_TERMS,
    SECONDARY_TARGET_TERMS,
)
from job_scraper_bot.utils import normalize_text


class JobMatcher:
    def __init__(self, resume_keywords=None):
        self.resume_keywords = [kw.lower() for kw in (resume_keywords or DEFAULT_RESUME_KEYWORDS)]
        self.primary_keywords = [term.lower() for term in PRIMARY_TARGET_TERMS]
        self.secondary_keywords = [term.lower() for term in SECONDARY_TARGET_TERMS]

    def score_job(self, job):
        title = job.get("title", "")
        text = normalize_text(" ".join([title, job.get("company", ""), job.get("location", ""), job.get("description", "")]))
        score = 0
        matches = Counter()

        for keyword in self.resume_keywords:
            if keyword in text:
                weight = self._keyword_weight(keyword)
                score += weight
                matches[keyword] += 1

        score += self._title_bonus(title, text)
        score += self._source_score(job.get("source", ""))

        return {
            "id": job["id"],
            "source": job.get("source", ""),
            "title": title,
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "score": score,
            "matched_keywords": dict(matches),
        }

    def _keyword_weight(self, keyword):
        if keyword in self.primary_keywords:
            return 5
        if keyword in self.secondary_keywords:
            return 3
        return 2

    def _title_bonus(self, title, text):
        title_lower = title.lower()
        bonus = 0
        if any(term in title_lower for term in ["meteorologist", "atmospheric", "forecast", "hurricane", "tropical"]):
            bonus += 3
        if any(term in title_lower for term in ["analyst", "data scientist", "geospatial", "risk"]):
            bonus += 1
        if "remote" in text:
            bonus += 1
        if "noaa" in text or "nws" in text:
            bonus += 2
        return bonus

    def _source_score(self, source):
        if source and "USAJOBS" in source:
            return 2
        if source and "StateBoard" in source:
            return 1
        return 0
