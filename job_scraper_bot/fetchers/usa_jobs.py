import requests
from bs4 import BeautifulSoup
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class USAJobsFetcher(JobFetcher):
    def source_name(self):
        return "USAJOBS"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:3]:
            url = f"https://www.usajobs.gov/Search/Results?keyword={requests.utils.requote_uri(term)}"
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            if response.status_code != 200:
                print(f"USAJobs fetch failed for {term}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("article.usajobs-search-result"):
                title_link = card.select_one("a.usc-job-link")
                if not title_link:
                    continue

                title = title_link.get_text(strip=True)
                job_url = requests.compat.urljoin("https://www.usajobs.gov", title_link["href"])
                organization = card.select_one("span.usajobs-organization")
                location = card.select_one("span.usajobs-location")
                summary = card.select_one("div.usajobs-search-result__snippet")
                job = {
                    "id": job_url,
                    "source": "USAJOBS",
                    "title": title,
                    "company": organization.get_text(strip=True) if organization else "USAJOBS",
                    "location": location.get_text(strip=True) if location else "",
                    "description": summary.get_text(strip=True) if summary else "",
                    "url": job_url,
                }
                results.append(job)

        return results
