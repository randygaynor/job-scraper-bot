from datetime import datetime
from job_scraper_bot.config import DIGEST_HTML_FILE, DIGEST_TEXT_FILE, DIGEST_EMAIL_FILE


class DigestGenerator:
    def __init__(self, ranked_jobs):
        self.ranked_jobs = ranked_jobs

    def write_html(self):
        html_parts = [
            "<html><head><meta charset=\"utf-8\"><title>Job Digest</title></head><body>",
            f"<h1>Job Digest - {datetime.now().strftime('%Y-%m-%d')}</h1>",
            "<ul>",
        ]

        for job in self.ranked_jobs:
            html_parts.append(
                f"<li><strong>{job['title']}</strong> - {job['company']} ({job['location']})<br />"
                f"Score: {job['score']} - <a href=\"{job['url']}\">Apply / View</a><br />"
                f"Matched: {', '.join(job['matched_keywords'].keys())}</li>"
            )

        html_parts.append("</ul></body></html>")
        with open(DIGEST_HTML_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(html_parts))

    def write_text(self):
        lines = [f"Job Digest - {datetime.now().strftime('%Y-%m-%d')}", ""]
        for job in self.ranked_jobs:
            lines.append(f"{job['title']} | {job['company']} | {job['location']}")
            lines.append(f"Score: {job['score']} | URL: {job['url']}")
            lines.append(f"Matched: {', '.join(job['matched_keywords'].keys())}")
            lines.append("")

        with open(DIGEST_TEXT_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

    def write_email(self):
        lines = [
            "Subject: Job Digest - " + datetime.now().strftime("%Y-%m-%d"),
            "",
            "Good morning, here are the new matched jobs from last night:",
            "",
        ]
        for job in self.ranked_jobs:
            lines.append(f"{job['title']} | {job['company']} | {job['location']}")
            lines.append(f"URL: {job['url']}")
            lines.append(f"Score: {job['score']} | Matched: {', '.join(job['matched_keywords'].keys())}")
            lines.append("")

        with open(DIGEST_EMAIL_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
