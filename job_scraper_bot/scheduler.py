import schedule
import time
from datetime import datetime
from job_scraper_bot.config import SCHEDULE_TIME


def schedule_nightly_run(task_callable):
    schedule_time = SCHEDULE_TIME.strftime("%H:%M")
    print(f"Scheduling nightly run at {schedule_time} local time.")
    schedule.every().day.at(schedule_time).do(task_callable)

    print("Scheduler started. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(10)


def run_now(task_callable):
    task_callable()


def parse_run_time(dt=None):
    return dt if dt is not None else datetime.now()
