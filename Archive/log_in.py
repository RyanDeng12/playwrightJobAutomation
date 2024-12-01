from playwright.sync_api import sync_playwright, Page
def log_in(page):
    URL = 'https://careers.tiktok.com/login'
    page.goto(URL, timeout=600000)
    """Automate login process on the page."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logging in...")

    try:
        page.wait_for_selector('#email', timeout=60000)
        page.fill('#email', '375797869@qq.com')

        page.wait_for_selector('#password', timeout=60000)
        page.fill('#password', 'AZsxDCfvGBhn321a')

        checkbox = page.wait_for_selector('input.atsx-checkbox-input', timeout=60000)
        checkbox.check()

        if not page.is_checked('input.atsx-checkbox-input'):
            raise Exception('Checkbox not checked')

        sign_in_button = page.wait_for_selector('button[data-test="signInBtn"]', timeout=60000)
        sign_in_button.click()
        page.wait_for_selector('span.topbar-userMobile.topbar-userMobile-transparent.atsx-dropdown-trigger')  # Small delay for login
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Log in clicked successfully.")
    except Exception as e:
        raise Exception('Error during the login process') from e