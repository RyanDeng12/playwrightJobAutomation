def input_text_by_id(page, id, text):
    try:
        # Wait for the element to appear before filling it
        page.wait_for_selector(f'#{id}', timeout=30000)  # Wait for up to 30 seconds
        page.fill(f'#{id}', text)  # Fill the input field
        print(f"Input text outside in a iframe: {text}")
    except:
        try:
            # Locate the iframe (example, adjust selector accordingly)
            iframe_element = page.locator('iframe')  # Or use specific selector for iframe
            iframe = iframe_element.element_handle().content_frame() # Get the frame context from the element handle

            # Wait for the input field inside the iframe to be available
            iframe.wait_for_selector(f'#{id}', timeout=30000)
            iframe.fill(f'#{id}', text)  # Fill the input field
            print(f"Input text in a iframe: {text}")
        except:
            from datetime import datetime
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error inputing into id:{id} field even in any iframe.: {e}")