from openai import OpenAI
import json
import os
from datetime import date
import time
import re

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

Output ONLY valid JSON inside triple backticks like this:
```json
[your JSON here]
