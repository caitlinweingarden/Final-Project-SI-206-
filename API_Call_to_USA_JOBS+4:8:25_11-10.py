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

# Define the endpoint and parameters
# url = "https://data.usajobs.gov/api/search"
url = "https://data.usajobs.gov/api/search?JobCategoryCode=2210"
params = {
    "Keyword": "Software",
     "LocationName": "Atlanta,%20Georgia"
}
# params = {
#     "Keyword": "Software",
#     "LocationName": "Dupont,%20Washington"
# }
# Set the headers
headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": USER_AGENT,
    "Authorization-Key": API_KEY
}

# Make the request
response = requests.get(url, headers=headers, params=params)
# print(response)

# Check the status and parse the data
if response.status_code == 200:
    data = response.json()
    # print(data)
    # Print job titles as an example
    for job in data.get("SearchResult", {}).get("SearchResultItems", []):
        print("here", job["MatchedObjectDescriptor"]["PositionTitle"])
else:
    print(f"Error: {response.status_code} - {response.text}")

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
   
