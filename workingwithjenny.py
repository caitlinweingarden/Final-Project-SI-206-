import requests
CLIENT_ID = "98deeb06709db2b3f28403d82af2d665258197ce34810597f163b5e0929c8f83"
CLIENT_SECRET = "f3431558b0ccc1f1ecda2c97822927d01fb0168412c8331589db668e18fa66c9"

# api_key2 = "XOtjR+MmBPBPUjxiux8Dpf6bBKTKUaU6F8ChXifeHhk"

# access_token = "1d603462de59cba022854727e5430fa364e8f3bdafcf5ac0eba0ecd883c19ee9"   # The value from the token endpoint
api_url = "https://api.dribbble.com/v2/user"
# # client_id=CLIENT_ID&client_secret=CLIENT_SECRET&code=COPIED_CODE
full_url = f"{api_url}?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
print(full_url)
# headers = {
#     "Authorization": f"Bearer {access_token}"
# }
# r = requests.get(api_url, headers=headers)
# print(r.status_code, r.text)

# url = f"https://api.dribbble.com/v2/user?access_token={api_key2}"
# print(url)