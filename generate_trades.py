from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on momentum breakout setups..."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on conservative swing trades..."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on news-driven trades..."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on healthcare, utilities..."},
    "person_e": {"name": "Leo - The Options Specialist", "prompt_overlay": "Focus on high IV, speculative options..."}
}

today = date.today().strftime('%Y-%m-%d')

total_tokens_used = 0
profile_usage = {}

for profile_id, profile in profiles.items():
    prompt = f"""
Act as a professional trader.

Generate exactly 10 high-reward trade recommendations for today ({today}).

{profile['prompt_overlay']}

IMPORTANT:
- Return exactly 10 trades.
- Use pure JSON array only.
- Do not explain anything.
"""

    success = False
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            raw_response = response.choices[0].message.content.strip()
            if not raw_response:
                raise ValueError("Empty response from GPT")

            trade_data = json.loads(raw_response)
            success = True

            tokens_used = response.usage.total_tokens
            profile_usage[profile['name']] = tokens_used
            total_tokens_used += tokens_used
            break

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    if not success:
        profile_usage[profile['name']] = "Failed"
        continue

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
