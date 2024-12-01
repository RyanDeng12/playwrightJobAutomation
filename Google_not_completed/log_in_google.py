from playwright.sync_api import sync_playwright, Page
import time
from datetime import datetime
def log_in(page):
    URL = 'https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fwww.google.com%2Fabout%2Fcareers%2Fapplications%2F&ec=GAZA6QE&followup=https%3A%2F%2Fwww.google.com%2Fabout%2Fcareers%2Fapplications%2F&ifkv=AcMMx-fX_HxJWMxYbx_fsupIrgnqrt3FN19tiu0SlPFguzZJZlG5afS42HSH9fJ5SrPDvT5FPg-E&passive=1209600&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S1812297108%3A1732714598074175&ddm=1'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        # Wait for the element with specific class and text "Sign in"
        

        # Fill the email address
        page.fill('input[type="email"]', 'ryan.y.deng@gmail.com')
        print("Email input filled.")

        # Wait for the 'Continue' button with the text 'Continue' and click it
        # Click on the 'Next' button
        # Wait for the "Next" button to be visible
        page.click('span[jsname="V67aGc"]:has-text("Next")')  # Click the "Next" button
        print("Continue button clicked.")
        # Wait for the password input field (using type and name attributes)
        password_selector = 'input[type="password"][name="Passwd"]'
        page.wait_for_selector(password_selector)

        # Fill in the password
        page.fill(password_selector, '!AZsxDCfvGBhn321c')  # Replace 'YOUR_PASSWORD' with your actual password
        print("Password input filled.")
    
        # Wait for the "Next" button to appear
        page.wait_for_selector('button:has-text("Next")')
        
        # Click the "Next" button
        page.click('button:has-text("Next")')
        print("Log in button clicked.")
        # Wait for the span containing the text "Your career"
        page.wait_for_selector('span:has-text("Your career")')
        print("Header 'Your career' is visible.")
    except Exception as e:
        raise Exception('Error during the login process') from e