# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
import sys
from playwright.sync_api import sync_playwright, TimeoutError
import re
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import insert_job

# Collect job links from the current page
def collect_job_links(page):
    try:
        # Wait for the label with "Sort by" text
        # page.get_by_text("Find jobs in Software Development").wait_for()
        # Wait for the first element that contains the 'share' icon
        page.wait_for_selector('i[aria-hidden="true"]:has-text("share")', timeout=60000)
        company_name = 'Google'

        # Select all the <a> tags with the specific class that contain the href
        links = page.query_selector_all('a.WpHeLc.VfPpkd-mRLv6.VfPpkd-RLmnJb')
        # Define regex to extract the job number and title
        job_regex = r"jobs/results/(\d+)-([a-z0-9\-]+)"
        # Base URL
        base_url = 'https://www.google.com/about/careers/applications/'

        # Combine the base URL with the hrefs to create full URLs
        full_links = []
        for link in links:
            href = link.get_attribute('href')
            if href:  # Only proceed if href is not None
                # Match the job number and job title using regex
                match = re.search(job_regex, href)
                job_number = match.group(1)
                title = match.group(2)
                full_url = base_url + href
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found job item number: {job_number}, title: {title}")
                insert_job(company_name, title, job_number, full_url)
            
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
    careerURL = 'https://www.google.com/about/careers/applications/jobs/results/?location=United%20States&skills=engineering'
    
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
