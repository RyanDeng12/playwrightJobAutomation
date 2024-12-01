# main.py
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from log_in_amz import log_in  # Assuming log_in is correctly implemented and imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from human_scroll import human_scroll
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied


def handle_scenario_a(page):
    try:
        print('Enter Job-specific questions')
        # Wait for the 'Job-specific questions' section to be loaded
        page.wait_for_selector("h2:has-text('Job-specific questions')")
        
        # Find all the elements with the placeholder text "Select an option"
        select_elements = page.query_selector_all("span.select2-selection__placeholder:has-text('Select an option')")

        # Loop through each of the select elements and click to open the dropdown
        for select in select_elements:
            # Click to open the dropdown
            time.sleep(1)  # Sleep for 3 seconds (adjust as necessary)
            select.click()
            time.sleep(1)  # Sleep for 3 seconds (adjust as necessary)
            # Wait for the options to appear in the dropdown
            page.wait_for_selector("ul.select2-results__options li")
            
            # Get all the options from the dropdown
            options = page.query_selector_all("ul.select2-results__options li")

            # Loop through options and click the one that matches
            for option in options:
                option_text = option.inner_text()        
                if 'Yes' in option_text:
                    option.click()  # Click the 'Yes' option
                    break
                elif '3 to 4 years' in option_text:
                    option.click()  # Click the '3 to 4 years' option
                    break

        # Click Continue button after selecting options
    
        human_scroll(page)
        page.click("button[type='button']:has-text('Continue')")
        time.sleep(3)
    
    except Exception as e:
        print(f"Error in Job-specific questions: {e}")

def handle_scenario_b(page):
    try:
        # Wait for the 'Work Eligibility' section
        page.wait_for_selector("h2:has-text('Work Eligibility')")

        # Check 'No' for immigration sponsorship question
        # Click the element using XPath
        page.click('//*[@id="REQUIRE_SPONSORSHIP-option-1-label"]')
        
        # Check 'No, I was NEVER a government employee.' for the government employee question
        page.click('//*[@id="GEF_EXT_USA_GOVERNMENT_EMPLOYEE-option-0-label"]')
        
        human_scroll(page)
        # Find and click Continue button
        page.click("button[type='button']:has-text('Continue')")
        # Wait for the "Submit application" button to appear
        page.wait_for_selector("button.btn.btn-primary.submit:visible")
        # Click the Submit application button
        submit_button = page.query_selector("button.btn.btn-primary.submit")
        submit_button.click()

    except Exception as e:
        print(f"Error in Work Eligibility: {e}")


def process_job_link(data_id, link, page, browser):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        page.goto(link, timeout=60000)
        # Define the selector for the <h2> element with the text "DESCRIPTION"
        header_selector = "h2:has-text('DESCRIPTION')"
        try:
            # Wait for the element to be visible, with a timeout of 60 seconds (60000 milliseconds)
            page.wait_for_selector(header_selector, timeout=60000)
            print("Header 'DESCRIPTION' is visible.")
            # Define the selector for the "Apply now" button using exact text match
            apply_button_selector = "a:has-text('Apply now')"

            # Wait for the apply button to be visible with a timeout of 60 seconds
            page.wait_for_selector(apply_button_selector, timeout=60000)

            # Click the apply button
            apply_button = page.locator(apply_button_selector)
            apply_button.click()

            print("Clicked the 'Apply now' button.")
            # Check for Job-specific questions
            try:
                # Wait for the 'Job-specific questions' section for up to 60 seconds
                page.wait_for_selector("h2:has-text('Job-specific questions')", timeout=10000)  # Timeout set to 60 seconds
                # If the element is found within the timeout, perform Action for Job-specific questions
                print("Element found! Performing Action for Job-specific questions...")
                handle_scenario_a(page)
            except Exception as e:
                # If element is not found in time, ignore
                print(f"Element not found within timeout. Ignoring. Error: {e}")
            
            # Check for Work Eligibility
            try:
                # Wait for the 'Work Eligibility' section for up to 60 seconds
                page.wait_for_selector("h2:has-text('Work Eligibility')", timeout=10000)  # Timeout set to 60 seconds
                # If the element is found within the timeout, perform Action for Work Eligibility
                print("Element found! Performing Action for Work Eligibility...")
                handle_scenario_b(page)
            except Exception as e:
                # If element is not found in time, ignore
                print(f"Work Eligibility page not found within timeout. Ignoring. Application is not successful. Error: {e}")
            try:
                page.wait_for_selector('h1.submission-complete.display-2.d-inline-block:has-text("Next steps of your application")', timeout=60000)
                print("Successful!")
                mark_job_as_applied('Amazon', data_id, 1)
                print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Update the applied status in your record')

            except Exception as e:
                print(f"Error: {e}")
            # mark successful
        except TimeoutError:
            print("Timed out waiting for the 'DESCRIPTION' header.")
        

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")



def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs('Amazon')
    if not jobs:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No unprocessed jobs found.")
        return

    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found {len(jobs)} unprocessed jobs.")
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
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
