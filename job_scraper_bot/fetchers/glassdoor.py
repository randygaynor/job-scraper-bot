import requests
from bs4 import BeautifulSoup
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class GlassdoorFetcher(JobFetcher):
    def source_name(self):
        return "Glassdoor"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:2]:
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={requests.utils.requote_uri(term)}&locT=C&locId=1&locKeyword=United+States"
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            if response.status_code != 200:
                print(f"Glassdoor fetch failed for {term}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("li.jl"):
                title = card.select_one("a.jobLink")
                company = card.select_one("div.jobHeader a")
                location = card.select_one("span.subtle.loc")
                summary = card.select_one("div.jobInfoItem")
                href = title.get("href") if title else None

                if not title or not href:
                    continue

                job = {
                    "id": href,
                    "source": "Glassdoor",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True) if company else "",
                    "location": location.get_text(strip=True) if location else "",
                    "description": summary.get_text(strip=True) if summary else "",
                    "url": requests.compat.urljoin("https://www.glassdoor.com", href),
                }
                results.append(job)

        return results
