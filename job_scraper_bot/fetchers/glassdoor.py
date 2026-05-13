import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class GlassdoorFetcher(JobFetcher):
    def source_name(self):
        return "Glassdoor"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:2]:
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={requests.utils.requote_uri(term)}&locT=C&locId=1&locKeyword=United+States"
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(5000)  # Wait for JS to load
                    html = page.content()
                except Exception as e:
                    print(f"Glassdoor fetch error for {term}: {e}")
                    browser.close()
                    continue
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select("div.jobCard"):
                title_elem = card.select_one("a.JobCard_jobTitle__GLyJ1")
                company_elem = card.select_one("span.EmployerProfile_compactEmployerName__9MGcV")
                location_elem = card.select_one("div.JobCard_location__Ds1fM")
                summary_elem = card.select_one("div.JobCard_jobDescriptionSnippet__QMp54")

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True) if company_elem else ""
                location = location_elem.get_text(strip=True) if location_elem else ""
                description = summary_elem.get_text(strip=True) if summary_elem else ""
                job_url = requests.compat.urljoin(url, title_elem.get("href"))

                job = {
                    "id": job_url,
                    "source": "Glassdoor",
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "url": job_url,
                }
                results.append(job)

        return results
