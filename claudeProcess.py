import base64
import datetime
import io
import json
import os
import re
import sys

import anthropic
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Initialize the Claude client
client = anthropic.Anthropic(api_key=api_key)

# Get the image path (configurable via command-line argument)
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    image_path = "bill_image.jpeg"

# Open and convert the image to ensure it's a proper JPEG
try:
    with open(image_path, "rb") as f:
        img = Image.open(f)
        img = img.convert("RGB")
except FileNotFoundError:
    raise FileNotFoundError(f"Image file not found: {image_path}")

buffer = io.BytesIO()
img.save(buffer, format="JPEG")
jpeg_data = buffer.getvalue()

# Encode the image data in Base64
image_data = base64.b64encode(jpeg_data).decode("utf-8").replace("\n", "")

# Get today's date in YYYY-MM-DD format
today_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Craft the prompt for Claude
prompt = f"""
You are a bill-splitting assistant. Process the attached restaurant bill image and do the following:
1. Extract each item and its price from the bill.
2. Calculate the total amount.
3. Split the total equally among the members of the Splitwise group "Test". Assume there are 2 members in the group for now.
4. Create an expense entry for the group with today's date ({today_date}).
5. Return the result in JSON format exactly as follows:

{{
  "items": [
    {{"item": "Pasta", "price": 12.0}},
    {{"item": "Salad", "price": 9.0}},
    {{"item": "Soda", "price": 3.0}}
  ],
  "total": 24.0,
  "splitwise_group": {{
      "group_name": "Test",
      "expense_date": "{today_date}",
      "split_equally": true,
      "each_share": 12.0
  }}
}}

Ensure all math is correct and the JSON structure exactly follows the format.
"""

# Send the request to Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
            ],
        }
    ],
)

# Debug: Print the raw response content
raw_response_text = response.content[0].text
print("Raw response text:")
print(raw_response_text)

# Extract JSON portion
try:
    # Look for the first JSON block between { and }
    json_match = re.search(r"({.*})", raw_response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group(1)
        bill_data = json.loads(json_text)
        print("Parsed JSON:", bill_data)

        # Validate the split
        total = bill_data["total"]
        each_share = bill_data["splitwise_group"]["each_share"]
        num_members = 2  # Hardcoded for now; fetch dynamically later
        calculated_total = each_share * num_members
        if abs(calculated_total - total) > 0.01:  # Allow small float errors
            raise ValueError(
                f"Split validation failed: {each_share} * {num_members} = {calculated_total}, but total is {total}"
            )
    else:
        raise ValueError("No JSON block found in the response.")
except json.decoder.JSONDecodeError as e:
    print("Failed to decode JSON. Extracted text was:")
    print(json_text)
    raise e

# Save the output for further processing
with open("bill_data.json", "w") as f:
    json.dump(bill_data, f)
