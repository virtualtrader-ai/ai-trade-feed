from openai import OpenAI
import json
import os
from datetime import date
import time
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = date.today().strftime('%Y-%m-%d')

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on stocks and options with breakout patterns, sector momentum, and volume spikes."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on fundamentally strong stocks and safe option strategies."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on stocks and options with upcoming catalysts like earnings, FDA approvals."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on stocks and options in safe sectors like healthcare, utilities, during uncertainty."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on high-risk speculative options plays with aggressive setups."},
    "person_f": {"name": "The Political Figure Trader", "prompt_overlay": "Focus strictly on replicating trades disclosed by U.S. politicians or their relatives. Include politician name, role, and official disclosure source link."}
}

total_tokens = 0
cost_per_1k = 0.002  # gpt-3.5-turbo
profile_stats = []

for profile_id, profile in profiles.items():
    prompt = f"""You are an elite Wall Street trader generating hyper-accurate trade recommendations.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate exactly 5 stock trades and 5 options trades for today ({today}).

For each trade:
- Include "ticker", "type" ("Stock" or "Option"), "setup", "direction", "entry", "target", "stop", "confidence"
- Include "estimated_duration" (e.g., "1 day", "1 week", "6 months")
- Include "rationale": Minimum 8 sentences. Explain the market setup, technical/fundamental reasoning, risks, and expected move.
- Include "source_link" (If no real source, say "AI Analysis")
- For Political Figure Trader only: Include "politician": Name and role (e.g., Nancy Pelosi, House Speaker) and "disclosure_link" (realistic source link or disclosure page)

Only output valid JSON inside triple backticks like this:
```json
[your JSON here]
```
Do not add any explanations, comments, or text outside the JSON block.
Ensure the JSON is valid and parsable.
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
            usage = response.usage
            tokens = usage.total_tokens
            total_tokens += tokens

            json_block_match = re.search(r"```json\s*(.*?)\s*```", raw_response, re.DOTALL)
            if json_block_match:
                clean_json = json_block_match.group(1)
            else:
                clean_json = raw_response

            trade_data = json.loads(clean_json)

            stocks = [t for t in trade_data if t.get('type', '').lower() == "stock"]
            options = [t for t in trade_data if t.get('type', '').lower() == "option"]
            if len(stocks) != 5 or len(options) != 5:
                raise ValueError(f"Expected 5 stock and 5 option trades, got {len(stocks)} stock and {len(options)} option")

            with open(f"live_trades_{profile_id}.json", "w") as f:
                json.dump(trade_data, f, indent=2)

            profile_stats.append({
                "id": profile_id,
                "name": profile["name"],
                "tokens_used_this_run": tokens
            })

            print(f"✅ Successfully generated trades for {profile['name']}")
            success = True
            break

        except Exception as e:
            print(f"Attempt {attempt+1} failed for {profile['name']}: {e}")
            time.sleep(5)

    if not success:
        print(f"❌ Failed to generate trades for {profile['name']} after 3 attempts.")

# Save usage_report.json
usage_report = {
    "date": today,
    "total_tokens_used": total_tokens,
    "estimated_cost": round(total_tokens / 1000 * cost_per_1k, 5),
    "profiles": []
}

# Update system_metrics.json
try:
    with open("system_metrics.json", "r") as f:
        system_metrics = json.load(f)
except FileNotFoundError:
    system_metrics = {
        "total_tokens_used": 0,
        "total_cost": 0,
        "profiles": {}
    }

for p in profile_stats:
    name = p["name"]
    tokens = p["tokens_used_this_run"]
    cost = round(tokens / 1000 * cost_per_1k, 5)

    usage_report["profiles"].append({
        "name": name,
        "tokens_used_this_run": tokens,
        "total_tokens_used": system_metrics["profiles"].get(name, {}).get("total_tokens_used", 0) + tokens,
        "total_cost": round(system_metrics["profiles"].get(name, {}).get("total_cost", 0) + cost, 5)
    })

    if name not in system_metrics["profiles"]:
        system_metrics["profiles"][name] = {"total_tokens_used": 0, "total_cost": 0}
    system_metrics["profiles"][name]["total_tokens_used"] += tokens
    system_metrics["profiles"][name]["total_cost"] += cost

system_metrics["total_tokens_used"] += total_tokens
system_metrics["total_cost"] += round(total_tokens / 1000 * cost_per_1k, 5)

with open("usage_report.json", "w") as f:
    json.dump(usage_report, f, indent=2)

with open("system_metrics.json", "w") as f:
    json.dump(system_metrics, f, indent=2)

print("📊 Usage and system metrics updated.")
