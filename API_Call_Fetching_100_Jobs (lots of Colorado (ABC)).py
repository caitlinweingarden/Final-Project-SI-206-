import requests
import unittest
import sqlite3
import json
import os
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

# Set your credentials
USER_AGENT = "caitliw@umich.edu"         # The email you used to sign up
API_KEY =  os.getenv("API_KEY")        # Your USAJOBS API Key

db_name = 'usajobs.db'









#copy after this line!!!!

valid_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": USER_AGENT,
    "Authorization-Key": API_KEY
}

# DB setup
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + "/" + db_name)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS Jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        organization TEXT NOT NULL,
        location TEXT NOT NULL
    )
''')
cur.execute('DELETE FROM Jobs')
conn.commit()

# Data fetching loop
clean_jobs_inserted = 0
max_jobs = 100

for state in valid_states:
    if clean_jobs_inserted >= max_jobs:
        break

    print(f"\n🔍 Searching jobs in {state}...")
    page = 1

    while True:
        if clean_jobs_inserted >= max_jobs:
            break

        url = "https://data.usajobs.gov/api/search"
        params = {
            "Keyword": "Software",
            "LocationName": state,
            "ResultsPerPage": 50,
            "Page": page
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f" Error for {state} page {page}: {response.status_code}")
            break

        data = response.json()
        results = data.get("SearchResult", {}).get("SearchResultItems", [])

        if not results:
            break

        for job in results:
            descriptor = job.get("MatchedObjectDescriptor", {})
            title = descriptor.get("PositionTitle", "N/A")
            organization = descriptor.get("OrganizationName", "N/A")
            job_location = descriptor.get("PositionLocationDisplay", "")

            # Skip if job location is vague
            skip_keywords = ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]
            if any(word.lower() in job_location.lower() for word in skip_keywords):
                continue

            # Extract state portion of location
            if "," in job_location:
                *_, last_part = [p.strip() for p in job_location.split(",")]
                if last_part not in valid_states:
                    continue
            else:
                continue

            cur.execute('''
                INSERT INTO Jobs (title, organization, location)
                VALUES (?, ?, ?)
            ''', (title, organization, job_location))

            clean_jobs_inserted += 1
            print(f"✅ {clean_jobs_inserted}. {title} | {job_location}")

            if clean_jobs_inserted >= max_jobs:
                break

        page += 1

conn.commit()
conn.close()

print(f"\n🎉 Done! {clean_jobs_inserted} jobs with clear state locations added to the database.")








