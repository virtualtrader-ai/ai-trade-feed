from openai import OpenAI
import json
import os
from datetime import date

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create the prompt
prompt = (
    f"Generate 3 high-risk, high-reward options trade ideas for today ({date.today().strftime('%Y-%m-%d')}). "
    "Each trade should include: ticker, setup, direction (Call or Put), strike price, expiry date, "
    "estimated entry, target, stop loss, confidence level (High/Medium/Low), and a short rationale. "
    "Output in raw JSON array format with no explanation."
)

# Request from ChatGPT
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

# Parse AI response as raw JSON
try:
    trade_data = json.loads(response.choices[0].message.content.strip())
except json.JSONDecodeError:
    raise Exception("Failed to parse AI output as valid JSON.")

# Save to file
with open("live_trades.json", "w") as f:
    json.dump(tra

