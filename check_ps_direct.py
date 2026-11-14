import logging
import os
from curl_cffi import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION (Loaded from GitHub Secrets) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_URL = "https://www.playstation.com/pt-pt/ps5/ps5-pro/buy-now/product/PSD001-PSDE01942_39-PS5PROCHASASIRSE/"

# Timing (Base 90 seconds + 10 to 30 seconds of random jitter)
BASE_INTERVAL = 90
JITTER_MIN = 10
JITTER_MAX = 30

# Out-of-stock text to look for
OUT_OF_STOCK_TEXT = "não disponível para compra"

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Use a session to maintain cookies like a real browser
session = requests.Session()

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logging.error(f"Error sending Telegram notification: {e}")

def check_stock():
    try:
        logging.info("Checking PlayStation store stock...")
        # impersonate="chrome" fakes the browser's cryptographic fingerprint
        response = requests.get(TARGET_URL, impersonate="chrome", timeout=15)
        
        if response.status_code == 403 or response.status_code == 429:
            logging.warning(f"Blocked or Rate-limited! HTTP Status: {response.status_code}. Consider slowing down check intervals.")
            return
        elif response.status_code != 200:
            logging.warning(f"Received unexpected status code {response.status_code}. Retrying later.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        if OUT_OF_STOCK_TEXT in page_text:
            logging.info("Status: Still out of stock ('Não disponível para compra' found).")
        else:
            logging.warning("ALERT: Out-of-stock text NOT found! It might be available!")
            alert_msg = (
                "🚨 *PS5 Pro Stock Alert!* 🚨\n\n"
                "A PS5 Pro console was detected on playstation.com!\n"
                f"Check it immediately:\n{TARGET_URL}"
            )
            send_telegram_message(alert_msg)

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error occurred: {e}")

if __name__ == "__main__":
    check_stock()
