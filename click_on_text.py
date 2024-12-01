def click_on_text(targeted_text, page):
    # Find all elements containing the text (case-sensitive)
    elements = page.locator('*')  # Search all elements on the page
    matching_element = None

    # Loop through each element and check if its inner text matches the targeted text case-sensitively
    count = elements.count()
    for i in range(count):
        element = elements.nth(i)
        
        try:
            # Check if the element is an HTMLElement and has inner text
            if element.is_visible():
                element_text = element.inner_text()
                if element_text == targeted_text:  # Case-sensitive match
                    matching_element = element
                    break
        except Exception as e:
            # Handle error for non-HTML elements gracefully
            # print(f"Skipping non-HTML element at index {i}: {e}")
            pass

    if matching_element:
        matching_element.click()
        print(f"Clicked the element with the exact case-sensitive text: '{targeted_text}'")
        return True
    else:
        print(f"No element with the exact text '{targeted_text}' found.")
    return False