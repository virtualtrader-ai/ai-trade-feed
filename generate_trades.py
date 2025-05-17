from openai import OpenAI
import json
import os
from datetime import date

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {
        "name": "Luna - The Momentum Trader",
        "prompt_overlay": "Focus on momentum breakout setups in Tech, Energy, Crypto. Seek multi-day consolidations with breakout volume."
    },
    "person_b": {
        "name": "Mark - The Conservative Investor",
        "prompt_overlay": "Focus on conservative swing trades backed by insider buying, dividends, low volatility setups."
    },
    "person_c": {
        "name": "Riley - The Catalyst Trader",
        "prompt_overlay": "Focus on news-driven trades (earnings, FDA, catalysts) with asymmetric reward/risk setups."
    },
    "person_d": {
        "name": "Zara - The Defensive Strategist",
        "prompt_overlay": "Focus on healthcare, utilities, staples. Seek setups that outperform in weak or uncertain markets."
    },
    "person_e": {
        "name": "Leo - The High-Risk Options Specialist",
        "prompt_overlay": "Focus on high IV, speculative short-term option setups (0DTE, 1DTE) with unusual flow."
    }
}

today = date.today().strftime('%Y-%m-%d')

for profile_id, profile in profiles.items():
    prompt = f"""
Act as a professional options and stock trader. Generate 10 high-reward trade recommendations for today ({today}).

Persona Focus:
{profile['prompt_overlay']}

Criteria:
- Scan all US stocks tradable on Robinhood (assume all US tickers).
- Include Ticker, Setup, Direction (Call or Put if applicable), Strike (if options), Expiry (if applicable), Entry, Target, Stop, Confidence (High/Medium/Low).
- Provide a **detailed multi-sentence rationale explaining the setup, catalyst, and why it fits the persona.**

Output a pure JSON array only.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        trade_data = json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        raise Exception(f"Failed to parse response for {profile['name']}")

    with open(f"live_trades_{profile_id}.json", "w") as f:
        json.dump(trade_data, f, indent=2)
