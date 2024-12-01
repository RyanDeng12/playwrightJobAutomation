from playwright.sync_api import sync_playwright, Page
import time
from datetime import datetime
def log_in(page):
    URL = 'https://www.amazon.jobs/en-US/applicant/login'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        # Wait for the element with specific class and text "Sign in"
        email_selector = "input[name='email']"
        page.wait_for_selector(email_selector)

        # Fill the email address
        page.fill(email_selector, 'ryan.y.deng@gmail.com')
        print("Email input filled.")

        # Wait for the 'Continue' button with the text 'Continue' and click it
        continue_button_selector = "button:has-text('Continue')"
        page.wait_for_selector(continue_button_selector)
        page.click(continue_button_selector)
        print("Continue button clicked.")
        # Wait for the password input field (using type and name attributes)
        password_selector = "input[type='password'][name='password']"
        page.wait_for_selector(password_selector)

        # Fill in the password
        page.fill(password_selector, '!AZsxDCfvGBhn321a')
        print("Password input filled.")

        # Wait for the 'Log in' button and click it (using button text)
        login_button_selector = "button:has-text('Log in')"
        page.wait_for_selector(login_button_selector)
        page.click(login_button_selector)
        print("Log in button clicked.")
        # Define the selector for the <h1> element with the text "Applications"
        header_selector = "h1:has-text('Applications')"
        
        # Wait for the element to be visible, with a timeout of 60 seconds (60000 milliseconds)
        page.wait_for_selector(header_selector, timeout=60000)
        print("Header 'Applications' is visible.")
    except Exception as e:
        raise Exception('Error during the login process') from e