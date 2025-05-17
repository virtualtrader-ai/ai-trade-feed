from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on momentum breakout setups in Tech, Energy, Crypto. Seek multi-day consolidations with breakout volume."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on conservative swing trades backed by insider buying, dividends, low volatility setups."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on news-driven trades (earnings, FDA, catalysts) with asymmetric reward/risk setups."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on healthcare, utilities, staples. Seek setups that outperform in weak or uncertain markets."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on high IV, speculative short-term option setups (0DTE, 1DTE) with unusual flow."}
}

today = date.today().strftime('%Y-%m-%d')

total_tokens_used = 0
profile_usage = {}

for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite professional stock and options trader.

I need you to generate exactly 10 unique and diverse trade ideas for today ({today}), in the following strict JSON array format only.

IMPORTANT:
- Only return a clean JSON array.
- DO NOT write anything else before or after the JSON.
- Each trade must include all the following fields:
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

Your persona is:
{profile['prompt_overlay']}

Ensure:
- 10 trades.
- JSON format is exactly as shown above.
- Include creative setups, avoid duplicates.
"""

    success = False
    for attempt in range(3):
        try:
            print(f"\n🔄 Attempt {attempt + 1} for {profile['name']}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            raw_response = response.choices[0].message.content.strip()
            if not raw_response:
                raise ValueError("⚠️ Empty response from GPT")

            print(f"✅ Raw response sample for {profile['name']}:\n{raw_response[:300]}...")

            trade_data = json.loads(raw_response)
            if len(trade_data) != 10:
                raise ValueError(f"❗ Expected 10 trades, got {len(trade_data)}")

            tokens_used = response.usage.total_tokens
            profile_usage[profile['name']] = tokens_used
            total_tokens_used += tokens_used
            success = True
            break

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    if not success:
        profile_usage[profile['name']] = "Failed"
        continue

    # Save file
    filename = f"live_trades_{profile_id}.json"
    with open(filename, "w") as f:
        json.dump(trade_data, f, indent=2)

# Save usage report
usage_report = {
    "date": today,
    "total_tokens_used": total_tokens_used,
    "estimated_cost_usd": round(total_tokens_used / 1000 * 0.002, 4),
    "profile_breakdown": profile_usage
}

with open("usage_report.json", "w") as f:
    json.dump(usage_report, f, indent=2)

print("✅ All files and usage report saved.")
