def click_by_id(page, id, cooling_factor=1):
    try:
        # Wait for the element to appear before clicking it
        page.wait_for_selector(f'#{id}', timeout=cooling_factor * 10000)  # Adjust timeout based on cooling_factor
        page.click(f'#{id}')  # Click the element with the given ID
        print(f"Clicked element with ID: {id} outside of an iframe.")
    except Exception as e:
        try:
            # Locate the iframe (adjust selector if needed)
            iframe_element = page.locator('iframe')  # Or use a more specific selector for the iframe
            iframe = iframe_element.element_handle().content_frame()  # Get the frame context from the element handle

            # Wait for the element inside the iframe to be available
            iframe.wait_for_selector(f'#{id}', timeout=cooling_factor * 10000)
            iframe.click(f'#{id}')  # Click the element inside the iframe
            print(f"Clicked element with ID: {id} inside an iframe.")
        except Exception as e:
            from datetime import datetime
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error clicking on id:{id} field, even inside an iframe: {e}")
