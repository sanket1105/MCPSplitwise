import base64
import json
import os

import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize Claude client
client = anthropic.Anthropic(api_key=api_key)

# Load and encode the bill image
with open("bill_image.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

# Prompt Claude to extract and split the bill
prompt = """
This is a restaurant bill image. Extract the items, prices, and total. Then split the bill based on the following:
- John had the pasta.
- Mary had the salad.
- The soda is split evenly between John and Mary.
- Add the expense to Splitwise group 'Dinner Friends' (group ID: 123456).

Return the result in JSON format like:
{
  "items": [
    {"person": "John", "item": "Pasta", "cost": 12.0},
    {"person": "Mary", "item": "Salad", "cost": 9.0},
    {"person": "John", "item": "Soda", "cost": 1.5},
    {"person": "Mary", "item": "Soda", "cost": 1.5}
  ],
  "splitwise_group_id": 123456
}
"""

# Send request to Claude
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

# Parse Claude’s response
bill_data = json.loads(response.content[0].text)
print(bill_data)

# Save the output for MCP
with open("bill_data.json", "w") as f:
    json.dump(bill_data, f)
