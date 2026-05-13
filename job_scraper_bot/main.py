import argparse
import os
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

    new_jobs = []
    for fetcher in fetchers:
        print(f"Fetching jobs from {fetcher.source_name()}")
        try:
            jobs = fetcher.fetch_jobs()
        except Exception as exc:
            print(f"Fetcher {fetcher.source_name()} failed: {exc}")
            jobs = []

        print(f"{fetcher.source_name()}: fetched {len(jobs)} jobs")
        scored_jobs = 0
        new_jobs_count = 0
        for job in jobs:
            if storage.is_job_seen(job):
                continue
            if matcher.is_broadcast_job(job):
                continue
            scored = matcher.score_job(job)
            if scored["score"] > 0:
                new_jobs.append(scored)
                scored_jobs += 1
            new_jobs_count += 1

        if scored_jobs == 0 and jobs:
            print(f"{fetcher.source_name()}: {len(jobs)} fetched jobs, but none scored > 0")
        elif jobs:
            print(f"{fetcher.source_name()}: {scored_jobs} new scored jobs")

    if new_jobs:
        storage.save_jobs(new_jobs)

    ranked_jobs = sorted(new_jobs, key=lambda item: item["score"], reverse=True)
    mail_jobs = [job for job in ranked_jobs if job["score"] >= MIN_EMAIL_SCORE]

    generator = DigestGenerator(mail_jobs)
    generator.write_html()
    generator.write_text()
    generator.write_email()

    if mail_jobs:
        if EmailSender.can_send():
            try:
                EmailSender.send_digest()
                print("Email digest sent successfully.")
            except Exception as exc:
                print(f"Email send failed: {exc}")
        else:
            print("Email not sent: SMTP credentials are not configured in environment variables.")
    else:
        print(f"No jobs scored >= {MIN_EMAIL_SCORE}; digest generated but email was not sent.")

    print(f"Completed fetch cycle. {len(ranked_jobs)} new ranked jobs written, {len(mail_jobs)} jobs sent to the mailer.")


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
