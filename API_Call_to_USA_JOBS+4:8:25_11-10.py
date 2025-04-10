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


import os
import sqlite3
import requests

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
            print(f"❌ Error for {state} page {page}: {response.status_code}")
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



























# # Valid U.S. states
# valid_states = {
#     "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
#     "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
#     "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
#     "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
#     "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
#     "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
#     "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
# }

# # List of cities to search
# locations_to_add = [
#     ("New York", "New York", "USA"),
#     ("Los Angeles", "California", "USA"),
#     ("Chicago", "Illinois", "USA"),
#     ("Houston", "Texas", "USA"),
#     ("Phoenix", "Arizona", "USA"),
#     ("Philadelphia", "Pennsylvania", "USA"),
#     ("San Antonio", "Texas", "USA"),
#     ("San Diego", "California", "USA"),
#     ("Dallas", "Texas", "USA"),
#     ("San Jose", "California", "USA"),
#     ("Austin", "Texas", "USA"),
#     ("Jacksonville", "Florida", "USA"),
#     ("Fort Worth", "Texas", "USA"),
#     ("Columbus", "Ohio", "USA"),
#     ("Charlotte", "North Carolina", "USA"),
#     ("San Francisco", "California", "USA"),
#     ("Indianapolis", "Indiana", "USA"),
#     ("Seattle", "Washington", "USA"),
#     ("Denver", "Colorado", "USA"),
#     ("Washington", "D.C.", "USA"),
# ]

# # Headers for the API
# headers = {
#     "Host": "data.usajobs.gov",
#     "User-Agent": USER_AGENT,
#     "Authorization-Key": API_KEY
# }

# # Database setup
# path = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(path + "/" + db_name)
# cur = conn.cursor()

