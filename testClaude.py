import os

import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize Claude client
client = anthropic.Anthropic(api_key=api_key)

# Test with a simple text prompt
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello, Claude! Can you help me?"}],
)

# Print the response
print(response.content[0].text)
