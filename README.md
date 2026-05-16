# Job Scraper Bot

A Python-based job scraping and matching bot for USA federal, state, and private meteorology and environmental job postings.

## What this project includes

- `job_scraper_bot/main.py`: orchestrates scraping, matching, filtering, and digest generation
- `job_scraper_bot/fetchers`: source-specific fetchers for USAJobs, Indeed, LinkedIn, Glassdoor, and state boards
- `job_scraper_bot/matcher.py`: scoring logic tuned to resume and target role keywords
- `job_scraper_bot/storage.py`: duplicate filtering and resume keyword extraction from text
- `job_scraper_bot/digest.py`: HTML, text, and email digest outputs
- `job_scraper_bot/scheduler.py`: nightly scheduler support
- `scripts/create_windows_task.py`: helper for Windows Task Scheduler
- `scripts/setup_cron.sh`: example cron registration for Linux/macOS
- `resume.txt`: resume summary used to derive matching keywords
- `state_boards.json`: state job board URL collection for the state board fetcher

## Goals

- Scrape jobs nightly 
- Match postings to your resume and career goals
- Rank jobs by relevance to primary and secondary target terms
- Skip already-seen jobs across runs
- Generate a morning digest in HTML, text, and email-ready form

## Setup

1. Create and activate a Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Update `resume.txt` with your current resume summary or keywords.

4. Add or edit state board URLs in `state_boards.json` as needed.

5. Configure email sending via environment variables before running the bot:

```powershell
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USERNAME = "your@gmail.com"
$env:EMAIL_PASSWORD = "your_app_password"
$env:EMAIL_FROM = "your@gmail.com"
$env:EMAIL_TO = "rcg19fsu@gmail.com"
```

7. (Optional) Enable AI weather summaries

If you want an AI-written weather overview (concise narrative + bullet takeaways), add an OpenAI API key as an environment variable before running, or add it to your GitHub Actions secrets as `OPENAI_API_KEY`.

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:WEATHER_USE_AI_SUMMARY = "true"
```

By default the AI model used is `gpt-4o-mini`. To override the model, set `WEATHER_AI_MODEL`.

**See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed Gmail configuration steps.**

6. Run the bot once manually:

```powershell
python -m job_scraper_bot.main --run-once
```

7. Use the scheduler if you want the bot to run nightly:

## Scheduling

### Option A: GitHub Actions (Free, Cloud-Based, Always Running)

If you host this repo on GitHub, you can use GitHub Actions to run the bot nightly without needing your computer on.

1. Push your project to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/job-scraper-bot.git
git push -u origin main
```

2. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**

3. Add the following secrets:
   - `EMAIL_HOST` = `smtp.gmail.com`
   - `EMAIL_PORT` = `587`
   - `EMAIL_USERNAME` = your Gmail address
   - `EMAIL_PASSWORD` = your App Password
   - `EMAIL_FROM` = your Gmail address
   - `EMAIL_TO` = `your email`
   - (Optional) `OPENAI_API_KEY` = your OpenAI API key (enable AI weather summaries)

4. The workflow in `.github/workflows/scraper.yml` will automatically run daily at 21:00 UTC (adjust the cron schedule if needed).

5. Output files are committed back to the repo, so you can view digest history in your GitHub commits.

### Option B: Windows Task Scheduler (Local Computer)

Runs the bot only when your computer is on at 9 PM.

```powershell
python scripts\create_windows_task.py
```

### Option C: Linux/macOS Cron

For self-hosted systems running Linux or macOS:

```bash
sh scripts/setup_cron.sh
```

## Output

Generated files appear in the `output` folder:

- `digest.html`
- `digest.txt`
- `digest_email.txt`
- `jobs.json`

## Web UI

To view the latest digest in a browser, run:

```powershell
python -m job_scraper_bot.web
```

Then open `http://localhost:8000/`.

## Notes

- **Indeed scraping (403 errors)**: Indeed has aggressive bot protection. The scraper includes improved headers and delays, but may still be blocked. Consider using Indeed's public RSS feeds or API as alternatives.
- **State board URLs**: Some state job board URLs may change or require custom parsing. Update `state_boards.json` if URLs return 404.
- **Email**: If email sending fails with "Username and Password not accepted", verify you're using an App Password (not your Gmail password). See [EMAIL_SETUP.md](EMAIL_SETUP.md).
- **LinkedIn/Glassdoor**: These sites have JavaScript rendering and are difficult to scrape without Selenium or Playwright. The current fetchers are basic patterns.
- **Web UI**: The digest is served from `output/digest.html` via a simple Flask server. For production, use a proper WSGI server like Gunicorn.
