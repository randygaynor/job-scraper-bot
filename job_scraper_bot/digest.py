from datetime import datetime
from job_scraper_bot.config import DIGEST_HTML_FILE, DIGEST_TEXT_FILE, DIGEST_EMAIL_FILE


class DigestGenerator:
    def __init__(self, ranked_jobs, summary=None):
        self.ranked_jobs = ranked_jobs
        self.summary = summary or {}

    def _format_runtime(self):
        seconds = self.summary.get("runtime_seconds")
        if seconds is None:
            return "N/A"
        minutes, sec = divmod(seconds, 60)
        return f"{int(minutes)}m {int(sec)}s"

    def _summary_html(self):
        lines = [
            "<section style=\"margin-bottom:24px; font-family:Arial, sans-serif;\">",
            f"<h2>Summary</h2>",
            f"<p><strong>Start:</strong> {self.summary.get('start_time','N/A')}</p>",
            f"<p><strong>End:</strong> {self.summary.get('end_time','N/A')}</p>",
            f"<p><strong>Runtime:</strong> {self._format_runtime()}</p>",
            f"<p><strong>Sources with email jobs:</strong> {', '.join(self.summary.get('email_sources', [])) or 'None'}</p>",
            f"<p><strong>Fetched:</strong> {self.summary.get('total_fetched', 0)} | <strong>Considered:</strong> {self.summary.get('total_new_considered', 0)} | <strong>Matched:</strong> {self.summary.get('total_scored', 0)} | <strong>Mailed:</strong> {self.summary.get('total_email_jobs', 0)}</p>",
        ]

        if self.summary.get("errors"):
            lines.append("<p><strong>Errors:</strong></p>")
            lines.append("<ul>")
            for error in self.summary["errors"]:
                lines.append(f"<li>{error}</li>")
            lines.append("</ul>")

        lines.append("</section>")
        return lines

    def _summary_text(self):
        lines = [
            f"Job Digest - {datetime.now().strftime('%Y-%m-%d')}",
            "", 
            "Summary:",
            f"  Start: {self.summary.get('start_time', 'N/A')}",
            f"  End: {self.summary.get('end_time', 'N/A')}",
            f"  Runtime: {self._format_runtime()}",
            f"  Sources with email jobs: {', '.join(self.summary.get('email_sources', [])) or 'None'}",
            f"  Fetched: {self.summary.get('total_fetched', 0)} | Considered: {self.summary.get('total_new_considered', 0)} | Matched: {self.summary.get('total_scored', 0)} | Mailed: {self.summary.get('total_email_jobs', 0)}",
        ]

        if self.summary.get("errors"):
            lines.append("Errors:")
            for error in self.summary["errors"]:
                lines.append(f"  - {error}")

        lines.append("")
        return lines

    def write_html(self):
        html_parts = [
            "<html><head><meta charset=\"utf-8\"><title>Job Digest</title></head><body>",
            f"<h1>Job Digest - {datetime.now().strftime('%Y-%m-%d')}</h1>",
        ]
        html_parts.extend(self._summary_html())
        html_parts.append("<ul>")

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
        lines = self._summary_text()
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
        lines.extend(self._summary_text()[1:])
        for job in self.ranked_jobs:
            lines.append(f"{job['title']} | {job['company']} | {job['location']}")
            lines.append(f"URL: {job['url']}")
            lines.append(f"Score: {job['score']} | Matched: {', '.join(job['matched_keywords'].keys())}")
            lines.append("")

        with open(DIGEST_EMAIL_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
