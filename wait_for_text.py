def wait_for_text(page, text, cooling_factor=1):
    try:
        page.wait_for_selector(f"* :has-text('{text}')", timeout=cooling_factor * 10000)
        print(f"Found an element containing the text: '{text}' outside iframe.")
        return True
    except Exception as e:
        # If the element isn't in an iframe, search in the main page context
        try:
            # Try locating the iframe and get the frame context
            iframe_element = page.locator('iframe')  # Adjust the selector if necessary
            iframe = iframe_element.frame()  # Switch to the iframe context
            
            # Wait for the element inside the iframe containing the specified text
            iframe.wait_for_selector(f"* :has-text('{text}')", timeout=cooling_factor * 10000)
            print(f"Found an element containing the text: '{text}' inside iframe.")
            return True
        except Exception as e:
            from datetime import datetime
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error waiting for element containing text '{text}': {e}")
            return False
