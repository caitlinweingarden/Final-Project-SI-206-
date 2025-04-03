import requests

access_token = "1d603462de59cba022854727e5430fa364e8f3bdafcf5ac0eba0ecd883c19ee9"   # The value from the token endpoint
api_url = "https://api.dribbble.com/v2/user"

headers = {
    "Authorization": f"Bearer {access_token}"
}
r = requests.get(api_url, headers=headers)
print(r.status_code, r.text)