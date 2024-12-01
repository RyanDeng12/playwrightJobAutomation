# main.py
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from log_in_google import log_in  # Assuming log_in is correctly implemented and imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from human_scroll import human_scroll
from click_on_text import click_on_text
from wait_for_text import wait_for_text
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied

COOLING_FACTOR = 1


def process_job_link(data_id, link, page, browser):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        page.goto(link, timeout=60000)
        try:
            # Wait for the span containing the text "Your career"
            page.wait_for_selector('span:has-text("Your career")')
            # Wait for the span element containing the exact text "Apply"
            # page.wait_for_selector('span.VfPpkd-vQzf8d:has-text("Apply")')
            print("Header 'Your career' is visible.")
            human_scroll(page, COOLING_FACTOR)
            # Define the selector for the "Apply now" button using exact text match
            page.click('span.VfPpkd-vQzf8d:has-text("Apply")', force=True)
            wait_for_text(page, 'Next')
            # Force the click action to open the dropdown list
            page.click('span.VfPpkd-t08AT-Bz112c', force=True)
            # Select the first option
            time.sleep(COOLING_FACTOR)
            page.click('ul.VfPpkd-rymPhb')
            time.sleep(COOLING_FACTOR)
            checkboxes = page.locator("ul[aria-label='Additional location options list with multiple selection'] input[type='checkbox']")
            # Loop through all the checkboxes and check them
            checkbox_count = checkboxes.count()
            for i in range(checkbox_count):
                checkbox = checkboxes.nth(i)
                checkbox.check(force=True)
                time.sleep(COOLING_FACTOR)
            # Find all radio buttons with the value 'Yes' and select them for Minimum qualifications
            radio_buttons = page.query_selector_all('input[type="radio"][value="1"]')

            for radio in radio_buttons:
                radio.check()
                time.sleep(COOLING_FACTOR)
            
            page.click('input[name="WorkAuthEligibleQuestion"][value="Yes"]')
            time.sleep(COOLING_FACTOR)
            page.click('input[name="WorkAuthSponsorQuestion"][value="No"]')
            human_scroll(page, COOLING_FACTOR)
            click_on_text('Next', page)
            # Wait for the <h1> element that contains the text "Voluntary self-identification"
            wait_for_text(page, 'Voluntary self-identification')
            # Click on the "Male" label
            click_on_text("Male", page)
            time.sleep(COOLING_FACTOR)
            # Click on the "Asian" span
            click_on_text("Asian", page)
            time.sleep(COOLING_FACTOR)
            # Click on "I am not a protected veteran"
            click_on_text("I am not a protected veteran", page)
            time.sleep(COOLING_FACTOR)
            click_on_text("No, I don't have a disability", page)
            time.sleep(COOLING_FACTOR)
            click_on_text("No, I do not have a disability and have not had one in the past", page)
            time.sleep(COOLING_FACTOR)

            click_on_text("No - I am not currently serving or have never served in a military in the past", page)
            time.sleep(COOLING_FACTOR)

            # Click on "No, I do not have a disability and have not had one in the past"
            click_on_text('Next', page)
            time.sleep(COOLING_FACTOR)
            click_on_text('Next', page)
            wait_for_text(page, 'Review your application')
            human_scroll(page, COOLING_FACTOR)
            click_on_text("I understand that the information I submit as part of my job application will be used in accordance with Google's applicant and candidate privacy policy.open_in_new I consent to the processing of my information as described in that policy including that, in limited circumstances, Google may share my contact information with trusted third parties, to assist in certain phases of the hiring process (such as conducting background checks).", page)
            time.sleep(COOLING_FACTOR)
            click_on_text("Apply", page)
            human_scroll(page, COOLING_FACTOR)
            wait_for_text(page, 'Review your application')


            
        except TimeoutError:
            print("Timed out waiting for the 'DESCRIPTION' header.")
        

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")



def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs('Google')
    if not jobs:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No unprocessed jobs found.")
        return

    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found {len(jobs)} unprocessed jobs.")
        playwright = sync_playwright().start()
        # browser = playwright.chromium.launch(headless=False)
        browser = playwright.chromium.launch(
        headless=False,  # Set to False to see the UI (you can set True if you don't need the UI)
        args=[
            "--disable-notifications",                     # Disable notifications
            "--disable-gpu",                               # Disable GPU hardware acceleration
            "--disable-setuid-sandbox",                    # Disable sandboxing features
            "--deterministic-fetch",                       # Use deterministic fetches
            "--disable-features=IsolateOrigins,site-per-process",  # Disable site isolation
            "--disable-site-isolation-trials",            # Disable site isolation trials
            "--disable-web-security",                     # Disable web security checks
            "--disable-blink-features=AutomationControlled",  # Disable automation detection
        ]
    )
    #     context = browser.new_context(
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # )
    #     page = context.new_page()
        page = browser.new_page()

        # Log in
        log_in(page)

        # Process each job
        for data_id, link in jobs:
            
            process_job_link(data_id, link, page, browser)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}")
    finally:
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    main()
