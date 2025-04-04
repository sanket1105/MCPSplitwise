import webbrowser

from flask import Flask, request

app = Flask(__name__)

# Global variable to store the authorization code
auth_code = None


@app.route("/callback")
def callback():
    global auth_code
    auth_code = request.args.get("code")
    return "Authorization code received! You can close this window."


if __name__ == "__main__":
    # Open the browser to start the OAuth flow
    auth_url = "https://secure.splitwise.com/oauth/authorize?client_id=your_client_id_here&redirect_uri=http://localhost:8000/callback&response_type=code"
    webbrowser.open(auth_url)
    app.run(host="0.0.0.0", port=8000)
