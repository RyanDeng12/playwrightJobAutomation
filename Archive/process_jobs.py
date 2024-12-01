import os
import time
import sqlite3
from playwright.sync_api import sync_playwright
from log_in import log_in  # Assuming log_in is correctly implemented and imported

# Database path
DB_PATH = os.path.join(os.getcwd(), 'jobs.db')

def get_unprocessed_jobs():
    """Fetch all jobs where 'applied' is 0."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data_id, link From job_posts WHERE applied = 0 and company_name = "TikTok"')
        return cursor.fetchall()

def mark_job_as_applied(data_id):
    """Mark a job as applied in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('Update job_posts SET applied = 1 WHERE company_name = "TikTok" AND data_id = ?', (data_id,))
        conn.commit()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Job {data_id} marked as applied.")

def select_option(page, dropdown_xpath, option_text):
    """Select an option from a dropdown."""
    try:
        dropdown = page.wait_for_selector(dropdown_xpath, timeout=60000)
        dropdown.click()
        page.wait_for_timeout(1000)  # Wait for the dropdown to expand

        option_xpath = f'//div[contains(@class, "ud__select__list__item") and .//span[text()="{option_text}"]]'
        option = page.wait_for_selector(option_xpath, timeout=60000)
        option.click()

        print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Selected "{option_text}" option.')

        # Close the dropdown by clicking the form label to collapse it
        page.mouse.click(0, 0)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error selecting {option_text}: {e}")

def fill_survey(page):
    """Fill out the demographic survey."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Filling demographic survey...")

        # Gender dropdown
        gender_dropdown_xpath = (
            '//*[@id="bd"]/section/section/main/div/div[1]/div/div/div/div[1]/form/div[13]/div/div[2]/div/div/div[1]/div/form/div/div[2]/div/div[1]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]'
        )
        select_option(page, gender_dropdown_xpath, "Man")

        # Race/Ethnicity dropdown
        race_dropdown_xpath = (
            '//*[@id="bd"]/section/section/main/div/div[1]/div/div/div/div[1]/form/div[13]/div/div[2]/div/div/div[1]/div/form/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]'
        )
        select_option(page, race_dropdown_xpath, "Asian")

        # Sponsorship dropdown
        sponsorship_dropdown_xpath = (
            '//*[@id="bd"]/section/section/main/div/div[1]/div/div/div/div[1]/form/div[14]/div/div[2]/div/div/div[1]/div/form/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[1]/div[1]'
        )
        select_option(page, sponsorship_dropdown_xpath, "No")

        # Legality dropdown
        legality_dropdown_xpath = (
            '//*[@id="bd"]/section/section/main/div/div[1]/div/div/div/div[1]/form/div[14]/div/div[2]/div/div/div[1]/div/form/div/div[2]/div/div[1]/div[2]/div/div/div/div/div[1]/div[1]'
        )
        select_option(page, legality_dropdown_xpath, "Yes")

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Demographic survey completed.")
        time.sleep(1)  # Give time for changes to take effect
        return True

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error filling demographic survey: {e}")
        return False

def process_job_link(data_id, link, page):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        page.goto(link)
        page.wait_for_selector('span.job-title', timeout=60000)

        # Check if the job has already been applied
        if page.query_selector('span.AppliedTag[data-test="appliedTag"]'):
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Job {data_id} has already been applied.")
            mark_job_as_applied(data_id)
        else:                               
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Applying to job {data_id}...")
            apply_button = page.query_selector(
                'button.atsx-btn.apply-block-applyBtn.atsx-btn-primary.atsx-btn-lg'
            )
            if apply_button:
                apply_button.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Apply' button.")

                # Wait for 'Submit' button to appear and complete the survey
                page.wait_for_selector('button[data-test="applyResumeBtn"]', timeout=60000)
                submit_button = page.query_selector('button[data-test="applyResumeBtn"]')
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Submit button found. Proceeding with the survey...")
                if fill_survey(page):
                    submit_button.click()
                    received_message = page.wait_for_selector('div.received.sofiaBold', timeout=60000)
                    if received_message and "We have received your resume." in received_message.inner_text():
                        mark_job_as_applied(data_id)  # Mark job as applied
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully processed job: {link}")
                    else:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Application failed for {data_id}.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Apply button not found for job {data_id}.")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")

def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs()
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
            process_job_link(data_id, link, page)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}")
    finally:
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    main()
