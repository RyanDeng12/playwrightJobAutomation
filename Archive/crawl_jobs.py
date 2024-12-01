import os
import time
from playwright.sync_api import sync_playwright, TimeoutError
import sqlite3
from log_in import log_in

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
        # Wait for the main job list to load
        page.wait_for_selector('div.listItems__1q9i5', timeout=60000)
        job_links = page.query_selector_all('a[href^="/referral/tiktok/position/"]')

        for link in job_links:
            title = link.query_selector('span.positionItem-title-text').inner_text()
            url = link.get_attribute('href')
            data_id = link.get_attribute('data-id')
            company_name = "TikTok"  # Hardcoded since this script is for TikTok careers

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Job Title: {title}")
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Data ID: {data_id}")
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Link: {url}")

            # Insert into the database
            insert_job(company_name, title, data_id, f"https://careers.tiktok.com{url}")

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error collecting job links: {e}")

# Function to go through all pages
def go_through_all_pages(page):
    while True:
        # Collect job links on the current page
        collect_job_links(page)

        try:
            # Check if 'Next Page' button is enabled
            next_button = page.query_selector('li.atsx-pagination-next[aria-disabled="false"]')
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
    URL = 'https://careers.tiktok.com/referral/tiktok/position?keywords=Engineer&category=&location=CT_94%2CCT_114%2CCT_157%2CCT_1103355&project=&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag=&token=MzsxNzE0NDUzMjgwMzQwOzczMTExNTg0NzkzNTAxMzgzNzc7MDsy'
    
    init_db()  # Initialize the database

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        # Log in if necessary (your log_in function)
        log_in(page)
        page.goto(URL)
        # Go through all pages and collect job links
        go_through_all_pages(page)

    except TimeoutError:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Timed out waiting for the application form to load.')
    except Exception as e:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - An error occurred: {str(e)}')
    finally:
        browser.close()
        playwright.stop()

main()
