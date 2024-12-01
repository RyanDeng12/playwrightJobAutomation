# db_operations.py
import os
import sqlite3
from datetime import datetime
# Database path
DB_PATH = os.path.join(os.getcwd(), 'jobs.db')

UNDESIRED = ['phd', 'principal', 'soc ', 'silicon', 'designer', 'mba', 'lead', 'director', 'head']
DESIRED = []

def contains_any(string):
    return any(word in string.lower() for word in UNDESIRED) and not any(word in string.lower() for word in DESIRED)

# Insert job data into the database with deduplication
def insert_job(company_name, job_title, data_id, link):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    # Desired words and undesired words
    if contains_any(job_title):
        application_status = 4
    else:
        application_status = 0
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO job_posts (company_name, job_title, data_id, link, applied) 
            VALUES (?, ?, ?, ?, ?)
        ''', (company_name, job_title, data_id, link, application_status))
        conn.commit()
    except sqlite3.Error as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SQLite Error: {e}")
    finally:
        conn.close()

def get_unprocessed_jobs(company_name):
    """Fetch all jobs where 'applied' is 0 for the specified company."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data_id, link From job_posts WHERE applied = 0 AND company_name = ? ORDER BY CREATE_DATE DESC', (company_name,))
        # cursor.execute('SELECT data_id, link From job_posts WHERE applied = 0 AND company_name = ? AND DATE(create_date) = "2024-11-02" ORDER BY CREATE_DATE DESC', (company_name,))
        return cursor.fetchall()

def mark_job_as_applied(company_name, data_id, applied_status):
    """Mark a job as applied in the database for the specified company."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('Update job_posts SET applied = ? WHERE company_name = ? AND data_id = ?', (applied_status, company_name, data_id))
        conn.commit()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Job {data_id} marked as applied.")
