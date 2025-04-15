import requests
import unittest
import sqlite3
import json
import os
from dotenv import load_dotenv
import os
from datetime import datetime
import matplotlib.pyplot as plt
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

# DB setup
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
conn.commit()

cur.execute("SELECT COUNT(*) FROM Jobs")
start_index = cur.fetchone()[0]
clean_jobs_inserted = 0

# Fetch and insert data
for state in valid_states:
    if clean_jobs_inserted >= batch_size:
        break

    page = 1
    while True:
        if clean_jobs_inserted >= batch_size:
            break

        url = "https://data.usajobs.gov/api/search"
        params = {
            "Keyword": "Software",
            "LocationName": state,
            "ResultsPerPage": 50,
            "Page": page
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {state}: {e}")
            break

        data = response.json()
        results = data.get("SearchResult", {}).get("SearchResultItems", [])
        if not results:
            break

        for job in results:
            if clean_jobs_inserted >= batch_size:
                break

            descriptor = job.get("MatchedObjectDescriptor", {})
            title = descriptor.get("PositionTitle", "N/A")
            organization = descriptor.get("OrganizationName", "N/A")
            job_location = descriptor.get("PositionLocationDisplay", "")

            skip_keywords = ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]
            if any(word.lower() in job_location.lower() for word in skip_keywords):
                continue

            salary_info = descriptor.get("PositionRemuneration", [])
            salary_min = salary_max = None
            for salary in salary_info:
                if salary.get("CurrencyCode") == "USD":
                    try:
                        salary_min = float(salary.get("MinimumRange", 0))
                        salary_max = float(salary.get("MaximumRange", 0))
                    except (ValueError, TypeError):
                        pass
                    break

            cur.execute('''
                SELECT COUNT(*) FROM Jobs
                WHERE title = ? AND organization = ? AND location = ?
            ''', (title, organization, job_location))
            if cur.fetchone()[0] > 0:
                continue

            cur.execute('''
                INSERT INTO Jobs (title, organization, location, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, organization, job_location, salary_min, salary_max))
            clean_jobs_inserted += 1

        page += 1

conn.commit()

# -------------------
# Salary Analysis
# -------------------
cur.execute('''
    SELECT location, AVG(salary_min), AVG(salary_max)
    FROM Jobs
    WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
    GROUP BY location
    ORDER BY AVG(salary_max) DESC
    LIMIT 10
''')
salary_data = cur.fetchall()

txt_path = os.path.join(path, "salary_summary.txt")
with open(txt_path, "w") as f:
    f.write("Top 10 Locations by Average Max Salary:\n")
    for row in salary_data:
        f.write(f"{row[0]}: ${row[1]:,.2f} - ${row[2]:,.2f}\n")

locations = [row[0] for row in salary_data]
avg_min = [row[1] for row in salary_data]
avg_max = [row[2] for row in salary_data]

plt.figure(figsize=(12, 6))
plt.bar(locations, avg_max, label="Avg Max Salary", color="orange")
plt.bar(locations, avg_min, label="Avg Min Salary", color="skyblue", alpha=0.7)
plt.title("Top 10 Locations by Avg Salary for Software Jobs")
plt.xlabel("Location")
plt.ylabel("Salary (USD)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
chart_path = os.path.join(path, "salary_chart.png")
plt.savefig(chart_path)

conn.close()
print(f"✅ Added {clean_jobs_inserted} new jobs.\n📄 Salary summary: {txt_path}\n📊 Salary chart: {chart_path}")







# # === Headers for the API request ===
# headers = {
#     "Host": "data.usajobs.gov",
#     "User-Agent": USER_AGENT,
#     "Authorization-Key": API_KEY
# }

# # === DB setup ===
# path = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(path + "/" + db_name)
# cur = conn.cursor()

# # Create Jobs table
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS Jobs (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT NOT NULL,
#         organization TEXT NOT NULL,
#         location TEXT NOT NULL
#     )
# ''')

