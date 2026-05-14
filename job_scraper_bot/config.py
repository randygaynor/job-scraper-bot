import os
from datetime import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_path(relative_path):
    return os.path.normpath(os.path.join(PROJECT_ROOT, relative_path))

DEFAULT_RESUME_KEYWORDS = [
    "meteorology",
    "atmospheric",
    "weather",
    "forecast",
    "operational",
    "NOAA",
    "NWS",
    "USAJobs",
    "hurricane",
    "tropical",
    "data assimilation",
    "WRF",
    "Python",
    "GIS",
    "spatial",
    "visualization",
    "HPC",
    "climate",
    "risk",
    "insurance",
    "emergency management",
    "environmental",
    "analyst",
    "remote",
    "modeling",
    "analysis",
    "data",
    "scientist",
]

PRIMARY_TARGET_TERMS = [
    "meteorologist",
    "atmospheric scientist",
    "operational forecaster",
    "research meteorologist",
    "hurricane analyst",
    "tropical weather analyst",
    "NWS",
    "NOAA",
    "USAJobs",
]

SECONDARY_TARGET_TERMS = [
    "environmental data scientist",
    "geospatial analyst",
    "climate risk analyst",
    "weather risk analyst",
    "emergency management specialist",
    "insurance",
    "risk analyst",
    "data assimilation",
    "spatial",
    "visualization",
]

SEARCH_TERMS = [
    "meteorologist",
    "atmospheric scientist",
    "hurricane analyst",
    "tropical weather analyst",
    "operational forecaster",
    "research meteorologist",
    "environmental data scientist",
    "geospatial analyst",
    "climate risk analyst",
    "weather risk analyst",
    "emergency management specialist",
]

JOB_SOURCES = [
    "USAJOBS",
    "Indeed",
    "LinkedIn",
    "Glassdoor",
    "StateBoards",
]

SCHEDULE_TIME = time(hour=21, minute=0)

OUTPUT_DIRECTORY = "output"
JOB_STORAGE_FILE = "output/jobs.json"
DIGEST_HTML_FILE = "output/digest.html"
DIGEST_TEXT_FILE = "output/digest.txt"
DIGEST_EMAIL_FILE = "output/digest_email.txt"
RESUME_FILE = "resume.txt"
RESUME_KEYWORDS_FILE = "resume_keywords.txt"
STATE_BOARD_URLS_FILE = "state_boards.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USERNAME)
EMAIL_TO = os.getenv("EMAIL_TO", "rcg19fsu@gmail.com")

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
BROADCAST_EXCLUSION_TERMS = [
    "broadcast",
    "broadcast meteorology",
    "tv meteorologist",
    "television meteorologist",
    "on-air meteorologist",
    "on-air",
    "on-camera",
    "weather anchor",
    "anchor",
    "sinclair",
    "cnn",
    "gray media",
    "hearst",
    "gray television",
    "emmis",
    "television station",
    "tv station",
    "news station",
    "news director",
    "live broadcast",
    "wect",
    "ktiv",
    "wjhg",
    "wdtv",
    "kvvu",
    "kosa",
    "wlfi",
    "Chief Meteorologist",
    "Channel",
    "W/END",
    "Weekend Meteorologist",
    "News and Stations",
    "Freelance",
    "News 12",
    "on camera",
    "Allen Media",
    "WPTV",
    "WJCL",
    "WTVJ",
    "WFXL",
    "WECT",
    "WTVD",
    "WESH",
    "WLOX",
    "WVTM",
    "WINK",
    "WBND",
    "TEGNA",
    "Nexstar",
    "Spectrum",
    "WGBA",
]
MIN_EMAIL_SCORE = 3

WINDOWS_TASK_NAME = "JobScraperBotDaily"

STATE_BOARD_QUERY_STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]

STATE_BOARD_URLS = {
    "State": "https://www.governmentjobs.com/jobs?keyword=&location="
}
