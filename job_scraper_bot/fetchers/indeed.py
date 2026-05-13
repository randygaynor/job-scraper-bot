import requests
from bs4 import BeautifulSoup
import time
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class IndeedFetcher(JobFetcher):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def source_name(self):
        return "Indeed"

    def fetch_jobs(self):
        results = []
        for idx, term in enumerate(SEARCH_TERMS[:2]):
            if idx > 0:
                time.sleep(2)
            url = f"https://www.indeed.com/jobs?q={requests.utils.requote_uri(term)}&l=United+States"
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code != 200:
                    print(f"Indeed fetch failed for {term}: {response.status_code}")
                    continue
            except Exception as e:
                print(f"Indeed fetch error for {term}: {e}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("a.tapItem"):
                title = card.select_one("h2.jobTitle")
                company = card.select_one("span.companyName")
                location = card.select_one("div.companyLocation")
                summary = card.select_one("div.job-snippet")
                href = card.get("href")

                if not title or not href:
                    continue

                job = {
                    "id": href,
                    "source": "Indeed",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True) if company else "",
                    "location": location.get_text(strip=True) if location else "",
                    "description": summary.get_text(separator=" ", strip=True) if summary else "",
                    "url": requests.compat.urljoin("https://www.indeed.com", href),
                }
                results.append(job)

        return results
