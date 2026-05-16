import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from job_scraper_bot.config import (
    WEATHER_HTML_FILE,
    WEATHER_TEXT_FILE,
    WEATHER_EMAIL_FILE,
    WEATHER_USE_AI_SUMMARY,
    WEATHER_AI_MODEL,
)
try:
    import openai
except Exception:
    openai = None


class WeatherSummaryGenerator:
    def __init__(self):
        self.sections = []

    def _fetch(self, url, timeout=20):
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            return r.text
        except Exception as exc:
            return None

    def _extract_headlines(self, html, selectors=None, fallback=3):
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        headlines = []
        if selectors:
            for sel in selectors:
                for el in soup.select(sel):
                    text = el.get_text(strip=True)
                    if text and text not in headlines:
                        headlines.append(text)
                        if len(headlines) >= fallback:
                            return headlines
        # fallback: collect h1/h2/h3
        for tag in ("h1", "h2", "h3"):
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text and text not in headlines:
                    headlines.append(text)
                    if len(headlines) >= fallback:
                        return headlines
        return headlines[:fallback]

    def _summarize_simple(self, texts, max_sentences=3):
        # naive summarizer: take first sentences from concatenated text
        import re

        concat = "\n\n".join([t for t in texts if t])
        if not concat:
            return "No summary available."
        # split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", concat)
        sentences = [s.strip() for s in sentences if s.strip()]
        return " ".join(sentences[:max_sentences])

    def _ai_summarize_section(self, title, headlines, fallback_summary):
        if not WEATHER_USE_AI_SUMMARY or openai is None:
            return fallback_summary
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return fallback_summary
        try:
            openai.api_key = api_key
            prompt = (
                f"You are a concise meteorology-aware assistant.\n\nSection: {title}\n\n"
                "Given the following headlines, produce:\n"
                "1) a 2-3 sentence plain-text summary, and\n"
                "2) a short list of 2-4 actionable bullet takeaways.\n\n"
                "Headlines:\n" + "\n".join(f"- {h}" for h in headlines)
            )
            response = openai.ChatCompletion.create(
                model=WEATHER_AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.2,
            )
            text = response["choices"][0]["message"]["content"].strip()
            return text
        except Exception:
            return fallback_summary

    def build(self):
        # NHC - National Hurricane Center
        nhc_html = self._fetch("https://www.nhc.noaa.gov/")
        nhc_headlines = self._extract_headlines(nhc_html, selectors=[".map-title", ".headline", ".contentBox h2"], fallback=4)
        nhc_text = " \n ".join(nhc_headlines)
        nhc_summary = self._summarize_simple(nhc_headlines, max_sentences=4)
        self.sections.append({"title": "Hurricane/NHC", "headlines": nhc_headlines, "summary": nhc_summary, "source": "https://www.nhc.noaa.gov/"})

        # SPC - Storm Prediction Center
        spc_html = self._fetch("https://www.spc.noaa.gov/")
        spc_headlines = self._extract_headlines(spc_html, selectors=["#topcontent h2", ".box header h3", ".headline"], fallback=4)
        spc_summary = self._summarize_simple(spc_headlines, max_sentences=3)
        self.sections.append({"title": "Convective/Severe Weather (SPC)", "headlines": spc_headlines, "summary": spc_summary, "source": "https://www.spc.noaa.gov/"})

        # NOAA top stories
        noaa_html = self._fetch("https://www.noaa.gov/")
        noaa_headlines = self._extract_headlines(noaa_html, selectors=[".views-row h3", ".top-stories__headline"], fallback=5)
        noaa_summary = self._summarize_simple(noaa_headlines, max_sentences=3)
        self.sections.append({"title": "NOAA Top Stories", "headlines": noaa_headlines, "summary": noaa_summary, "source": "https://www.noaa.gov/"})
        # If configured, run AI summarization per section
        if WEATHER_USE_AI_SUMMARY:
            for sec in self.sections:
                sec_fallback = sec.get("summary", "")
                sec["summary"] = self._ai_summarize_section(sec.get("title", ""), sec.get("headlines", []), sec_fallback)

    def write_text(self):
        lines = [f"Weather Summary - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ""]
        for sec in self.sections:
            lines.append(sec["title"])
            lines.append("-")
            if sec["headlines"]:
                for hl in sec["headlines"]:
                    lines.append(f"- {hl}")
            else:
                lines.append("(no headlines found)")
            lines.append("")
            lines.append("Summary:")
            lines.append(sec["summary"]) 
            lines.append("")
        with open(WEATHER_TEXT_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

    def write_html(self):
        parts = ["<html><head><meta charset=\"utf-8\"><title>Weather Summary</title></head><body>"]
        parts.append(f"<h1>Weather Summary - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</h1>")
        for sec in self.sections:
            parts.append(f"<h2>{sec['title']}</h2>")
            parts.append("<ul>")
            if sec["headlines"]:
                for hl in sec["headlines"]:
                    parts.append(f"<li>{hl}</li>")
            else:
                parts.append("<li>(no headlines found)</li>")
            parts.append("</ul>")
            parts.append(f"<p><strong>Summary:</strong> {sec['summary']}</p>")
        parts.append("</body></html>")
        with open(WEATHER_HTML_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(parts))

    def write_email(self):
        lines = [f"Subject: Weather Summary - {datetime.utcnow().strftime('%Y-%m-%d')}", "", "Good morning, here is the automated weather summary:", ""]
        for sec in self.sections:
            lines.append(sec["title"])
            lines.append("")
            lines.append(sec["summary"])
            lines.append("")
        with open(WEATHER_EMAIL_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
 