
import openai
import json
from datetime import date

# Get your OpenAI API key from GitHub Secrets
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt to generate trade ideas
prompt = (
    "Generate 3 high-risk, high-reward options trade ideas for today ({today}). "
    "Each idea should include: ticker, setup, direction (Call or Put), strike price, expiry date, "
    "estimated entry, target, stop loss, confidence level (High/Medium/Low), and a short rationale."
).format(today=date.today().strftime("%Y-%m-%d"))

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=600
)

# Parse the result
ideas = response['choices'][0]['message']['content'].strip()

# Basic JSON formatting assumption (you may need more robust parsing depending on output style)
# We'll simulate proper formatting for now
trade_data = [
    {
        "ticker": "SPY",
        "setup": "CPI Reversal",
        "direction": "Put",
        "strike": 510,
        "expiry": date.today().strftime("%Y-%m-%d"),
        "entry": 0.40,
        "target": 1.00,
        "stop": 0.20,
        "confidence": "High",
        "rationale": "SPY rejected CPI highs with bearish volume."
    },
    {
        "ticker": "TSLA",
        "setup": "Breakout",
        "direction": "Call",
        "strike": 185,
        "expiry": date.today().strftime("%Y-%m-%d"),
        "entry": 0.45,
        "target": 1.20,
        "stop": 0.25,
        "confidence": "Medium",
        "rationale": "TSLA gaining momentum post earnings beat."
    },
    {
        "ticker": "RIOT",
        "setup": "Crypto Sentiment",
        "direction": "Call",
        "strike": 10,
        "expiry": date.today().strftime("%Y-%m-%d"),
        "entry": 0.22,
        "target": 0.60,
        "stop": 0.10,
        "confidence": "Medium",
        "rationale": "RIOT rebounding with Bitcoin volatility spike."
    }
]

# Save to JSON
with open("live_trades.json", "w") as f:
    json.dump(trade_data, f, indent=2)
