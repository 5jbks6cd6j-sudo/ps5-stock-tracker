import time
import os
import logging
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WORTEN_SEARCH_URL = "https://www.worten.pt/search?query=ps5+pro&f.range_visibility=True&f.seller_id=Worten&f.brand_name=SONY+PLAYSTATION&f.storage=2+TB"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

def send_telegram_alert(message):
    try:
        from curl_cffi import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logging.error(f"Telegram error: {e}")

def check_worten_with_playwright():
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="pt-PT"
        )
        page = context.new_page()
        
        try:
            logging.info("Checking Worten filtered search results...")            # Go to page and wait until network calls complete
            page.goto(WORTEN_SEARCH_URL, timeout=30000, wait_until="domcontentloaded")

            # Wait for Nuxt to render either product cards OR the "no results" empty state
            try:
                page.wait_for_selector(
                    "[data-testid='product-card'], .product-card, .w-product, :text('Não encontrámos resultados')",
                    timeout=15000
                )
            except Exception:
                # Extra buffer if Worten's frontend is slow to hydrate
                time.sleep(5)

            # Grab all product links/cards on the page
            product_cards = page.locator("a[href*='/produtos/']").all()
            
            for card in product_cards:
                card_text = card.inner_text().lower()
                
                # Must be a PS5 Pro console (exclude controllers, covers, stands, games)
#                if "consola" in card_text and "ps5" in card_text and "pro" in card_text:
                if "consola" in card_text and "ps5 pro" in card_text:
                    logging.info("Possible stock detected!")

                    alert_msg = (
                        "🚨 *Worten PS5 Pro Stock Alert!* 🚨\n\n"
                        "A PS5 Pro console was detected on Worten.pt!\n"
                        f"Check immediately:\n{WORTEN_SEARCH_URL}"
                    )
                    send_telegram_alert(alert_msg)
                    break
            else:
                logging.info("Status: No official Worten PS5 Pro console in search results.")

        except Exception as e:
            logging.error(f"Playwright execution error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_worten_with_playwright()