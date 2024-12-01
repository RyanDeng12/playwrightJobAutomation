import time
from datetime import datetime
def human_scroll(page, cooling_factor=1, distance=100, delay=0.5):
    while True:
        # Get the current scroll position
        current_scroll = page.evaluate("window.scrollY")
        # Get the total height of the document
        document_height = page.evaluate("document.body.scrollHeight")
        # Get the height of the viewport
        viewport_height = page.evaluate("window.innerHeight")

        # Scroll down
        if current_scroll + viewport_height >= document_height - 3:  # At bottom
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reached bottom, finishing...")
            break  # Exit the loop
        else:
            page.mouse.wheel(0, distance/cooling_factor)
            # print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scrolling down...")

        time.sleep(delay)  # Wait for a bit to simulate human behavior