import requests
import unittest
import sqlite3
import json
import os
from dotenv import load_dotenv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
load_dotenv()  # Loads variables from .env

# Set your credentials
USER_AGENT = "caitliw@umich.edu"         # The email you used to sign up
API_KEY =  os.getenv("API_KEY")        # Your USAJOBS API Key

db_name = 'usajobs.db'

batch_size = 25

# Use current working directory instead of __file__
path = os.getcwd()
db_path = os.path.join(path, db_name)

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

# === DB setup ===
path = os.getcwd()
db_path = os.path.join(path, db_name)
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS Jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        organization TEXT NOT NULL,
        location TEXT NOT NULL,
        salary_min REAL,
        salary_max REAL
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS JobMetadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        post_date TEXT,
        day_of_week TEXT,
        FOREIGN KEY (job_id) REFERENCES Jobs(id)
    )
''')

conn.commit()

# === Count existing jobs ===
cur.execute("SELECT COUNT(*) FROM Jobs")
existing_count = cur.fetchone()[0]

# === Fetch jobs ===
inserted_this_run = 0
max_to_insert = batch_size

for state in valid_states:
    if inserted_this_run >= max_to_insert:
        break

    print(f"\n🔍 Searching jobs in {state}...")
    page = 1

    while True:
        if inserted_this_run >= max_to_insert:
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
            print(f"❌ Error for {state} page {page}: {response.status_code}")
            break

        results = response.json().get("SearchResult", {}).get("SearchResultItems", [])
        if not results:
            break

        for job in results:
            if inserted_this_run >= max_to_insert:
                break

            if existing_count > 0:
                existing_count -= 1
                continue

            descriptor = job.get("MatchedObjectDescriptor", {})
            title = descriptor.get("PositionTitle", "N/A")
            organization = descriptor.get("OrganizationName", "N/A")
            job_location = descriptor.get("PositionLocationDisplay", "")
            salary_info = descriptor.get("PositionRemuneration", [])
            salary_min = salary_max = None

            for salary in salary_info:
                if salary.get("CurrencyCode") == "USD":
                    salary_min = float(salary.get("MinimumRange", 0))
                    salary_max = float(salary.get("MaximumRange", 0))
                    break

            if any(word.lower() in job_location.lower() for word in ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]):
                continue

            # Correctly get the post date
            date_str = descriptor.get("PublicationStartDate", "")
    
            try:
                if date_str:
                    post_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                else:
                    raise ValueError("Missing PublicationStartDate")

                day_of_week = post_date.strftime("%A")  # Get the day of the week
            except Exception as e:
                print(f"Error parsing date for job: {descriptor.get('PositionTitle')}, Error: {str(e)}")
                post_date = datetime.now()  # Fallback to current date if there's an error
                day_of_week = post_date.strftime("%A")


            # Insert job
            cur.execute('''
                INSERT INTO Jobs (title, organization, location, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, organization, job_location, salary_min, salary_max))

            job_id = cur.lastrowid

            # Insert metadata
            cur.execute('''
                INSERT INTO JobMetadata (job_id, post_date, day_of_week)
                VALUES (?, ?, ?)
            ''', (job_id, post_date.strftime("%Y-%m-%d"), day_of_week))

            inserted_this_run += 1
            print(f"✅ Inserted {inserted_this_run}: {title} | {job_location}")

        page += 1

conn.commit()

# === Data analysis and visualizations ===
query = """
SELECT J.location, M.day_of_week
FROM Jobs J
JOIN JobMetadata M ON J.id = M.job_id
"""
df = pd.read_sql_query(query, conn)

# Jobs per day
day_counts = df['day_of_week'].value_counts().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
).fillna(0).astype(int)

# Alphabetical sample of 10 job locations
location_counts = (
    df.groupby("location").size().reset_index(name="count")
    .sort_values("location")
    .head(10)
    .set_index("location")["count"]
)

# Write to text file
with open("job_summary.txt", "w") as f:
    f.write("=== Job Count by Day of Week ===\n")
    f.write(day_counts.to_string())
    f.write("\n\n=== 10 Alphabetically Sorted Job Locations ===\n")
    f.write(location_counts.to_string())

# Plot 1: Jobs by Day of the Week
plt.figure(figsize=(8, 5))
day_counts.plot(kind='bar', color='skyblue')
plt.title('Jobs Posted by Day of the Week')
plt.xlabel('Day of the Week')
plt.ylabel('Number of Jobs')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('jobs_by_day.png')
plt.close()

# Plot 2: Alphabetical Job Locations
plt.figure(figsize=(8, 5))
location_counts.plot(kind='barh', color='lightgreen')
plt.title('10 Job Locations (Alphabetical Sample)')
plt.xlabel('Number of Jobs')
plt.ylabel('Location')
plt.tight_layout()
plt.savefig('jobs_by_location.png')
plt.close()

print("✅ Plots saved as 'jobs_by_day.png' and 'jobs_by_location.png'")

conn.close()
print(f"\n🎉 Done! {inserted_this_run} new jobs added to the database.")


#             organization = descriptor.get("OrganizationName", "N/A")
#             job_location = descriptor.get("PositionLocationDisplay", "")

#             # Skip if job location is vague
#             skip_keywords = ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]
#             if any(word.lower() in job_location.lower() for word in skip_keywords):
#                 continue

#             new_inserts = 0 
#             for item in results: 
#                 if new_inserts >= 25: 
#                     break

#             if cur.rowcount == 1: 
#                     new_inserts += 1
#             conn.commit



#             # Insert the job data into the database
#             cur.execute('''
#                 INSERT INTO Jobs (title, organization, location)
#                 VALUES (?, ?, ?)
#             ''', (title, organization, job_location))

#             clean_jobs_inserted += 1
#             print(f"✅ {clean_jobs_inserted}. {title} | {job_location}")

#             if clean_jobs_inserted >= max_jobs:
#                 break

#         page += 1



        

# conn.commit()
# conn.close()

# print(f"\n🎉 Done! {clean_jobs_inserted} jobs with clear state locations added to the database.")