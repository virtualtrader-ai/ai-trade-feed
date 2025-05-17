from openai import OpenAI
import json
import os
from datetime import date
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

profiles = {
    "person_a": {"name": "Luna - The Momentum Trader", "prompt_overlay": "Focus on stocks and options with breakout patterns, sector momentum, and volume spikes."},
    "person_b": {"name": "Mark - The Conservative Investor", "prompt_overlay": "Focus on fundamentally strong stocks and safe option strategies."},
    "person_c": {"name": "Riley - The Catalyst Trader", "prompt_overlay": "Focus on stocks and options with upcoming catalysts like earnings, FDA approvals."},
    "person_d": {"name": "Zara - The Defensive Strategist", "prompt_overlay": "Focus on stocks and options in safe sectors like healthcare, utilities, during uncertainty."},
    "person_e": {"name": "Leo - The High-Risk Options Specialist", "prompt_overlay": "Focus on high-risk speculative options plays with aggressive setups."},
    "person_f": {"name": "The Political Figure Trader", "prompt_overlay": "Focus on replicating trades disclosed by U.S. politicians like Nancy Pelosi. Always include the politician's name and disclosure link."}
}

today = date.today().strftime('%Y-%m-%d')

# Trades per profile
for profile_id, profile in profiles.items():
    prompt = f"""
You are an elite trader.

For persona {profile['name']}:
{profile['prompt_overlay']}

Generate exactly 5 stock trades and 5 options trades for today ({today}).

For each trade:
- Include "ticker", "type" ("Stock" or "Option"), "setup", "direction", "entry", "target", "stop", "confidence"
- Include "estimated_duration" (e.g., "1 day", "1 week", "6 months")
- Include "rationale": At least 8 sentences.
- Include "source_link" or "source_description" (If no known source, say "AI Analysis")
- For Political Figure Trader: Also include "politician": Name of politician & reference disclosure

Output strict JSON like this:
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
    "estimated_duration": "1-3 days",
    "source_link": "https://example.com/news",
    "rationale": "...",
    "politician": "Nancy Pelosi" (only for political trades, otherwise omit)
  }}
]
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    raw_response = response.choices[0].message.content.strip()
    with open(f"live_trades_{profile_id}.json", "w") as f:
        json.dump(json.loads(raw_response), f, indent=2)
