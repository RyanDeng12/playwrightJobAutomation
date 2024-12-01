def extract_links(page, url_pattern):
    import re
    # Define the regex pattern to match the links starting with "/en-us/details/"
    # Get the page content
    content = page.content()
    # Use regex to find all matching URLs starting with "/en-us/details/"
    links = re.findall(url_pattern, content)
    unique_links = set(links)
    # Print all the matching links
    for link in unique_links:
        print(link)
    return unique_links

