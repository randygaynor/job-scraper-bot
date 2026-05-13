import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from job_scraper_bot.config import SEARCH_TERMS, USER_AGENT
from job_scraper_bot.fetchers import JobFetcher


class USAJobsFetcher(JobFetcher):
    def source_name(self):
        return "USAJOBS"

    def fetch_jobs(self):
        results = []
        for term in SEARCH_TERMS[:3]:
            url = f"https://www.usajobs.gov/Search/Results?keyword={requests.utils.requote_uri(term)}"
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(5000)  # Wait for JS to load
                    html = page.content()
                except Exception as e:
                    print(f"USAJobs fetch error for {term}: {e}")
                    browser.close()
                    continue
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            for link in soup.select('a[href^="/job/"]'):
                href = link.get("href")
                text = link.get_text(strip=True)
                if not href or not text:
                    continue

                job_url = requests.compat.urljoin(url, href)
                h2 = link.find_parent('h2')
                if not h2:
                    continue
                card = h2.find_parent('div', class_=['border', 'border-gray-lighter', 'bg-white', 'p-4'])
                if not card:
                    continue

                # Extract details from card
                title = text
                company = "USAJOBS"  # Default
                location = ""
                description = ""

                # Look for location in card
                loc_elem = card.select_one('span.location, div.location')
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                # Look for organization
                org_elem = card.select_one('span.organization, div.organization')
                if org_elem:
                    company = org_elem.get_text(strip=True)

                # Look for summary
                sum_elem = card.select_one('div.summary, div.description')
                if sum_elem:
                    description = sum_elem.get_text(strip=True)

                job = {
                    "id": job_url,
                    "source": "USAJOBS",
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "url": job_url,
                }
                results.append(job)

        return results
