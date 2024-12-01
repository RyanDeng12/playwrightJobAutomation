def extract_job_details(url, pattern):
    import re
    # Use regex to extract job_id and title
    match = re.search(pattern, url)
    
    if match:
        job_id = match.group(1)  # Extract job ID
        title = match.group(2)   # Extract title
        return job_id, title
    else:
        return None, None