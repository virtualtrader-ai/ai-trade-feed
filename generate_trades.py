from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on stocks and options showing breakout volume, earnings beats, or sector shifts."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on fundamentally strong stocks and conservative options with dividends and insider buying."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on stocks and options with catalysts like earnings, FDA, or institutional flows."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on healthcare, utilities, and staples stocks and options during weak markets."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on speculative options with high volatility, short expiries, unusual flow."},
    "person_f": {"name": "The Political Figure Trader", "prompt_overlay": "Focus strictly on trades disclosed by U.S. politicians like Nancy Pelosi. Always state the politician's name and link to disclosure source."}
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

# Ensure profiles initialized
for profile in profiles.values():
    if profile['name'] not in system_metrics["profiles"]:
        system_metrics["profiles"][profile['name']] = {"tokens": 0, "cost_usd": 0}
if "Market Pulse" not in system_metrics["profiles"]:
    system_metrics["profiles"]["Market Pulse"] = {"tokens": 0, "cost_usd": 0}

# Trades per profile
for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite trader.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate exactly 5 stock trades and 5 options trades for today ({today}).

Rules:
- Include "type": "Stock" or "Option"
- Include "estimated_duration" (e.g., "1 day", "1 week", "6 months")
- Include "setup", "direction", "entry", "target", "stop", "confidence"
- Include "source_link" (always include a plausible link or describe where the info came from)
- Each rationale must be at least 8 sentences covering catalysts, technicals, psychology, and for Political Trader always specify politician's name in rationale and source.

Format as strict JSON:
[
  {{
    "ticker": "AAPL",
    "type": "Stock",
    "setup": "Breakout",
    "direction": "Buy",
    "entry": 175.5,
    "target": 180.0,
    "stop": 172.8,
    "confidence": "High",
    "estimated_duration": "3 days",
    "source_link": "https://example.com/news-article",
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
            trade_data = json.loads(raw_response)
            # Check both Stock and Option present
            stocks = [t for t in trade_data if t['type'] == "Stock"]
            options = [t for t in trade_data if t['type'] == "Option"]
            if len(stocks) != 5 or len(options) != 5:
                raise ValueError(f"Expected 5 stock and 5 option trades, got {len(stocks)} stock and {len(options)} option")

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
            print(f"Attempt {attempt+1} failed for {profile['name']}: {e}")
            time.sleep(5)

    if not success:
        profile_usage[profile['name']] = "Failed"
        continue

    with open(f"live_trades_{profile_id}.json", "w") as f:
        json.dump(trade_data, f, indent=2)

# Save reports
with open("usage_report.json", "w") as f:
    json.dump({
        "date": today,
        "total_tokens_used": total_tokens_used,
        "estimated_cost_usd": round(total_tokens_used / 1000 * 0.002, 4),
        "profile_breakdown": profile_usage,
        "cumulative_metrics": system_metrics
    }, f, indent=2)
with open(cumulative_metrics_file, "w") as f:
    json.dump(system_metrics, f, indent=2)
