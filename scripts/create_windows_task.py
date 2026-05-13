import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXECUTABLE = Path(__file__).resolve().parents[1] / ".venv" / "Scripts" / "python.exe"
TASK_NAME = "JobScraperBotDaily"
START_TIME = "21:00"
COMMAND = f"cd /d \"{PROJECT_ROOT}\" && \"{PYTHON_EXECUTABLE}\" -m job_scraper_bot.main --run-once"


def create_windows_task():
    print(f"Creating Windows scheduled task '{TASK_NAME}' for daily run at {START_TIME}.")
    subprocess.run(
        [
            "schtasks",
            "/Create",
            "/SC",
            "DAILY",
            "/TN",
            TASK_NAME,
            "/TR",
            COMMAND,
            "/ST",
            START_TIME,
            "/F",
        ],
        check=True,
    )
    print("Scheduled task created. Use Task Scheduler to review or edit the task.")


if __name__ == "__main__":
    create_windows_task()
