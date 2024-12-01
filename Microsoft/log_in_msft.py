from playwright.sync_api import sync_playwright, Page
import time
from datetime import datetime
def log_in(page):
    URL = 'https://careers.microsoft.com/v2/global/en/home.html'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        # Wait for the element with specific class and text "Sign in"
        sign_in_div = page.wait_for_selector('div.msame_Header_name.st_msame_placeholder', timeout=10000)
        # Click on it once it appears
        sign_in_div.click()
        page.wait_for_selector('div[aria-label="Sign in with Microsoft"]', timeout=60000)  # Waits up to 10 seconds
        page.get_by_label('Sign in with Microsoft').click()
        page.get_by_label("Enter your email, phone, or Skype.").fill("375797869@qq.com")
        # Click the button with the visible text 'Next'
        page.get_by_role("button", name="Next").click()
        page.get_by_label("Password").fill("!AZsxDCfvGBhn321c")
        # Click the "Sign in" button using its id
        page.locator("#idSIButton9").click()
        # Click the button with the visible text 'Yes'
        # Wait for the "Yes" button to be visible, then click it
        page.wait_for_selector("#acceptButton", timeout=10000)  # Wait up to 10 seconds
        page.locator("#acceptButton").click()
        try:
            # Wait for the div with id 'mectrl_headerPicture' to appear
            page.wait_for_selector('#mectrl_headerPicture', timeout=10000)
            # time.sleep(1)
            page.goto('https://jobs.careers.microsoft.com/global/en/job/1776808')
            # Wait for the element with specific class and text "Sign in"
            sign_in_div = page.wait_for_selector('div.msame_Header_name.st_msame_placeholder', timeout=10000)
            # Click on it once it appears
            time.sleep(1)
            sign_in_div.click()
            time.sleep(1)
            page.wait_for_selector('div[aria-label="Sign in with Microsoft"]', timeout=60000)  # Waits up to 10 seconds
            time.sleep(1)
            page.get_by_label('Sign in with Microsoft').click()
            # Wait for the div with id 'mectrl_headerPicture' to appear
            page.wait_for_selector('#mectrl_headerPicture', timeout=30000)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Login sucessful.")
        except Exception:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Action Center button not found within the timeout period.")
    except Exception as e:
        raise Exception('Error during the login process') from e