import json
import os
import re
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from job_scraper_bot.config import (
    STATE_BOARD_URLS,
    STATE_BOARD_URLS_FILE,
    STATE_BOARD_QUERY_STATES,
    USER_AGENT,
)
from job_scraper_bot.fetchers import JobFetcher


class StateBoardFetcher(JobFetcher):
    def source_name(self):
        return "StateBoards"

    def _build_state_urls(self, base_url):
        if "{state}" in base_url:
            return {
                state: base_url.format(state=quote_plus(state))
                for state in STATE_BOARD_QUERY_STATES
            }

        if base_url.endswith("location="):
            return {
                state: f"{base_url}{quote_plus(state)}"
                for state in STATE_BOARD_QUERY_STATES
            }

        return {"State": base_url}

    def _load_state_urls(self):
        if os.path.exists(STATE_BOARD_URLS_FILE):
            try:
                with open(STATE_BOARD_URLS_FILE, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    if isinstance(data, dict) and data:
                        processed = {}
                        for state, url in data.items():
                            if state.lower() == "state":
                                processed.update(self._build_state_urls(url))
                            else:
                                processed[state] = url
                        return processed
            except (OSError, json.JSONDecodeError):
                print(f"Unable to parse state board url file: {STATE_BOARD_URLS_FILE}")
        return self._build_state_urls(STATE_BOARD_URLS.get("State", ""))

    def _extract_location(self, parent, default_location):
        if not parent:
            return default_location

        for selector in [
            ".job-location",
            ".location",
            ".job-location span",
            ".location span",
            "span[itemprop='jobLocation']",
        ]:
            node = parent.select_one(selector)
            if node:
                text = node.get_text(" ", strip=True)
                if text:
                    return text

        for tag in parent.find_all(["span", "div", "p"], limit=20):
            text = tag.get_text(" ", strip=True)
            if text and default_location.lower() in text.lower():
                return text
            if re.search(r"\b[A-Za-z ]+,?\s*[A-Z]{2}\b", text):
                return text

        return default_location

    def fetch_jobs(self):
        results = []
        state_urls = self._load_state_urls()

        for state, url in state_urls.items():
            try:
                response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            except requests.exceptions.RequestException as exc:
                print(f"State board fetch failed for {state}: {exc}")
                continue

            if response.status_code != 200:
                print(f"State board fetch failed for {state}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.select("a"):
                href = link.get("href")
                text = link.get_text(strip=True)
                if not href or not text or href.startswith("javascript:") or href.startswith("#"):
                    continue

                if self._is_job_link(href, text):
                    job_url = requests.compat.urljoin(url, href)
                    parent = link.find_parent(["article", "li", "div"])
                    location = self._extract_location(parent, state)
                    job = {
                        "id": job_url,
                        "source": f"StateBoard:{state}",
                        "title": text,
                        "company": state,
                        "location": location,
                        "description": text,
                        "url": job_url,
                    }
                    results.append(job)

        return results

    def _is_job_link(self, href, text):
        href_lower = href.lower()
        if "/jobs/" in href_lower:
            return True

        job_patterns = ["job", "career", "opening", "position", "vacancy", "announcement", "opportunity"]
        text_lower = text.lower()
        return any(pattern in href_lower or pattern in text_lower for pattern in job_patterns)
