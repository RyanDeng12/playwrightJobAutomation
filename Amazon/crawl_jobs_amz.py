# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
import sys
from playwright.sync_api import sync_playwright, TimeoutError
from log_in_amz import log_in
import re
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import insert_job

# Collect job links from the current page
def collect_job_links(page):
    try:
        # Wait for the label with "Sort by" text
        # page.get_by_text("Find jobs in Software Development").wait_for()
        page.get_by_text("Find jobs in Software Development").nth(0).wait_for(timeout = 60000)
        company_name = 'Amazon'

        #  Wait for job tiles to load (adjust the selector if needed)
        page.wait_for_selector("ul.jobs-module_root__gY8Hp li div a")

        # Locate all elements with the class "job-tile"
        job_links = page.query_selector_all('ul.jobs-module_root__gY8Hp li div a')

        # Loop through each job listing and check for specific titles
        for job in job_links:
            title = job.get_attribute('aria-label')
            link = job.get_attribute('href')
            match = re.search(r"/jobs/(\d+)", link)
            job_number = match.group(1) if match else None
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found job item number: {job_number}, title: {title}")
            insert_job(company_name, title, job_number, f"https://www.amazon.jobs{link}")
            
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error collecting job links: {e}")

# Function to go through all pages
def go_through_all_pages(page):
    while True:
        # Collect job links on the current page
        collect_job_links(page)

        try:
            # Check if 'Next Page' button is enabled
            next_button = page.get_by_label('Next')
            if next_button:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Navigating to the next page...")
                next_button.click()
                time.sleep(3)  # Small delay to let the page load
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No more pages to process.")
                break  # Exit the loop if no more pages
        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error navigating to the next page: {e}")
            break  # Exit the loop if there is an issue

def main():
    careerURL = 'https://www.amazon.jobs/content/en/job-categories/software-development?country%5B%5D=US'
    
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        # browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        # Log in if necessary (your log_in function)
        # log_in(page)
        page.goto(careerURL)
        # Go through all pages and collect job links
        go_through_all_pages(page)

    except TimeoutError:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Timed out waiting for the application form to load.')
    except Exception as e:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - An error occurred: {str(e)}')
    finally:
        # browser.close()
        playwright.stop()

main()
