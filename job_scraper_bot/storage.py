import json
import os
from job_scraper_bot.config import (
    JOB_STORAGE_FILE,
    DEFAULT_RESUME_KEYWORDS,
    RESUME_FILE,
    RESUME_KEYWORDS_FILE,
)
from job_scraper_bot.utils import extract_resume_keywords


class JobStorage:
    def __init__(self):
        self.storage_file = JOB_STORAGE_FILE
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        self.jobs = self._load_existing_jobs()

    def _load_existing_jobs(self):
        if not os.path.exists(self.storage_file):
            return []
        with open(self.storage_file, "r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return []

    def load_resume_keywords(self):
        if os.path.exists(RESUME_KEYWORDS_FILE):
            try:
                with open(RESUME_KEYWORDS_FILE, "r", encoding="utf-8") as handle:
                    lines = [line.strip().lower() for line in handle if line.strip()]
                    if lines:
                        return list(dict.fromkeys(lines))
            except OSError:
                pass

        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, "r", encoding="utf-8") as handle:
                    resume_text = handle.read()
                extracted = extract_resume_keywords(resume_text)
                if extracted:
                    return extracted
            except OSError:
                pass

        return DEFAULT_RESUME_KEYWORDS

    def is_job_seen(self, job):
        return any(existing.get("id") == job.get("id") for existing in self.jobs)

    def save_jobs(self, jobs):
        self.jobs.extend(jobs)
        with open(self.storage_file, "w", encoding="utf-8") as handle:
            json.dump(self.jobs, handle, indent=2)
