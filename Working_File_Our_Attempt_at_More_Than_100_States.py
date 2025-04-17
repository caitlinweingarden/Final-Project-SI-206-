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
#We did this in order to hide the API key by storing it in a separate section

# Set your credentials
USER_AGENT = "caitliw@umich.edu"         # The email you used to sign up for USA Jobs
API_KEY =  os.getenv("API_KEY")        # Your USAJOBS API Key

db_name = 'usajobs.db'

batch_size = 25

# Use current working directory instead of __file__
path = os.getcwd()
db_path = os.path.join(path, db_name)

headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": USER_AGENT,
    "Authorization-Key": API_KEY
}

# Here  is where connect to SQl and create the database. 
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


conn.commit()

valid_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

salary_buckets = {0:"24999", 25: "25000:49999", 50: "50,000-$74999", 75: "75,000-$99999", 100: "100000-$124999", 125: "125000-$149999", 150: "150000-$174999", 175: "175000-$199999", 200: "200000"}


salary_buckets[0] = "0:24999"
"0:24999", "25000:49999", "50,000-$74999", "75,000-$99999", "100000-$124999", "125000-$149999", "150000-$174999", "175000-$199999" "200000"



#Here we created the table and checks if no jobs exist as well. 


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

# Counting the existing jobs 
cur.execute("SELECT COUNT(*) FROM Jobs")
existing_count = cur.fetchone()[0]

# Getting the jobs 
inserted_this_run = 0
max_to_insert = batch_size

for state in valid_states:
    if inserted_this_run >= max_to_insert:
        break

    print(f"\n Searching for jobs in {state}...")
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
            print(f" Error for {state} page {page}: {response.status_code}")
            break

        results = response.json().get("SearchResult", {}).get("SearchResultItems", [])

        results_salary = response.json().get("SearchResult", {})
        
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

    
            cur.execute('''
                INSERT OR IGNORE INTO Jobs (title, organization, location, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, organization, job_location, salary_min, salary_max))

            job_id = cur.lastrowid


            inserted_this_run += 1
            print(f" Inserted {inserted_this_run}: {title} | {job_location}")

        page += 1

#above is where we fetch the data and add it to the database. 








conn.commit()


conn.close()
print(f"\n All Done! {inserted_this_run} new jobs added to the database.")










# #  Data analysis and visualizations
# query = """
# SELECT J.location, M.day_of_week
# FROM Jobs J
# JOIN JobMetadata M ON J.id = M.job_id
# """
# df = pd.read_sql_query(query, conn)

# # Jobs per day
# day_counts = df['day_of_week'].value_counts().reindex(
#     ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# ).fillna(0).astype(int)

# This is where we make an alphabetical sample of 10 job locations
# location_counts = (
#     df.groupby("location").size().reset_index(name="count")
#     .sort_values("location")
#     .head(10)
#     .set_index("location")["count"]
# )

# # Writing the text to a text file
# with open("job_summary.txt", "w") as f:
#     f.write("=== Job Count by Day of Week ===\n")
#     f.write(day_counts.to_string())
#     f.write("\n\n=== 10 Alphabetically Sorted Job Locations ===\n")
#     f.write(location_counts.to_string())



#calculations is in one file 
#visualizationseach one is in one file 
#creating the database and fetching/storing the database stuff is in one file. 

         