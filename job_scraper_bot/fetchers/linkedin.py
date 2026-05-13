import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class LinkedInFetcher(JobFetcher):
    def source_name(self):
        return "LinkedIn"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:2]:
            url = f"https://www.linkedin.com/jobs/search?keywords={requests.utils.requote_uri(term)}&location=United%20States"
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(5000)  # Wait for JS to load
                    html = page.content()
                except Exception as e:
                    print(f"LinkedIn fetch error for {term}: {e}")
                    browser.close()
                    continue
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select("div.base-card"):
                title_elem = card.select_one("h3")
                company_elem = card.select_one("h4")
                location_elem = card.select_one("span.job-search-card__location")
                link_elem = card.select_one("a")

                if not title_elem or not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True) if company_elem else ""
                location = location_elem.get_text(strip=True) if location_elem else ""
                job_url = link_elem.get("href")

                job = {
                    "id": job_url,
                    "source": "LinkedIn",
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": "",
                    "url": job_url,
                }
                results.append(job)

        return results
