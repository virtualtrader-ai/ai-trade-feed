from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "..."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "..."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "..."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "..."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "..."},
    "person_f": {"name": "The Political Figure Trader", "prompt_overlay": "Focus on trades inspired by recent financial disclosures of U.S. politicians, especially congress members such as Nancy Pelosi, analyzing the patterns and sectors they favor."}
}

today = date.today().strftime('%Y-%m-%d')
total_tokens_used = 0
profile_usage = {}
cumulative_metrics_file = "system_metrics.json"

# Load or create system metrics
if os.path.exists(cumulative_metrics_file):
    with open(cumulative_metrics_file) as f:
        system_metrics = json.load(f)
else:
    system_metrics = {"total_tokens": 0, "total_cost_usd": 0, "profiles": {}}

# Ensure all profiles are initialized
for profile in profiles.values():
    if profile['name'] not in system_metrics["profiles"]:
        system_metrics["profiles"][profile['name']] = {"tokens": 0, "cost_usd": 0}
if "Market Pulse" not in system_metrics["profiles"]:
    system_metrics["profiles"]["Market Pulse"] = {"tokens": 0, "cost_usd": 0}

# Generate Market Pulse
try:
    market_pulse_prompt = f"""
You are a professional market strategist.

Generate a concise, insightful, and actionable market pulse report for today ({today}).

Include:
- General sentiment (bullish, bearish, neutral)
- Key macroeconomic drivers
- Sector rotations or themes
- Geopolitical risks
- Institutional activity
- Important political actions impacting markets

Write in TLDR style, no more than 200 words.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": market_pulse_prompt}],
        temperature=0.3
    )
    pulse_text = response.choices[0].message.content.strip()
    with open("market_pulse.json", "w") as f:
        json.dump({"date": today, "pulse": pulse_text}, f, indent=2)

    pulse_tokens_used = response.usage.total_tokens
    total_tokens_used += pulse_tokens_used
    profile_usage["Market Pulse"] = {
        "tokens_this_run": pulse_tokens_used,
        "estimated_cost_this_run": round(pulse_tokens_used / 1000 * 0.002, 4)
    }
    system_metrics["total_tokens"] += pulse_tokens_used
    system_metrics["total_cost_usd"] += pulse_tokens_used / 1000 * 0.002
    system_metrics["profiles"]["Market Pulse"]["tokens"] += pulse_tokens_used
    system_metrics["profiles"]["Market Pulse"]["cost_usd"] += pulse_tokens_used / 1000 * 0.002

    print(f"✅ Market Pulse generated. Tokens used: {pulse_tokens_used}")
except Exception as e:
    print(f"❌ Failed to generate Market Pulse: {e}")
    profile_usage["Market Pulse"] = "Failed"

# Generate trades per profile
for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite stock and options trader.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate exactly 10 unique, creative, and diverse trade ideas for today ({today}).

Important:
- Include catalysts: news, earnings, insider buying, political trades, flow data, macro.
- Each rationale must be at least 5 detailed sentences, referencing catalysts, technicals, and psychology.
- Format as strict JSON:
[
  {{
    "ticker": "SPY",
    "setup": "Gap Fade Reversal with CPI catalyst",
    "direction": "Put",
    "strike": 512,
    "expiry": "{today}",
    "entry": 0.45,
    "target": 1.20,
    "stop": 0.20,
    "confidence": "High",
    "rationale": "..."
  }}
]
"""

    success = False
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            raw_response = response.choices[0].message.content.strip()
            if not raw_response:
                raise ValueError("Empty response from GPT")

            trade_data = json.loads(raw_response)
            if len(trade_data) != 10:
                raise ValueError(f"Expected 10 trades, got {len(trade_data)}")

            tokens_used = response.usage.total_tokens
            profile_usage[profile['name']] = {
                "tokens_this_run": tokens_used,
                "estimated_cost_this_run": round(tokens_used / 1000 * 0.002, 4)
            }
            system_metrics["total_tokens"] += tokens_used
            system_metrics["total_cost_usd"] += tokens_used / 1000 * 0.002
            system_metrics["profiles"][profile['name']]["tokens"] += tokens_used
            system_metrics["profiles"][profile['name']]["cost_usd"] += tokens_used / 1000 * 0.002

            total_tokens_used += tokens_used
            success = True
            break

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} for {profile['name']} failed: {e}")
            time.sleep(5)

    if not success:
        profile_usage[profile['name']] = "Failed"
        continue

    filename = f"live_trades_{profile_id}.json"
    with open(filename, "w") as f:
        json.dump(trade_data, f, indent=2)

# Save usage report and cumulative metrics
usage_report = {
    "date": today,
    "total_tokens_used": total_tokens_used,
    "estimated_cost_usd": round(total_tokens_used / 1000 * 0.002, 4),
    "profile_breakdown": profile_usage,
    "cumulative_metrics": system_metrics
}

with open("usage_report.json", "w") as f:
    json.dump(usage_report, f, indent=2)
with open(cumulative_metrics_file, "w") as f:
    json.dump(system_metrics, f, indent=2)

print("✅ All trades, reports, and metrics saved.")
