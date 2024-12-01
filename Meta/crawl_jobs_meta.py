import os
import time
import sys
from playwright.sync_api import sync_playwright, TimeoutError
from log_in_meta import log_in
import re
from datetime import datetime
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import insert_job

# Collect job links from the current page
def collect_job_links(page, context):
    company_name = "Meta"
    try:
        # Wait for the "Clear Filters" button to appear
        page.wait_for_selector('div[role="button"]:has-text("Clear Filters")', state='visible', timeout=10000)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clear Filters button is visible.")


        # Wait for the main container to load
        page.wait_for_selector('//*[@id="careersContentContainer"]')

        # Define the XPath to select all job postings starting from a specific index
        # Adjust the position() >= 4 if your list starts at a different index
        job_posts_xpath = '//*[@id="careersContentContainer"]/div/div[1]/div/div/div[2]/div/div[2]/div[position() >= 4]/div/div[1]/div[1]'

        # Select all job post elements starting from the specified position
        job_post_elements = page.locator(job_posts_xpath)

        # Get the count of job posts
        job_count = job_post_elements.count()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found {job_count} job posts.")

        for i in range(job_count):
            try:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job post {i + 1}...")

                # Scroll the job post into view
                job_post_elements.nth(i).scroll_into_view_if_needed()

                # Use expect_page to handle the new tab that opens upon clicking the job post
                with context.expect_page() as new_page_info:
                    # Click on the job post to open it in a new tab
                    job_post_elements.nth(i).click()
                
                # Get the new page that opened
                new_page = new_page_info.value
                # Avoid blockage
                time.sleep(10)
                # Wait for the careersPageContainer element to be visible
                page.wait_for_selector('#careersPageContainer', timeout=10000)  # waits up to 10 seconds
                
                # Assuming 'page' is your current page object from Playwright or a similar library
                page_title_element = new_page.query_selector('#pageTitle')
                title_text = page_title_element.inner_text() if page_title_element else ''

                # Extracting job title from the title text
                match = re.search(r'^(.*?) \| Meta Careers$', title_text)
                if match:
                    job_title = match.group(1).strip()
                    print(job_title)
                # Extract the URL of the new page (job post link)
                job_post_url = new_page.url
                job_number = job_post_url.split('/')[-2]
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Job post URL: {job_post_url}")

                # Perform any additional data extraction here if needed
                # For example, extract job title, description, etc.
                insert_job(company_name, job_title, job_number, job_post_url)
                # Close the new tab after processing
                new_page.close()
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error Processing job post: {e}")
                    

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error collecting job links: {e}")

# Function to go through all pages
def go_through_all_pages(page, context):
    while True:
        # Check for the "Load more" button using a more stable locator
        load_more_button = page.query_selector('text=Load more')

        if load_more_button:
            load_more_button.click()
            # Optionally wait for the new content to load
            page.wait_for_timeout(1000)  # Adjust the timeout as needed
        else:
            break  # Exit the loop if the button is not found
    
    collect_job_links(page, context)


def main():
    careerURL = 'https://www.metacareers.com/jobs?leadership_levels[0]=Individual%20Contributor&offices[0]=Remote%2C%20US&offices[1]=San%20Francisco%2C%20CA&offices[2]=New%20York%2C%20NY&offices[3]=Boston%2C%20MA&offices[4]=Washington%2C%20DC&offices[5]=Burlingame%2C%20CA&offices[6]=Seattle%2C%20WA&offices[7]=Menlo%20Park%2C%20CA&offices[8]=Atlanta%2C%20GA&offices[9]=Austin%2C%20TX&offices[10]=Redmond%2C%20WA&offices[11]=Bellevue%2C%20WA&offices[12]=Sunnyvale%2C%20CA&page=2'
    

    try:
        playwright = sync_playwright().start()
        # browser = playwright.chromium.launch(headless=False)
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        # Log in if necessary (your log_in function)
        # log_in(page)
        page.goto(careerURL)
        # Go through all pages and collect job links
        go_through_all_pages(page, context)

    except TimeoutError:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Timed out waiting for the application form to load.')
    except Exception as e:
        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - An error occurred: {str(e)}')
    finally:
        # browser.close()
        playwright.stop()

main()
