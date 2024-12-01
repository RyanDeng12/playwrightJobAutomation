import asyncio
from playwright.async_api import async_playwright
from Archive.log_in_msft_async import log_in  # Assuming log_in is correctly implemented and imported

async def test_playwright_on_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Log in and maintain the session
        page = await log_in(page)
        
        try:
            # Step 1: Open the test URL using the same logged-in page
            await page.goto(url)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Page loaded successfully.")

            # Step 2: Check if we can access the URL and print it
            current_url = page.url
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Current URL: {current_url}")

            # Step 3: Test for a common element like the body tag to ensure page is loaded
            if await page.locator("body").is_visible():
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Body tag found and visible.")

            # Step 4: Interact with an input field (if available) to ensure Playwright can send keystrokes
            input_fields = page.locator("input[type='text']")
            if await input_fields.count() > 0:
                await input_fields.first.fill("Playwright test")
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully filled text in the first input field.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No input field found to interact with.")

            # Step 5: Try finding and clicking a button (if available)
            buttons = page.locator("button")
            if await buttons.count() > 0:
                await buttons.first.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully clicked the first button.")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No button found to interact with.")

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - An error occurred while testing the page: {e}")
        
        finally:
            await browser.close()

# Usage

asyncio.run(test_playwright_on_page("https://industryuseng-ms.icims.com/jobs/1675865/principal-software-engineer/questions?global=1&mobile=false&width=1152&height=500&bga=true&needsRedirect=false&jan1offset=480&jun1offset=480"))
