 
import requests
import json
import unittest
import os


# $ curl -H 'Host: data.usajobs.gov' \
#   'User-Agent: $YOUR_EMAIL' \   
#   'Authorization-Key: $AUTH_KEY' \   
  https://data.usajobs.gov/api/search?JobCategoryCode=2210
#how do we include the API key ebedded in the 
# base_url = "https://arbeitnow.com/api/job-board-api"
api_key = "XOtjR+MmBPBPUjxiux8Dpf6bBKTKUaU6F8ChXifeHhk="
base_url = f"https://data.usajobs.gov/api/Search?PositionTitle=Psychologist?apikey={api_key}"
# base_url = "https://api.ziprecruiter.com/partner/v0/job"

# try: 
response = requests.get(base_url, timeout = 10)
if response.status_code == 200:
    data = response.json()
    print(data)
else: 
    print(f"Error: {response.status_code} - {response.text}")

