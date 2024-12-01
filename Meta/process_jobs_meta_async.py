# main.py
import os
import sys
import time
from datetime import datetime
from playwright.async_api import async_playwright
from log_in_meta import log_in  # Ensure this is an async function
import asyncio
# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied
from human_scroll import human_scroll  # Ensure this is an async function
SLEEP_MULTIPLE = 1

async def process_job_link(data_id, link, page, context):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        await asyncio.sleep(SLEEP_MULTIPLE * 10)
        await page.goto(link)
        await asyncio.sleep(SLEEP_MULTIPLE * 10)
        try:
            # Attempt to locate and click the 'Close' button
            close_button = await page.query_selector("a:has-text('Close')")
            if close_button:
                await close_button.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked the 'Close' button.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 'Close' button not found, ignoring.")
        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error occurred while trying to click 'Close' button: {e}")
        await human_scroll(page)
        # Check for the block message
        if await page.query_selector("h1:has-text('You’re Temporarily Blocked')"):
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Temporarily blocked, sleeping for 30 minutes...")
            await asyncio.sleep(SLEEP_MULTIPLE * 30 * 60)  # Sleep for 30 minutes
            return  # Exit the process_job_link function
        # Wait for the div with aria-label="Career Profile Account"
        await page.wait_for_selector('div[aria-label="Career Profile Account"]')

        # Find all "Apply to this job" buttons
        apply_buttons = await page.query_selector_all("a:has-text('Apply to this job')")
        await asyncio.sleep(SLEEP_MULTIPLE * 15)
        # Click the first button if it exists
        if apply_buttons:
            # Use expect_page to handle the new tab that opens upon clicking the job post
            async with context.expect_page() as new_page_info:
                await apply_buttons[1].click()
            # Get the new page that opened
            resume_page = await new_page_info.value
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New page stored in resume_page.")
            # Wait for the location checkbox elements to be present
            await resume_page.wait_for_selector("input[type='checkbox']")
            # Select all checkbox inputs and check them
            checkboxes = await resume_page.query_selector_all("input[type='checkbox']")
            await asyncio.sleep(SLEEP_MULTIPLE * 15)
            await human_scroll(resume_page)
            for checkbox in checkboxes:
                if not await checkbox.is_checked():
                    await checkbox.check()  # Check the checkbox if it is not already checked
            # Wait for the 'Next' button to be visible
            await asyncio.sleep(SLEEP_MULTIPLE * 10)
            await human_scroll(resume_page)
            await resume_page.wait_for_selector("a:has-text('Next')")
            # Click the 'Next' button
            await resume_page.click("a:has-text('Next')")
            await asyncio.sleep(SLEEP_MULTIPLE * 15)
            await human_scroll(resume_page)
            # Repeat the above steps for subsequent 'Next' buttons
            for _ in range(3):
                await resume_page.wait_for_selector("a:has-text('Next')")
                await resume_page.click("a:has-text('Next')")
                await asyncio.sleep(SLEEP_MULTIPLE * 15)
                await human_scroll(resume_page)
            # Wait for the 'Submit' button to be visible
            await resume_page.wait_for_selector("#appSubmitButton")
            # Click the 'Submit' button
            await resume_page.click("#appSubmitButton")
            await asyncio.sleep(SLEEP_MULTIPLE * 20)
            await human_scroll(resume_page)
            await resume_page.wait_for_selector('div[aria-label="Career Profile Account"]')
            # Check for the specific h2 element containing the text
            if await resume_page.query_selector("h2:has-text('Thanks for applying')"):
                # Update the applied status in your record
                mark_job_as_applied('Meta', data_id, 1)
                print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Updated the applied status in your record')
            await resume_page.close()
            await asyncio.sleep(SLEEP_MULTIPLE * 10)
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No 'Apply to this job' buttons found.")
        # Wait for the checkbox elements to be present

        await asyncio.sleep(SLEEP_MULTIPLE * 10)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")

async def main():
    """Main function to process all unprocessed jobs."""
    jobs =  get_unprocessed_jobs('Meta')
    if not jobs:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No unprocessed jobs found.")
        return

    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found {len(jobs)} unprocessed jobs.")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            # Log in
            await log_in(page)

            # Process each job
            for data_id, link in jobs:
                await process_job_link(data_id, link, page, context)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}")
    finally:
        await browser.close()

asyncio.run(main())
