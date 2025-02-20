import requests

url = "https://staging-express.delhivery.com/c/api/pin-codes/json/?parameters"  # Replace with the correct endpoint
params = {
    "filter_codes": "500047"  # Replace with a valid Pincode
}
headers = {
    "Authorization": "Token 905691f1819ece80a92344e3633ae3342bf30b34",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers, params=params)
print(response.status_code)

# Handle response content
if response.headers.get('Content-Type') == 'application/json':
    print(response.json())
else:
    print(response.text)
