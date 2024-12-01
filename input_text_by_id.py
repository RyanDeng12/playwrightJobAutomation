def input_text_by_id(page, id, text, cooling_factor=1):
    try:
        # Wait for the element to appear before filling it
        page.wait_for_selector(f'#{id}', timeout=cooling_factor * 10000)  # Fixed parenthesis issue
        page.fill(f'#{id}', text)  # Fill the input field
        print(f"Input text outside an iframe: {text}")
    except Exception as e:
        try:
            # Locate the iframe (example, adjust selector accordingly)
            iframe_element = page.locator('iframe')  # Or use a more specific selector for the iframe
            iframe = iframe_element.element_handle().content_frame()  # Get the frame context from the element handle

            # Wait for the input field inside the iframe to be available
            iframe.wait_for_selector(f'#{id}', timeout=cooling_factor * 10000)
            iframe.fill(f'#{id}', text)  # Fill the input field
            print(f"Input text in an iframe: {text}")
        except Exception as e:
            from datetime import datetime
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error inputting into id:{id} field, even in any iframe: {e}")

