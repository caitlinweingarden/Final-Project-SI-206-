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


db_name = 'usajobs.db' #this is where we name our database

batch_size = 25
#the batch size is the amount of jobs that get added to that data base at a time 

#this is where we get the working directory and combine it with usajobs to create a full path. 
path = os.getcwd()
db_path = os.path.join(path, db_name)



#here is where we establish what headers we need to access the data from the API
headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": USER_AGENT,
    "Authorization-Key": API_KEY
}

# Here  is where connect to SQl and create the database. 
path = os.getcwd()
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS Titles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization TEXT NOT NULL
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL
    )
''')



#This creates the table called jobs and checks if it doesn't exist as well
cur.execute('''
    CREATE TABLE IF NOT EXISTS Jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title_id INTEGER NOT NULL,
        organization_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        salary_min REAL,
        salary_max REAL,
        FOREIGN KEY (title_id) REFERENCES Titles(id),
        FOREIGN KEY (organization_id) REFERENCES Organizations(id),
        FOREIGN KEY (location_id) REFERENCES Locations(id)
    )
''')
def get_or_insert(cur, table_name, column_name, value):
    cur.execute(f"SELECT id FROM {table_name} WHERE {column_name} = ?", (value,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        return cur.lastrowid

conn.commit()

#here we are listing all the possible states that could be an option for the database, since it is only U.S States
valid_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

#here we are not yet finished but this is where we are trying to get salary bucket information to find which job relates to which salary bucket. 



#Here this is where we define what kind of information we are storing in the table about each job
#so in this case we are getting the id, job title, organization, location, and 
#still attempting to grab the salaries


cur.execute('''
    CREATE TABLE IF NOT EXISTS Jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title_id TEXT NOT NULL,
        organization_id TEXT NOT NULL,
        location_id TEXT NOT NULL,
        salary_min REAL,
        salary_max REAL
    )
''')


conn.commit()

# this part counts if the job already exists in the database, and if it does then it skips over them
cur.execute("SELECT COUNT(*) FROM Jobs")
existing_count = cur.fetchone()[0]






# this code block loops through each state and keeps going until the batch size (25) is reached
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



            #this line of code sends a request to get job data 
            #from the USAJOBS API. It also tries to get 50 job results 
            #per page. 

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
        


        #this section of the code grabs the keys from each job (values) and 
        #gravs the title organization and tries to get salary info too. 
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
            print(f"the salary info is{salary_info}")
            salary_min = salary_max = None




            #here is where we try to get the salary info by saving the varibale 
            #names as salary_max, and salary_min 
            for salary in salary_info:
                salary_min = float(salary.get("MinimumRange", 0))
                print(f"the salary min is {salary_min}")
                salary_max = float(salary.get("MaximumRange", 0))
                print(f"the salary max is {salary_max}")
                break
                #here it checks if there is a job that 
                #doesn't have an exact location and filters those out of the mix
            if any(word.lower() in job_location.lower() for word in ["Negotiable", "Anywhere", "Multiple", "Various", "Remote"]):
                continue
             # Get or insert the title, organization, and location into lookup tables
            title_id= get_or_insert(cur, 'Titles', 'title', title)
            organization_id = get_or_insert(cur, 'Organizations', 'organization', organization)
            location_id = get_or_insert(cur, 'Locations', 'location', job_location)
            

            #this last section inserts the keys relating to the job into 
            #the job database
            cur.execute('''
                INSERT INTO Jobs (title_id, organization_id, location_id, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?)
            ''', (title_id, organization_id, location_id, salary_min, salary_max))

            job_id = cur.lastrowid


            inserted_this_run += 1
            print(f" Inserted {inserted_this_run}: {title} | {job_location}")

        page += 1


#this last part saves all the changes and closes the SQL connection 

conn.commit()
conn.close()
print(f"\n All Done! {inserted_this_run} new jobs added to the database.")



#****************************
















































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

         