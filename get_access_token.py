import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client_id = os.getenv("SPLITWISE_CLIENT_ID")
client_secret = os.getenv("SPLITWISE_CLIENT_SECRET")

# Authorization code (from the Flask server output)
auth_code = "LF73OHC1d13IZOmDAbpc"  # Replace with the code you copied

# OAuth 2.0 token endpoint
token_url = "https://secure.splitwise.com/oauth/token"
redirect_uri = "http://localhost:8000/callback"

# Request the access token
payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri,
}

response = requests.post(token_url, data=payload)
token_data = response.json()

if "error" in token_data:
    print(f"Error: {token_data['error']}")
else:
    access_token = token_data["access_token"]
    print(f"Access Token: {access_token}")
    with open("splitwise_access_token.txt", "w") as f:
        f.write(access_token)
