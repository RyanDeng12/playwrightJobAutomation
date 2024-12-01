from playwright.sync_api import sync_playwright, Page
import time, sys, os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from input_text_by_id import input_text_by_id 
from human_scroll import human_scroll
from click_on_text import click_on_text
from click_by_id import click_by_id
from wait_for_text import wait_for_text
def log_in(page):
    URL = 'https://idmsa.apple.com/IDMSWebAuth/signin.html?appIdKey=967e0c9eb29cb96878a15488726dd401bae3c121c2b0b124d9e6eb537387d235&rv=2&path=%2Fen-us%2Fsearch%3Fsort%3Drelevance%26key%3Dengineer%26location%3Dunited-states-USA&view=0&language=US-EN'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        # Wait for the element with specific class and text "Sign in"
        

        # Fill the email address
        input_text_by_id(page, 'account_name_text_field', 'djyya123@163.com')
        print("Email input filled.")
        human_scroll(page)
        click_by_id(page, 'sign-in')
        click_by_id(page, 'continue-password')
        input_text_by_id(page, 'password_text_field', 'AZsxDCfvGBhn321a')
        click_by_id(page, 'sign-in')
        # Wait for the 'Continue' button with the text 'Continue' and click it
        # Click on the 'Next' button
        # Wait for the "Next" button to be visible
        if wait_for_text(page, 'Find your perfect role.', 360):
            print('Successfully logged in.')
        else:
            print('Failed to logged in.')
    except Exception as e:
        raise Exception('Error during the login process') from e