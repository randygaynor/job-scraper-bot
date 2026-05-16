import json
import os
from datetime import datetime
from job_scraper_bot.config import (
    JOB_STORAGE_FILE,
    DEFAULT_RESUME_KEYWORDS,
    RESUME_FILE,
    RESUME_KEYWORDS_FILE,
)
from job_scraper_bot.utils import extract_resume_keywords, job_fingerprint, normalize_url


class JobStorage:
    def __init__(self):
        self.storage_file = JOB_STORAGE_FILE
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        self.jobs = self._load_existing_jobs()
        # Ensure every stored job has a stable fingerprint and build sent index
        self.sent_ids = set()
        for job in self.jobs:
            fp = job.get("fingerprint") or job_fingerprint(job)
            job["fingerprint"] = fp
            if job.get("sent"):
                self.sent_ids.add(fp)

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

    def _find_job_index(self, fingerprint):
        for index, existing in enumerate(self.jobs):
            if existing.get("fingerprint") == fingerprint:
                return index
        return None

    def _save_storage(self):
        with open(self.storage_file, "w", encoding="utf-8") as handle:
            json.dump(self.jobs, handle, indent=2)

    def is_job_seen(self, job):
        fp = job_fingerprint(job)
        return any(existing.get("fingerprint") == fp for existing in self.jobs)

    def is_job_sent(self, job):
        fp = job_fingerprint(job)
        return fp in self.sent_ids

    def save_jobs(self, jobs):
        for job in jobs:
            fp = job_fingerprint(job)
            if not fp:
                continue
            existing_index = self._find_job_index(fp)
            record = {**job, "sent": False, "fingerprint": fp}
            if existing_index is not None:
                existing_sent = self.jobs[existing_index].get("sent", False)
                record["sent"] = existing_sent
                self.jobs[existing_index] = record
            else:
                self.jobs.append(record)
        self._save_storage()

    def mark_jobs_as_sent(self, jobs_or_ids):
        """Accepts a list of job dicts or identifiers; mark matching stored jobs as sent."""
        now = datetime.utcnow().isoformat() + "Z"
        for item in jobs_or_ids:
            # determine fingerprint
            if isinstance(item, dict):
                fp = job_fingerprint(item)
            else:
                # item is likely a URL or id string
                fp = normalize_url(str(item))

            index = self._find_job_index(fp)
            if index is None:
                # nothing found, try matching by raw id field
                for idx, existing in enumerate(self.jobs):
                    if existing.get("id") == item or existing.get("id") == fp:
                        index = idx
                        break
            if index is None:
                continue
            self.jobs[index]["sent"] = True
            self.jobs[index]["sent_at"] = now
            self.sent_ids.add(self.jobs[index].get("fingerprint"))
        self._save_storage()
