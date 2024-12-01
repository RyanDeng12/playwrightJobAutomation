from playwright.sync_api import sync_playwright, Page
import time
from datetime import datetime
def log_in(page):
    URL = 'https://www.metacareers.com/login'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        # Wait for the input field to be visible
        page.wait_for_selector('input#js_1', state='visible', timeout=10000)
        time.sleep(5)
        # Fill the input field with the email
        page.fill('input#js_1', "375797869@qq.com")
        # page.fill('input#js_1', "ryan.y.deng@gmail.com")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Entered email: {"375797869@qq.com"}")
        time.sleep(5)
        # Fill the input field with the pwd
        page.fill('input#js_b', "!AZsxDCfvGB321a")
        time.sleep(5)
        # Click the button
        page.click('div[role="button"]:has-text("Log in")')
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked the 'Log in' button.")
        time.sleep(5)
        # Wait for the welcome message to appear
        page.wait_for_selector('h1:has-text("Welcome")', state='visible', timeout=60000)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Welcome message is visible.")
    except Exception as e:
        raise Exception('Error during the login process') from e