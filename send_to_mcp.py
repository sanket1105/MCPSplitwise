import json

import requests

# Load Claude’s output
with open("bill_data.json", "r") as f:
    bill_data = json.load(f)

# Send to MCP server
response = requests.post("http://localhost:8000/process_bill", json=bill_data)
print(response.json())
