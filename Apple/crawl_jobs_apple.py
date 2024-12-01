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
from wait_for_text import wait_for_text
from extract_links import extract_links
from click_on_text import click_on_text
from human_scroll import human_scroll
from click_by_id import click_by_id

COOLING_FACTOR = 0.1
COMPANY_NAME = 'Apple'
# Collect job links from the current page
def collect_job_links(page):
    try:
        # Wait for the label with "Sort by" text
        # page.get_by_text("Find jobs in Software Development").wait_for()
        # Wait for the first element that contains the 'share' icon
        wait_for_text(page, 'Refine by')

        # Select all the <a> tags with the specific class that contain the href
        url_pattern = r"/en-us/details/\d+[^\s'\"]*"
        links = extract_links(page, url_pattern)
        base_url = 'https://jobs.apple.com/app/en-us/apply/'
        for link in links:
            info = link.split('/')
            job_number = info[3]
            title = info[4]
            full_url = base_url + job_number
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found job item number: {job_number}, title: {title}")
            insert_job(COMPANY_NAME, title, job_number, full_url)
            
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error collecting job links: {e}")

# Function to go through all pages
def go_through_all_pages(page):
    while True:
        # Collect job links on the current page
        wait_for_text(page, 'Refine by')
        human_scroll(page, COOLING_FACTOR)
        collect_job_links(page)

        try:
            # Check if 'Next Page' button is enabled
            if click_on_text('Next Page', page):
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Navigating to the next page...")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No more pages to process.")
                break  # Exit the loop if no more pages
        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error navigating to the next page: {e}")
            break  # Exit the loop if there is an issue

def main():
    careerURL = 'https://jobs.apple.com/en-us/search?sort=relevance&key=engineer&location=united-states-USA'
    
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
