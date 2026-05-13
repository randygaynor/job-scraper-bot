# Email and Web UI Setup Guide

## Gmail SMTP Configuration

To send job digests via email, you need to configure Gmail SMTP credentials using environment variables.

### Step 1: Enable 2-Factor Authentication

1. Go to https://myaccount.google.com
2. Click "Security" in the left sidebar
3. Scroll to "How you sign in to Google" and enable "2-Step Verification"

### Step 2: Create an App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your platform)
3. Google will generate a 16-character password
4. Copy this password

### Step 3: Configure Environment Variables

On Windows PowerShell:

```powershell
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USERNAME = "your@gmail.com"
$env:EMAIL_PASSWORD = "your-16-char-app-password"
$env:EMAIL_FROM = "your@gmail.com"
$env:EMAIL_TO = "rcg19fsu@gmail.com"
```

To persist these variables across sessions, add them to your PowerShell profile:

```powershell
# Edit your profile
notepad $PROFILE
```

Add the above lines to the file.

### Step 4: Test Email Sending

```powershell
python -m job_scraper_bot.main --run-once
```

Check for "Email digest sent successfully" in the output.

## Web UI Configuration

The web UI runs on `http://localhost:8000` by default.

To change the host/port, set environment variables:

```powershell
$env:WEB_HOST = "0.0.0.0"
$env:WEB_PORT = "8000"
```

Then run:

```powershell
python -m job_scraper_bot.web
```

Visit the URL shown in the terminal.
