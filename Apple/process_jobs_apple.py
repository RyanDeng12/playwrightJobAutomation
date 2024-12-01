# main.py
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from log_in_apple import log_in  # Assuming log_in is correctly implemented and imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from human_scroll import human_scroll
from click_on_text import click_on_text
from wait_for_text import wait_for_text
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied
from click_by_id import click_by_id
COOLING_FACTOR = 20


def process_job_link(data_id, link, page, browser):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        page.goto(link, timeout=60000)
        try:
            # Wait for the span containing the text "Your career"
            wait_for_text(page, 'Your Resume')
            human_scroll(page, COOLING_FACTOR)
            click_by_id(page, "applyResumeContinue")
            human_scroll(page, COOLING_FACTOR)
            click_by_id(page, 'applyReviewSubmit')
            human_scroll(page, COOLING_FACTOR)
            wait_for_text(page, 'Thanks, Jianyang Deng.')
            mark_job_as_applied('Apple', data_id, 1)
            print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Update the applied status of {data_id} in your record')
            
        except TimeoutError:
            print(f"Timed out waiting for application complete message for {data_id}.")
        

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")



def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs('Apple')
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
