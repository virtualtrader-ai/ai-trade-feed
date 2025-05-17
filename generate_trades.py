from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on stocks showing unusual breakout volume, recent earnings beats, or sector momentum shifts."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on fundamentally strong companies with dividend support, low beta, and recent insider buying or upgrades."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on stocks with upcoming earnings, FDA events, regulatory rulings, or notable institutional flows."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on healthcare, utilities, or consumer staples stocks outperforming during market pullbacks or high VIX environments."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on speculative small caps with unusual options flow, high implied volatility, or rumor-driven moves."}
}

today = date.today().strftime('%Y-%m-%d')

total_tokens_used = 0
profile_usage = {}
cumulative_metrics_file = "system_metrics.json"

# Load system metrics if exist
if os.path.exists(cumulative_metrics_file):
    with open(cumulative_metrics_file) as f:
        system_metrics = json.load(f)
else:
    system_metrics = {"total_tokens": 0, "total_cost_usd": 0, "profiles": {p['name']: {"tokens": 0, "cost_usd": 0} for p in profiles.values()}}

for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite stock and options trader.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate exactly 10 unique and diverse trade ideas for today ({today}).

Important:
- Include catalysts like news, earnings, flow data, or economic reports.
- Mention relevant sectors, volatility, insider buying, or macro risks.
- Use this **strict JSON array format only**, with NO explanations outside JSON:
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
    "rationale": "SPY opened weak after CPI data indicating persistent inflation. The rejection at key resistance combined with high put volume and deteriorating breadth makes this a high probability short opportunity fitting the persona strategy. Additionally, macro sentiment is risk-off today following Fed comments, increasing the setup quality."
  }}
]

Ensure:
- JSON format as above.
- Include creative setups, avoid duplicates.
- Each rationale must be at least **5 detailed sentences**, referencing catalysts, technical, and market psychology.
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
                raise ValueError("Empty response from GPT")

            print(f"✅ Raw response sample for {profile['name']}:\n{raw_response[:300]}...")

            trade_data = json.loads(raw_response)
            if len(trade_data) != 10:
                raise ValueError(f"Expected 10 trades, got {len(trade_data)}")

            tokens_used = response.usage.total_tokens
            profile_usage[profile['name']] = {
                "tokens_this_run": tokens_used,
                "estimated_cost_this_run": round(tokens_used / 1000 * 0.002, 4)
            }

            # Update cumulative metrics
            system_metrics["total_tokens"] += tokens_used
            system_metrics["total_cost_usd"] += tokens_used / 1000 * 0.002
            system_metrics["profiles"][profile['name']]["tokens"] += tokens_used
            system_metrics["profiles"][profile['name']]["cost_usd"] += tokens_used / 1000 * 0.002

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
    "profile_breakdown": profile_usage,
    "cumulative_metrics": system_metrics
}

with open("usage_report.json", "w") as f:
    json.dump(usage_report, f, indent=2)

with open(cumulative_metrics_file, "w") as f:
    json.dump(system_metrics, f, indent=2)

print("✅ All files, usage report, and system metrics saved.")
