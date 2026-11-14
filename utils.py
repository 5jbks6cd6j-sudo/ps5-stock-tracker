import os
import logging
from curl_cffi import requests

def send_telegram_alert(message: str) -> bool:
    """Sends a notification via Telegram using environment variables."""
    # --- CONFIGURATION (Loaded from GitHub Secrets) ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logging.error(f"Telegram error: {e}")

def disable_github_workflow() -> bool:
    """Automatically disables the GitHub Actions workflow once stock is found."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not token or not repo:
        logging.error("GitHub token or repo not found in environment.")
        return

    # Get the workflow ID or filename
    url = f"https://api.github.com/repos/{repo}/actions/workflows/stock_check.yml/disable"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        logging.info("Workflow successfully disabled automatically!")
    else:
        logging.error(f"Failed to disable workflow: {response.status_code} - {response.text}")