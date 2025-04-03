 
import requests
import json
import unittest
import os



#how do we include the API key ebedded in the 
# base_url = "https://arbeitnow.com/api/job-board-api"
base_url = "https://data.usajobs.gov/api/Search?PositionTitle=Psychologist"

# try: 
response = requests.get(base_url, timeout = 10)
if response.status_code == 200:
    data = response.json()
    print(data)
else: 
    print(f"Error: {response.status_code} - {response.text}")

# if data['Response'] == 'False': 
    # return None
    # print(data, response.url)
# except requests.RequestException:
    # return None