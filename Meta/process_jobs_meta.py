# main.py
import os
import sys
from datetime import datetime
import time
from playwright.sync_api import sync_playwright
from log_in_meta import log_in  # Assuming log_in is correctly implemented and imported

# Add the upper directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_operations import get_unprocessed_jobs, mark_job_as_applied
from human_scroll import human_scroll
SLEEP_MULTIPLE = 5
# List of states (full names) to select
STATES_TO_SELECT = [
    "California", "New York", "Massachusetts", "Washington", 
    "Georgia", "Texas"
]

# Education details for each group
EDUCATION_INFO = [
    {
        "university_name": "New York Institute of Tech",
        "select_option": "New York Institute of Technology",
        "degree": "Masters",
        "concentration": "Cybersecurity"
    },
    {
        "university_name": "Macau",
        "select_option": "University of Macau",
        "degree": "Masters",
        "concentration": "Electrical and Computer Engineering"
    },
    {
        "university_name": "Dalian Maritime",
        "select_option": "Dalian Maritime University",
        "degree": "Bachelors",
        "concentration": "Electrical Engineering and Automation"
    }
]

def fill_education_fields(page):
    for idx, edu in enumerate(EDUCATION_INFO):
        # College/University Name
        university_input = page.locator(f"input[placeholder='College/University Name']").nth(idx)
        university_input.fill(edu["university_name"])
        
        # Wait for the dropdown to appear and select the option
        page.locator(f"li[aria-label='{edu['select_option']}']").click()

        # Degree selection
        degree_selector = page.locator("select:has(option[value])").nth(idx)
        degree_selector.select_option(value=edu["degree"])

        # Concentration
        concentration_input = page.locator("input[placeholder='Concentration']").nth(idx * 2)
        concentration_input.fill(edu["concentration"])

        # Add another degree if it's not the last iteration
        if idx < len(EDUCATION_INFO) - 1:
            add_another_degree_button = page.locator("button:has-text('Add Another Degree')")
            add_another_degree_button.click()

def select_radio_option(page, question_text, answer_text='Yes'):
    # Helper function to escape single quotes in XPath expressions
    def escape_xpath_text(s):
        if "'" in s:
            # Escape single quotes in XPath strings
            parts = s.split("'")
            return "concat(" + ",\"'\",".join(f"'{part}'" for part in parts) + ")"
        else:
            return f"'{s}'"

    # Escape the question and answer texts for XPath
    question_text_xpath = escape_xpath_text(question_text.strip())
    answer_text_xpath = escape_xpath_text(answer_text.strip())

    # Locate the div containing the question text
    question_div_xpath = f"//div[normalize-space(text())={question_text_xpath}]"
    question_div = page.query_selector(f"xpath={question_div_xpath}")
    if not question_div:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Question not found: {question_text}")
        return

    # From the question div, get the parent div that contains both the question and the options
    question_container_xpath = ".//ancestor::div[1]"
    question_container = question_div.evaluate_handle("node => node.parentElement")
    if not question_container:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Question container not found for question: {question_text}")
        return

    # Within the question container, find the radio input with the desired answer text
    input_xpath = (
        f".//input[@type='radio' and following-sibling::span[normalize-space(text())={answer_text_xpath}]]"
    )
    radio_input = question_container.query_selector(f"xpath={input_xpath}")
    if radio_input:
        radio_input.click()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Selected '{answer_text}' for question: {question_text}")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Radio input not found for answer '{answer_text}' and question '{question_text}'")

def select_state(page, state_name):
    # Selector for the state/province input field
    state_input_selector = "input[aria-label='State/Province']"
    
    # Check if the state input field exists
    if page.query_selector(state_input_selector):
        # Type the state name into the input field
        page.fill(state_input_selector, state_name)
        
        # Wait for the option to appear in the dropdown
        option_selector = f"li[aria-label='{state_name}']"
        page.wait_for_selector(option_selector, timeout=3000)  # Adjust timeout if needed
        
        # Select the state option if it appears
        if page.query_selector(option_selector):
            page.click(option_selector)
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Option '{state_name}' not found.")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - State input field not found, skipping.")

