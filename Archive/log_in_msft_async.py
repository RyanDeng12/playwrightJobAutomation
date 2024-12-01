from playwright.async_api import async_playwright, Page
import asyncio

async def log_in(page: Page):
    try:
        # Step 1: Go to Microsoft Careers home page and log in
        URL = 'https://careers.microsoft.com/v2/global/en/home.html'
        await page.goto(URL, wait_until="networkidle", timeout=120000)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Navigating to login page...")

        # Step 2: Click 'Sign in' button on the main page
        sign_in_div = await page.wait_for_selector('div.msame_Header_name.st_msame_placeholder', timeout=10000)
        await sign_in_div.click()

        # Step 3: Choose 'Sign in with Microsoft' on the login page
        await page.wait_for_selector('div[aria-label="Sign in with Microsoft"]', timeout=60000)
        await page.get_by_label('Sign in with Microsoft').click()

        # Step 4: Enter credentials
        await page.get_by_label("Enter your email, phone, or Skype.").fill("375797869@qq.com")
        await page.get_by_role("button", name="Next").click()
        await page.get_by_label("Password").fill("!AZsxDCfvGBhn321c")
        await page.locator("#idSIButton9").click()

        # Step 5: Confirm sign-in if prompted
        await page.wait_for_selector("#acceptButton", timeout=10000)
        await page.locator("#acceptButton").click()

        # Step 6: Verify successful login by checking for user profile icon
        await page.wait_for_selector('#mectrl_headerPicture', timeout=10000)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Login successful.")

        # Step 7: Navigate to job page
        job_url = 'https://jobs.careers.microsoft.com/global/en/job/1776808'
        await page.goto(job_url, wait_until="networkidle")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Navigated to job page.")

        # Step 8: Handle additional sign-in if prompted on job page
        try:
            sign_in_div = await page.wait_for_selector('div.msame_Header_name.st_msame_placeholder', timeout=10000)
            await sign_in_div.click()
            await page.wait_for_selector('div[aria-label="Sign in with Microsoft"]', timeout=60000)
            await page.get_by_label('Sign in with Microsoft').click()
            await page.wait_for_selector('#mectrl_headerPicture', timeout=30000)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Secondary login completed on job page.")
            return page
        except Exception:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No additional login required on job page.")

    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error during the login process: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await log_in(page)
        # await browser.close()

# Run the main function
asyncio.run(main())
