
from openai import OpenAI
import json
import os
from datetime import date

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

today = date.today().strftime('%Y-%m-%d')

# Safe prompt using placeholder and replacement instead of nested f-strings
prompt_template = """
Act as a professional options trader generating 3 high-reward, short-term trade ideas for today ({today}). 

Each trade must target stocks like SPY, TSLA, NVDA, AMD, RIOT — or other highly liquid tickers with active options chains.

Criteria:
- Direction: Call or Put
- Strike: Near current price, expiring today or tomorrow (0DTE or 1DTE)
- Entry cost: <$1 (cheap contracts)
- Setup: One of these — Gap Fade, Breakout Retest, Premarket Reversal, Momentum Run, or Catalyst Play (e.g. Earnings, CPI, News)
- Confidence: High, Medium, or Low
- Rationale: 1-2 sentence explanation using today's price action or context (CPI release, earnings reaction, sector momentum, etc.)

Output the results as a **pure JSON array**, with no explanation or commentary. Use this format exactly:

[
  {{
    "ticker": "SPY",
    "setup": "Gap Fade",
    "direction": "Put",
    "strike": 512,
    "expiry": "{today}",
    "entry": 0.40,
    "target": 1.00,
    "stop": 0.20,
    "confidence": "High",
    "rationale": "SPY gapped up after CPI but failed resistance at 512 with sell volume rising."
  }}
]
"""

# Replace placeholder with today's date safely
prompt = prompt_template.replace("{today}", today)

# Request from GPT
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        { "role": "user", "content": prompt }
    ],
    temperature=0.7
)

# Parse JSON from AI response
try:
    trade_data = json.loads(response.choices[0].message.content.strip())
except json.JSONDecodeError:
    raise Exception("Failed to parse GPT output as JSON.")

# Write to file
with open("live_trades.json", "w") as f:
    json.dump(trade_data, f, indent=2)
