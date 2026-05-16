import argparse
import os
from datetime import datetime
from job_scraper_bot.config import OUTPUT_DIRECTORY, MIN_EMAIL_SCORE
from job_scraper_bot.scheduler import schedule_nightly_run
from job_scraper_bot.storage import JobStorage
from job_scraper_bot.fetchers.usa_jobs import USAJobsFetcher
from job_scraper_bot.fetchers.indeed import IndeedFetcher
from job_scraper_bot.fetchers.linkedin import LinkedInFetcher
from job_scraper_bot.fetchers.glassdoor import GlassdoorFetcher
from job_scraper_bot.fetchers.state_boards import StateBoardFetcher
from job_scraper_bot.matcher import JobMatcher
from job_scraper_bot.digest import DigestGenerator
from job_scraper_bot.emailer import EmailSender


def ensure_output_directory():
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def run_once():
    ensure_output_directory()

    storage = JobStorage()
    resume_keywords = storage.load_resume_keywords()
    matcher = JobMatcher(resume_keywords)

    fetchers = [
        USAJobsFetcher(),
        IndeedFetcher(),
        LinkedInFetcher(),
        GlassdoorFetcher(),
        StateBoardFetcher(),
    ]

    start_time = datetime.utcnow()
    new_jobs = []
    current_seen_ids = set()
    fetch_stats = []

    for fetcher in fetchers:
        source_name = fetcher.source_name()
        print(f"Fetching jobs from {source_name}")
        source_stat = {
            "source": source_name,
            "fetched": 0,
            "scored": 0,
            "new_considered": 0,
            "errors": [],
        }

        try:
            jobs = fetcher.fetch_jobs()
        except Exception as exc:
            source_stat["errors"].append(str(exc))
            jobs = []

        source_stat["fetched"] = len(jobs)
        print(f"{source_name}: fetched {len(jobs)} jobs")

        for job in jobs:
            job_id = job.get("id")
            if not job_id or job_id in current_seen_ids:
                continue
            current_seen_ids.add(job_id)

            if storage.is_job_sent(job):
                continue
            if matcher.is_broadcast_job(job):
                continue

            scored = matcher.score_job(job)
            if scored["score"] > 0:
                new_jobs.append(scored)
                source_stat["scored"] += 1
            source_stat["new_considered"] += 1

        if source_stat["scored"] == 0 and jobs:
            print(f"{source_name}: {len(jobs)} fetched jobs, but none scored > 0")
        elif jobs:
            print(f"{source_name}: {source_stat['scored']} new scored jobs")

        fetch_stats.append(source_stat)

    if new_jobs:
        storage.save_jobs(new_jobs)

    ranked_jobs = sorted(new_jobs, key=lambda item: item["score"], reverse=True)
    mail_jobs = [job for job in ranked_jobs if job["score"] >= MIN_EMAIL_SCORE and not storage.is_job_sent(job)]

    end_time = datetime.utcnow()
    total_fetched = sum(stat["fetched"] for stat in fetch_stats)
    error_messages = [f"{stat['source']}: {err}" for stat in fetch_stats for err in stat["errors"]]
    summary = {
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "runtime_seconds": round((end_time - start_time).total_seconds(), 1),
        "total_sources": len(fetch_stats),
        "total_fetched": total_fetched,
        "total_new_considered": sum(stat["new_considered"] for stat in fetch_stats),
        "total_scored": len(ranked_jobs),
        "total_email_jobs": len(mail_jobs),
        "email_sources": sorted({job["source"] for job in mail_jobs}),
        "fetch_stats": fetch_stats,
        "errors": error_messages,
    }

    generator = DigestGenerator(mail_jobs, summary)
    generator.write_html()
    generator.write_text()
    generator.write_email()

    if mail_jobs:
        if EmailSender.can_send():
            try:
                EmailSender.send_digest()
                storage.mark_jobs_as_sent(mail_jobs)
                print("Email digest sent successfully.")
            except Exception as exc:
                print(f"Email send failed: {exc}")
        else:
            print("Email not sent: SMTP credentials are not configured in environment variables.")
    else:
        print(f"No jobs scored >= {MIN_EMAIL_SCORE}; digest generated but email was not sent.")

    print(
        f"Completed fetch cycle. {len(ranked_jobs)} new ranked jobs written, {len(mail_jobs)} jobs sent to the mailer."
    )


def main():
    parser = argparse.ArgumentParser(description="Job Scraper Bot for USA federal, state, and private job boards.")
    parser.add_argument("--run-once", action="store_true", help="Fetch jobs once and exit.")
    parser.add_argument("--schedule", action="store_true", help="Run the nightly scheduler loop.")
    args = parser.parse_args()

    if args.schedule:
        schedule_nightly_run(run_once)
    else:
        run_once()


if __name__ == "__main__":
    main()
