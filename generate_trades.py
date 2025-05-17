from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on momentum stocks and options showing unusual breakout volume, recent earnings beats, or sector momentum shifts."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on fundamentally strong stocks and conservative option strategies backed by insider buying, dividends, and low volatility setups."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on stocks and options with upcoming earnings, FDA events, regulatory rulings, or notable institutional flows."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on stocks and options in healthcare, utilities, and staples that outperform in weak or uncertain markets."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on speculative options setups with high implied volatility, short-dated expiries, and unusual options flow."},
    "person_f": {"name": "The Political Figure Trader", "prompt_overlay": "Focus on trades inspired by recent financial disclosures of U.S. politicians, such as Nancy Pelosi, analyzing and mimicking their trading behavior. Always specify the politician's name and include the source of disclosure."}
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

# Market Pulse
try:
    market_pulse_prompt = f"""
You are a global market strategist.

Generate a detailed, organized, actionable Market Pulse report for today ({today}).

Include:
1. General Market Sentiment
2. Key Economic Drivers
3. Sector Leadership & Themes (mention tickers)
4. Geopolitical & Macro Risks
5. Notable Institutional & Political Activity (with links if available)
6. Short-Term Trading Bias (what to watch intraday)
7. Important Calendar Events (include dates)

Be specific. Mention stocks, sectors, flows, political actions. If possible, include **links to sources or reports used**.
Target length: 500-700 words.
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

except Exception as e:
    profile_usage["Market Pulse"] = "Failed"

# Trades per profile
for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite trader.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate 5 stock trades and 5 options trades for today ({today}).

Rules:
- Specify type as "Stock" or "Option".
- Each must have an "estimated_duration" field (example: "1 day", "2 weeks", "6 months").
- Each must have a "source_link" or "source_description" explaining where the information came from.
- For Political Figure Trader: include the politician's name.
- Include catalysts like news, earnings, political disclosures, insider buying, unusual flow, etc.
- Each rationale must be at least 8 detailed sentences covering all factors.

Format as strict JSON:
[
  {{
    "ticker": "SPY",
    "type": "Option",
    "setup": "Gap Fade Reversal",
    "direction": "Put",
    "strike": 512,
    "expiry": "{today}",
    "entry": 0.45,
    "target": 1.20,
    "stop": 0.20,
    "confidence": "High",
    "estimated_duration": "1 day",
    "source_link": "https://example.com",
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
