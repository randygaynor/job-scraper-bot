#!/bin/sh
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_EXECUTABLE="$PROJECT_ROOT/.venv/bin/python"
CRON_ENTRY="0 21 * * * cd \"$PROJECT_ROOT\" && \"$PYTHON_EXECUTABLE\" -m job_scraper_bot.main --run-once"

crontab -l 2>/dev/null | grep -v -F "job_scraper_bot.main --run-once" > /tmp/current_cron || true
printf "%s\n%s\n" "# Job Scraper Bot daily schedule" "$CRON_ENTRY" >> /tmp/current_cron
crontab /tmp/current_cron
rm -f /tmp/current_cron

echo "Cron job registered for daily run at 21:00 local time."