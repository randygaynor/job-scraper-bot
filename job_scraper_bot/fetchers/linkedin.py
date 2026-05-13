import requests
from bs4 import BeautifulSoup
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class LinkedInFetcher(JobFetcher):
    def source_name(self):
        return "LinkedIn"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:2]:
            url = f"https://www.linkedin.com/jobs/search?keywords={requests.utils.requote_uri(term)}&location=United%20States"
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            if response.status_code != 200:
                print(f"LinkedIn fetch failed for {term}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("li.result-card"):  # LinkedIn structure may change frequently
                title = card.select_one("h3.result-card__title")
                company = card.select_one("h4.result-card__subtitle")
                location = card.select_one("span.job-result-card__location")
                link = card.select_one("a.result-card__full-card-link")

                if not title or not link:
                    continue

                job = {
                    "id": link.get("href"),
                    "source": "LinkedIn",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True) if company else "",
                    "location": location.get_text(strip=True) if location else "",
                    "description": "",
                    "url": link.get("href"),
                }
                results.append(job)

        return results
