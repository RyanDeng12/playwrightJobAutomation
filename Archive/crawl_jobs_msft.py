import os
import time
from playwright.sync_api import sync_playwright, TimeoutError
import sqlite3
from log_in_msft import log_in
import re

# Get the current directory path
DB_PATH = os.path.join(os.getcwd(), 'jobs.db')

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            company_name TEXT,
            job_title TEXT,
            data_id TEXT,
            link TEXT,
            applied BOOLEAN,
            create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, data_id)  -- Deduplication constraint
        )
    ''')
    conn.commit()
    conn.close()

# Insert job data into the database with deduplication
def insert_job(company_name, job_title, data_id, link):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO job_posts (company_name, job_title, data_id, link, applied) 
            VALUES (?, ?, ?, ?, ?)
        ''', (company_name, job_title, data_id, link, False))
        conn.commit()
    except sqlite3.Error as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SQLite Error: {e}")
    finally:
        conn.close()
# Collect job links from the current page
def collect_job_links(page):
    try:
        # Wait for the label with "Sort by" text
        page.get_by_text("Sort by").wait_for()
        # Find all job items based on the "aria-label" attribute starting with "Job item"
        job_elements = page.query_selector_all("[aria-label^='Job item']")
        company_name = 'Microsoft'

        # Loop through each job item and extract the job number and title
        for job_element in job_elements:
            # Extract the job item number from the aria-label attribute
            aria_label = job_element.get_attribute("aria-label")
            job_number_match = re.search(r"Job item (\d+)", aria_label)
            
            # Extract the job title, assuming it's within an <h2> element inside the job card
            title_element = job_element.query_selector("h2")
            title = title_element.inner_text() if title_element else "No title found"
            
            # Check that job number was found and add to results
            if job_number_match:
                job_number = job_number_match.group(1)
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found job item number: {job_number}, title: {title}")
                insert_job(company_name, title, job_number, f"https://jobs.careers.microsoft.com/global/en/job/{job_number}")

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
    careerURL = 'https://jobs.careers.microsoft.com/global/en/search?q=Engineer&lc=United%20States&l=en_us&pg=1&pgSz=20&o=Relevance&flt=true'
    
    init_db()  # Initialize the database

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        # Log in if necessary (your log_in function)
        log_in(page)
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
