# main.py
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from log_in_msft import log_in  # Assuming log_in is correctly implemented and imported

# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied

def process_job_link(data_id, link, page, browser):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        page.goto(link)
        page.wait_for_selector('label[for="Qualification_Consent"]')
        checkbox_container0 = page.query_selector('label[for="Qualification_Consent"]')
        checkbox_container1 = page.query_selector('label[for="DPN_Consent"]')
        checkbox_container0.click()
        checkbox_container1.click()
        time.sleep(3)
        save_and_continue_button = page.wait_for_selector("span.ms-Button-label.label-76:has-text('Save and continue')")
        save_and_continue_button.click()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Save and continue' button.")
        immigration_dropdown = page.locator('//*[@id="isImmigrationBenefitEligible-option"]')
        immigration_dropdown.click()  # Open the dropdown
        time.sleep(1)
        page.locator('//*[@id="isImmigrationBenefitEligible-list1"]/span').click()  # Select "No"
        # Select 'Yes' for the legal authorization question
        legal_authorization_dropdown = page.locator('//*[@id="isLegallyAuthorized-option"]')
        legal_authorization_dropdown.click()  # Open the dropdown
    
        time.sleep(1)
        page.locator('//*[@id="isLegallyAuthorized-list0"]/span').click() # Locate and select 'Yes'
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Selected 'Yes' for legal authorization.")
        time.sleep(1)
        page.locator('//*[@id="apply-appaction"]/div/div/div/div[2]/div[2]/div[2]/button[2]').click()
        time.sleep(3)
        # Wait for the button to be visible
        page.wait_for_selector('button#save65', state='visible', timeout=10000)
        # Locate the button
        save_button = page.query_selector('button#save65')
        if save_button:
            # Ensure the button is enabled
            if not save_button.is_disabled():
                # Scroll into view if necessary
                save_button.scroll_into_view_if_needed()
                # Click the button
                save_button.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked the 'Save and continue' button.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Button is disabled.")
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Button not found.")
        time.sleep(1)
        # Access iframe as before
        page.wait_for_selector('iframe#icims_content_iframe')
        iframe_element = page.query_selector('iframe#icims_content_iframe')
        iframe = iframe_element.content_frame()

        if iframe is not None:
            # Now click the submit button
            iframe.wait_for_selector('#quesp_form_submit_i', state='visible')
            button = iframe.query_selector('#quesp_form_submit_i')
            if button and not button.is_disabled():
                button.scroll_into_view_if_needed()
                button.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Form submitted successfully.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Submit button is disabled or not found.")

        # Job Specific Questions
        # Wait for the iframe to load
        page.wait_for_selector('iframe#icims_content_iframe')
        time.sleep(1)
        # Get the iframe element
        iframe_element = page.query_selector('iframe#icims_content_iframe')
        time.sleep(1)
        # Access the iframe's content frame
        iframe = iframe_element.content_frame()
        time.sleep(1)
        if iframe is not None:
            # Wait for any select elements to be available inside the iframe
            iframe.wait_for_selector('select', timeout=10000)
            time.sleep(2)

            # Get all select elements
            select_elements = iframe.query_selector_all('select')
            time.sleep(1)
            # Iterate over each select element
            for select_element in select_elements:
                # Get all option values
                options = select_element.query_selector_all('option')
                option_values = [
                    option.get_attribute('value').strip() if option.get_attribute('value') else ''
                    for option in options
                ]

                # Check if "Yes" and "No" are options (indicates a question)
                if 'Yes' in option_values and 'No' in option_values:
                    # Select "Yes"
                    select_element.select_option("Yes")
                    time.sleep(1)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Selected 'Yes' for select element with id {select_element.get_attribute('id')}")
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Skipping select element with id {select_element.get_attribute('id')}")

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Selected 'Yes' for all applicable questions.")

            # Optionally, click the submit button
            submit_button = iframe.query_selector('#quesp_form_submit_i')
            if submit_button and not submit_button.is_disabled():
                submit_button.click()

                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked the submit button.")
                # Check for the success message
                try:
                    # Wait for the success message to appear
                    page.wait_for_selector('div.ms-apply-thank-you-content', timeout=30003)
                    # Confirm the message is as expected
                    success_message = page.query_selector('div.ms-apply-thank-you-content h1')
                    if success_message:
                        text = success_message.text_content().strip()
                        if "Your application has been submitted" in text:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Application submitted successfully.")
                            mark_job_as_applied('Microsoft', data_id, 1)
                        else:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Success message not as expected.")
                        time.sleep(10)
                    else:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Success message not found.")
                except Exception as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error while checking for the success message: {e}")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Submit button not found or is disabled.")
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Could not access the iframe.")

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")



def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs('Microsoft')
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
