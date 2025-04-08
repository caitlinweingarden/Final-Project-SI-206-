import requests

# Replace this with your actual token:
ACCESS_TOKEN = "1d603462de59cba022854727e5430fa364e8f3bdafcf5ac0eba0ecd883c19ee9"

url = "https://dribbble.com/oauth/authorize?client_id=ca5de6117aa650d5512c4904b6dc2f39858221498c0a252eebe30d1daf31fe33"


# access token = https://ww7.codingproject.com/?code=1d603462de59cba022854727e5430fa364e8f3bdafcf5ac0eba0ecd883c19ee9&usid=26&utid=11548625625
# 1d603462de59cba022854727e5430fa364e8f3bdafcf5ac0eba0ecd883c19ee9
# Example: Get your user info (if your token is authorized to read user data)
api_url = "https://api.dribbble.com/v2/user"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
print(api_url)
response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("User info:")
    print(data)
else:
    print("Failed to fetch data:", response.status_code, response.text)