# # Create JobMetadata table for analysis
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS JobMetadata (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         job_id INTEGER NOT NULL,
#         post_date TEXT,
#         day_of_week TEXT,
#         FOREIGN KEY (job_id) REFERENCES Jobs(id)
#     )
# ''')
# try:
#     cur.execute('ALTER TABLE Jobs ADD COLUMN salary_min REAL')
#     cur.execute('ALTER TABLE Jobs ADD COLUMN salary_max REAL')
#     conn.commit()
# except sqlite3.OperationalError:
#     # Columns already exist
#     pass



# conn.commit()

# # === 🔹 Count how many jobs already exist ===
# cur.execute("SELECT COUNT(*) FROM Jobs")
# existing_count = cur.fetchone()[0]

# # === Setup for this run ===
# max_to_insert = 25
# inserted_this_run = 0

# # === Begin job fetching ===
# for state in valid_states:
#     if inserted_this_run >= max_to_insert:
#         break

#     print(f"\n🔍 Searching jobs in {state}...")
#     page = 1

#     while True:
#         if inserted_this_run >= max_to_insert:
#             break

#         url = "https://data.usajobs.gov/api/search"
#         params = {
#             "Keyword": "Software",
#             "LocationName": state,
#             "ResultsPerPage": 50,
#             "Page": page
#         }

#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code != 200:
#             print(f"❌ Error for {state} page {page}: {response.status_code}")
#             break

#         results = response.json().get("SearchResult", {}).get("SearchResultItems", [])
#         if not results:
#             break

#         for job in results:
#             if inserted_this_run >= max_to_insert:
#                 break

#             # 🔸 Skip previously inserted jobs
#             if existing_count > 0:
#                 existing_count -= 1
#                 continue

#             descriptor = job.get("MatchedObjectDescriptor", {})
#             title = descriptor.get("PositionTitle", "N/A")
#             organization = descriptor.get("OrganizationName", "N/A")
#             job_location = descriptor.get("PositionLocationDisplay", "")
#             salary_info = descriptor.get("PositionRemuneration", [])
#             salary_min = salary_max = None

#             # Grab salary range from PositionRemuneration list
#             for salary in salary_info:
#                 if salary.get("CurrencyCode") == "USD":
#                     salary_min = float(salary.get("MinimumRange", 0))
#                     salary_max = float(salary.get("MaximumRange", 0))
#                     break  # Use first valid USD range

#             # Skip vague locations
#             if any(word.lower() in job_location.lower() for word in ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]):
#                 continue

#             # Parse date
#             try:
#                 post_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
#                 day_of_week = post_date.strftime("%A")
#             except:
#                 post_date = datetime.now()
#                 day_of_week = post_date.strftime("%A")

#             # Insert into Jobs table
#             cur.execute('''
#                 INSERT INTO Jobs (title, organization, location, salary_min, salary_max)
#                 VALUES (?, ?, ?, ?, ?)
#             ''', (title, organization, job_location, salary_min, salary_max))

#             job_id = cur.lastrowid

#             # Insert into metadata table
#             cur.execute('''
#                 INSERT INTO JobMetadata (job_id, post_date, day_of_week)
#                 VALUES (?, ?, ?)
#             ''', (job_id, post_date.strftime("%Y-%m-%d"), day_of_week))
            


#             inserted_this_run += 1
#             print(f"✅ Inserted {inserted_this_run}: {title} | {job_location}")

#         page += 1

# # === Finalize ===
# conn.commit()
# conn.close()

# print(f"\n🎉 Done! {inserted_this_run} new jobs added to the database.")































# # List of all valid U.S. states
# valid_states = [
#     "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
#     "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
#     "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
#     "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
#     "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
#     "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
#     "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
# ]

# # Headers for the API request
# headers = {
#     "Host": "data.usajobs.gov",
#     "User-Agent": USER_AGENT,
#     "Authorization-Key": API_KEY
# }

# # DB setup
# path = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(path + "/" + db_name)
# cur = conn.cursor()

# # Create Jobs table if not exists
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS Jobs (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT NOT NULL,
#         organization TEXT NOT NULL,
#         location TEXT NOT NULL
#     )
# ''')
# conn.commit()

# # Data fetching loop
# clean_jobs_inserted = 0
# max_jobs = 1000  # Increase this if you need more than 1000 jobs

# for state in valid_states:
#     if clean_jobs_inserted >= max_jobs:
#         break

#     print(f"\n🔍 Searching jobs in {state}...")
#     page = 1

#     while True:
#         if clean_jobs_inserted >= max_jobs:
#             break

#         # API request parameters
#         url = "https://data.usajobs.gov/api/search"
#         params = {
#             "Keyword": "Software",  # You can modify this to other keywords if needed
#             "LocationName": state,
#             "ResultsPerPage": 50,  # Adjust based on how many jobs per request you want
#             "Page": page
#         }

#         response = requests.get(url, headers=headers, params=params)

#         if response.status_code != 200:
#             print(f"❌ Error for {state} page {page}: {response.status_code}")
#             break

#         data = response.json()
#         results = data.get("SearchResult", {}).get("SearchResultItems", [])

#         if not results:
#             break

#         for job in results:
#             descriptor = job.get("MatchedObjectDescriptor", {})
#             title = descriptor.get("PositionTitle", "N/A")
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