# # Optional: Clear old jobs (for testing/reruns)
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS Jobs (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT NOT NULL,
#         organization TEXT NOT NULL,
#         location TEXT NOT NULL
#     )
# ''')
# cur.execute('DELETE FROM Jobs')
# conn.commit()

# # Job scraping logic
# clean_jobs_inserted = 0

# for city, state, country in locations_to_add:
#     location_query = f"{city}, {state}".replace(" ", "%20")
#     print(f"\n🔍 Fetching jobs for {city}, {state}...")

#     page = 1
#     while True:
#         if clean_jobs_inserted >= 100:
#             break

#         url = "https://data.usajobs.gov/api/search"
#         params = {
#             "Keyword": "Software",
#             "LocationName": location_query,
#             "ResultsPerPage": 50,
#             "Page": page
#         }

#         response = requests.get(url, headers=headers, params=params)

#         if response.status_code != 200:
#             print(f"❌ Error for {city}, {state} (page {page}): {response.status_code}")
#             break

#         data = response.json()
#         results = data.get("SearchResult", {}).get("SearchResultItems", [])

#         if not results:
#             print(f"✅ No more jobs found for {city}, {state} at page {page}.")
#             break

#         for job in results:
#             descriptor = job.get("MatchedObjectDescriptor", {})
#             title = descriptor.get("PositionTitle", "N/A")
#             organization = descriptor.get("OrganizationName", "N/A")
#             job_location = descriptor.get("PositionLocationDisplay", "N/A")

#             # Filter out vague or multiple locations
#             skip_keywords = [
#                 "Various", "Multiple", "Negotiable", "Anywhere", "United States", "U.S.", "May be filled"
#             ]
#             if any(keyword.lower() in job_location.lower() for keyword in skip_keywords):
#                 continue

#             if "," not in job_location:
#                 continue

#             try:
#                 _, maybe_state = [part.strip() for part in job_location.split(",", 1)]
#             except ValueError:
#                 continue

#             if maybe_state not in valid_states:
#                 continue

#             # Insert clean job into DB
#             cur.execute('''
#                 INSERT INTO Jobs (title, organization, location)
#                 VALUES (?, ?, ?)
#             ''', (title, organization, job_location))

#             clean_jobs_inserted += 1
#             print(f"✅ Saved: {title} | {job_location}")

#             if clean_jobs_inserted >= 100:
#                 break

#         print(f"📄 Done page {page} for {city}, {state}")
#         page += 1

#     if clean_jobs_inserted >= 100:
#         break

# # Finalize
# conn.commit()
# conn.close()
# print(f"\n🎉 Finished inserting {clean_jobs_inserted} clean job listings into the database.")





































# locations_to_add = [
#     ("New York", "New York", "USA"),
#     ("Los Angeles", "California", "USA"),
#     ("Chicago", "Illinois", "USA"),
#     ("Houston", "Texas", "USA"),
#     ("Phoenix", "Arizona", "USA"),
#     ("Philadelphia", "Pennsylvania", "USA"),
#     ("San Antonio", "Texas", "USA"),
#     ("San Diego", "California", "USA"),
#     ("Dallas", "Texas", "USA"),
#     ("San Jose", "California", "USA"),
#     ("Austin", "Texas", "USA"),
#     ("Jacksonville", "Florida", "USA"),
#     ("Fort Worth", "Texas", "USA"),
#     ("Columbus", "Ohio", "USA"),
#     ("Charlotte", "North Carolina", "USA"),
#     ("San Francisco", "California", "USA"),
#     ("Indianapolis", "Indiana", "USA"),
#     ("Seattle", "Washington", "USA"),
#     ("Denver", "Colorado", "USA"),
#     ("Washington", "D.C.", "USA"),
#     # Add more cities and states as needed
# ]
# for location in locations_to_add:
#     url = "https://data.usajobs.gov/api/search?JobCategoryCode=2210"
#     params = {
#         "Keyword": "Software",
#         "LocationName": f"{location[0]}, {location[1]}".replace(" ","%20")
#     }

# path = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(path + "/" + db_name)
# cur = conn.cursor()

# # Create the Jobs table if it doesn't exist
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS Jobs (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT NOT NULL,
#         organization TEXT NOT NULL,
#         location TEXT NOT NULL
#     )
# ''')

# # Set headers for the request
# headers = {
#     "Host": "data.usajobs.gov",
#     "User-Agent": USER_AGENT,
#     "Authorization-Key": API_KEY
# }

# # Loop through locations and get job data
# for city, state, country in locations_to_add:
#     location_query = f"{city}, {state}".replace(" ", "%20")
#     print(f"Fetching jobs for {city}, {state}...")

#     page = 1  
#     while True: 
#         url = "https://data.usajobs.gov/api/search"
#         params = {
#             "Keyword": "Software",
#             "LocationName": location_query,
#             "ResultsPerPage": 50, 
#             "Page": page 
#         }

#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code != 200:
#                 print(f"Error for {city}, {state} (page {page}): {response.status_code} - {response.text}")  
#                 break 


        
#         data = response.json()
#         results = data.get("SearchResult", {}).get("SearchResultItems", [])
#         if not results:
#                 print(f"No more jobs found for {city}, {state} at page {page}.")  # 🔹 NEW
#                 break 

#         for job in results:
#             descriptor = job.get("MatchedObjectDescriptor", {})
#             title = descriptor.get("PositionTitle", "N/A")
#             organization = descriptor.get("OrganizationName", "N/A")
#             job_location = descriptor.get("PositionLocationDisplay", "N/A")


#             if any(keyword in job_location for keyword in ["Various", ";", "Multiple", "United States"]):
#                     continue
#             if job_location.count(",") != 1:
#                     continue
#             # Insert into the database
#             cur.execute('''
#                 INSERT INTO Jobs (title, organization, location)
#                 VALUES (?, ?, ?)
#             ''', (title, organization, job_location))

#             print(f"Page {page} done for {city}, {state}")  # 🔹 NEW
#             page += 1  # 🔹 NEW

            
# # Commit changes and close the connection
# conn.commit()
# conn.close()
# print("All data inserted into the database successfully.")















# # for city, state, country in locations_to_add:
# #     cur.execute('''
# #         INSERT INTO Locations (city, state, country)
# #         VALUES (?, ?, ?)
# #     ''', (city, state, country))

# # conn.commit()


# # # Define the endpoint and parameters
# # # url = "https://data.usajobs.gov/api/search"

# # # params = {
# # #     "Keyword": "Software",
# # #     "LocationName": "Dupont,%20Washington"
# # # }
# # # Set the headers



# # headers = {
# #     "Host": "data.usajobs.gov",
# #     "User-Agent": USER_AGENT,
# #     "Authorization-Key": API_KEY
# # }

# # # Make the request
# # response = requests.get(url, headers=headers, params=params)
# # # print(response)

# # # Check the status and parse the data
# # if response.status_code == 200:
# #     data = response.json()
# #     # print(data)
# #     # Print job titles as an example
# #     for job in data.get("SearchResult", {}).get("SearchResultItems", []):
# #         print("here", job["MatchedObjectDescriptor"]["PositionTitle"])
# # else:
# #     print(f"Error: {response.status_code} - {response.text}")

# #     path = os.path.dirname(os.path.abspath(__file__))
# #     conn = sqlite3.connect(path + "/" + db_name)
# #     cur = conn.cursor()

# #     # Fetch data from the API
# # response = requests.get(url, headers=headers, params=params)

# # # Check the API response
# # if response.status_code == 200:
# #     data = response.json()
    
# #     # Define database connection and cursor
# #     db_name = 'usajobs.db'
# #     path = os.path.dirname(os.path.abspath(__file__))
# #     conn = sqlite3.connect(path + "/" + db_name)
# #     cur = conn.cursor()

# #     # Create the table if it doesn't exist
# #     cur.execute('''
# #         CREATE TABLE IF NOT EXISTS Jobs (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             title TEXT NOT NULL,
# #             organization TEXT NOT NULL,
# #             location TEXT NOT NULL
# #         )
# #     ''')

# #     # Insert data into the database
# #     for job in data.get("SearchResult", {}).get("SearchResultItems", []):
# #         title = job.get("MatchedObjectDescriptor", {}).get("PositionTitle", "N/A")
# #         organization = job.get("MatchedObjectDescriptor", {}).get("OrganizationName", "N/A")
# #         location = job.get("MatchedObjectDescriptor", {}).get("PositionLocationDisplay", "N/A")

# #         # Insert the job data into the Jobs table
# #         cur.execute('''
# #             INSERT INTO Jobs (title, organization, location)
# #             VALUES (?, ?, ?)
# #         ''', (title, organization, location))

# #     # Commit and close the connection
# #     conn.commit()
# #     conn.close()

# #     print("Data inserted into the database successfully.")

# # else:
# #     print(f"Error: {response.status_code} - {response.text}")
   