def process_job_link(data_id, link, page, context):
    """Process a job link: check if applied, and apply if not."""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Processing job {data_id}...")
        time.sleep(SLEEP_MULTIPLE * 10)
        page.goto(link)
        time.sleep(SLEEP_MULTIPLE * 10)
        try:
            # Attempt to locate and click the misusing Close button
            close_button = page.query_selector("a:has-text('Close')")
            if close_button:
                close_button.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked the 'Close' button.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 'Close' button not found, ignoring.")
                if page.is_visible("text=This page is no longer available"):
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Page is no longer available. Marking job as applied.")
                    # Call the function to mark the job as applied
                    mark_job_as_applied('Meta', data_id, 2)
        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error occurred while trying to click 'Close' button: {e}")
        human_scroll(page)
        # Check for the block message
        if page.query_selector("h1:has-text('You’re Temporarily Blocked')"):
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Temporarily blocked, sleeping for 30 minutes...")
            time.sleep(SLEEP_MULTIPLE * 30 * 60)  # Sleep for 30 minutes
            return  # Exit the process_job_link function
        # Wait for the div with aria-label="Career Profile Account"
        page.wait_for_selector('div[aria-label="Career Profile Account"]')


        # Find all "Apply to this job" buttons
        apply_buttons = page.query_selector_all("a:has-text('Apply to this job')")
        time.sleep(SLEEP_MULTIPLE * 15)
        # Click the first button if it exists
        if apply_buttons:
            # Use expect_page to handle the new tab that opens upon clicking the job post
            with context.expect_page() as new_page_info:
                apply_buttons[1].click()
            # Get the new page that opened
            resume_page = new_page_info.value
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New page stored in resume_page.")
            time.sleep(SLEEP_MULTIPLE * 15)
            # Select all checkbox inputs and check them
            checkboxes = resume_page.query_selector_all("input[type='checkbox']")
            human_scroll(resume_page)
            for checkbox in checkboxes:
                if not checkbox.is_checked():
                    checkbox.check()  # Check the checkbox if it is not already checked
            
            
            # Selector for the country input field
            country_input_selector = "input[aria-label='Country'][placeholder='Country']"
            
            # Check if the country input field exists
            if resume_page.query_selector(country_input_selector):
                # Type 'United States' into the country input field
                resume_page.fill(country_input_selector, "United States")
                
                # Wait for the 'United States' option to appear in the dropdown
                option_selector = "li[aria-label='United States']"
                resume_page.wait_for_selector(option_selector, timeout=3000)  # Adjust timeout if needed
                
                # Select the 'United States' option if it appears
                if resume_page.query_selector(option_selector):
                    resume_page.click(option_selector)
                    time.sleep(2 * SLEEP_MULTIPLE)
                    # Loop through each state and select it
                    for state in STATES_TO_SELECT:
                        select_state(resume_page, state)
                        time.sleep(1 * SLEEP_MULTIPLE)
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Option 'United States' not found.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Country input field not found, skipping.")
            
            
            input_selector = 'input[name="availableStartMonth"][placeholder="(MM/YYYY)"]'
    
            # Locate the input field
            input_field = resume_page.query_selector(input_selector)

            if input_field:
                # Clear any existing text in the input field
                input_field.fill("")
                # Input "02/2025"
                input_field.fill("02/2025")
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Entered '02/2025' into the input field.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Input field 'availableStartMonth' not found.")
            
            
            # Wait for the 'Next' button to be visible
            time.sleep(SLEEP_MULTIPLE * 10)

            questions_and_answers = [
                {
                    "question": "If hired, can you produce acceptable evidence of your identity and authorization to work in the United States on your first date of employment?",
                    "answer": "Yes"
                },
                {
                    "question": "If hired, will you need immigration assistance or sponsorship from Meta to begin or, at any time in the future, to continue to work lawfully for Meta in the United States? This includes any need to transfer/extend a current non-immigrant visa status, change non-immigrant status, renew a work permit/EAD card, or assistance with applying for a United States green card.",
                    "answer": "No"
                }
            ]

            # Loop through each question and select the appropriate option
            for qa in questions_and_answers:
                select_radio_option(resume_page, qa["question"], qa["answer"])
                # Add a short delay if necessary
                time.sleep(1)


            human_scroll(resume_page)
            resume_page.wait_for_selector("a:has-text('Next')")
            # Click the 'Next' button
            resume_page.click("a:has-text('Next')")
            time.sleep(SLEEP_MULTIPLE * 15)
            human_scroll(resume_page)
            input_selector = "input[placeholder='College/University Name']"
            # Get the 'value' attribute of the input field
            college = resume_page.locator(input_selector).first.get_attribute("value")
            if not college:  # If 'college' is empty
                print("College input field is empty, trying to input.")
                fill_education_fields(resume_page)
            else:
                print("College input field is not empty, ignoring.")



            # Wait for the 'Next' button to be visible
            resume_page.wait_for_selector("a:has-text('Next')")
            # Click the 'Next' button
            resume_page.click("a:has-text('Next')")
            time.sleep(SLEEP_MULTIPLE * 15)
            human_scroll(resume_page)
            # Wait for the 'Next' button to be visible
            resume_page.wait_for_selector("a:has-text('Next')")
            # Click the 'Next' button
            resume_page.click("a:has-text('Next')")
            time.sleep(SLEEP_MULTIPLE * 15)
            human_scroll(resume_page)
            # Wait for the 'Next' button to be visible
            resume_page.wait_for_selector("a:has-text('Next')")
            # Click the 'Next' button
            resume_page.click("a:has-text('Next')")
            time.sleep(SLEEP_MULTIPLE * 15)
            human_scroll(resume_page)
            # Wait for the button to be visible
            resume_page.wait_for_selector("#appSubmitButton")
            # Click the button
            resume_page.click("#appSubmitButton")
            time.sleep(SLEEP_MULTIPLE * 20)
            human_scroll(resume_page)
            resume_page.wait_for_selector('div[aria-label="Career Profile Account"]')
            # Check for the specific h2 element containing the text
            if resume_page.query_selector("h2:has-text('Thanks for applying')"):
                # Update the applied status in your record
                mark_job_as_applied('Meta', data_id, 1)
                print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Update the applied status in your record')
            resume_page.close()
            time.sleep(SLEEP_MULTIPLE * 10)
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No 'Apply to this job' buttons found.")
        # Wait for the checkbox elements to be present

        time.sleep(SLEEP_MULTIPLE * 10)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error processing job {data_id}: {e}")



def main():
    """Main function to process all unprocessed jobs."""
    jobs = get_unprocessed_jobs('Meta')
    if not jobs:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No unprocessed jobs found.")
        return

    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Found {len(jobs)} unprocessed jobs.")
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        # browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        # Log in
        log_in(page)

        # Process each job
        for data_id, link in jobs:
            process_job_link(data_id, link, page, context)

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}")
    finally:
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    main()
