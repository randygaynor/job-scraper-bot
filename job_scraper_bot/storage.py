import json
import os
from datetime import datetime
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
        self.sent_ids = {job.get("id") for job in self.jobs if job.get("sent")}

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

    def _find_job_index(self, job_id):
        for index, existing in enumerate(self.jobs):
            if existing.get("id") == job_id:
                return index
        return None

    def _save_storage(self):
        with open(self.storage_file, "w", encoding="utf-8") as handle:
            json.dump(self.jobs, handle, indent=2)

    def is_job_seen(self, job):
        return any(existing.get("id") == job.get("id") for existing in self.jobs)

    def is_job_sent(self, job):
        return job.get("id") in self.sent_ids

    def save_jobs(self, jobs):
        for job in jobs:
            job_id = job.get("id")
            if not job_id:
                continue
            existing_index = self._find_job_index(job_id)
            record = {**job, "sent": False}
            if existing_index is not None:
                existing_sent = self.jobs[existing_index].get("sent", False)
                record["sent"] = existing_sent
                self.jobs[existing_index] = record
            else:
                self.jobs.append(record)
        self._save_storage()

    def mark_jobs_as_sent(self, job_ids):
        now = datetime.utcnow().isoformat() + "Z"
        for job_id in job_ids:
            index = self._find_job_index(job_id)
            if index is None:
                continue
            self.jobs[index]["sent"] = True
            self.jobs[index]["sent_at"] = now
            self.sent_ids.add(job_id)
        self._save_storage()
