import os
import webbrowser

from dotenv import load_dotenv
from flask import Flask, request

app = Flask(__name__)

# Load environment variables
load_dotenv()
client_id = os.getenv("SPLITWISE_CLIENT_ID")

# Global variable to store the authorization code
auth_code = None


@app.route("/callback")
def callback():
    global auth_code
    auth_code = request.args.get("code")
    print(f"Authorization Code: {auth_code}")
    return "Authorization code received! You can close this window."


if __name__ == "__main__":
    auth_url = f"https://secure.splitwise.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost:8000/callback&response_type=code"
    webbrowser.open(auth_url)
    app.run(host="0.0.0.0", port=8000)
