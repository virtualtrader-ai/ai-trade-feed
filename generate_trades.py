from openai import OpenAI
import json
import os
from datetime import date
import time

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

IMPORTANT: 
- ONLY reply with a pure JSON array.
- If you cannot find 10 trades, return at least 3.
- DO NOT leave response blank or provide explanations.
- JSON must include:
    - ticker, setup, direction, strike, expiry, entry, target, stop, confidence, rationale.
    - Rationale must be 3-5 sentences explaining the trade setup, catalyst, and why it fits the persona.

Example:
[
  {{
    "ticker": "SPY",
    "setup": "Gap Fade Reversal",
    "direction": "Put",
    "strike": 512,
    "expiry": "{today}",
    "entry": 0.45,
    "target": 1.20,
    "stop": 0.20,
    "confidence": "High",
    "rationale": "SPY opened with a weak gap following CPI data, showing rejection at premarket highs. Coupled with increasing put volume and soft breadth, this creates a high probability fade fitting the momentum strategy."
  }}
]
"""

    success = False
    for attempt in range(3):
        try:
            print(f"\n🔄 Attempt {attempt + 1} for {profile['name']}")
            response = client.chat.completions.create(
               model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            raw_response = response.choices[0].message.content.strip()
            if not raw_response:
                raise ValueError("⚠️ Empty response from GPT")

            # Debug log the raw output if needed
            print(f"✅ Received response for {profile['name']}:")
            print(raw_response[:500] + "...")  # Print first 500 chars

            trade_data = json.loads(raw_response)
            success = True
            break  # Success, exit loop

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retry

    if not success:
        raise Exception(f"❗ Failed after 3 attempts for {profile['name']}")

    # Save profile-specific JSON
    filename = f"live_trades_{profile_id}.json"
    with open(filename, "w") as f:
        json.dump(trade_data, f, indent=2)
    print(f"📦 Saved {filename}")
