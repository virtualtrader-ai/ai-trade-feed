# Generate Market Pulse and track tokens
try:
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

    # Update system metrics for market pulse
    if "Market Pulse" not in system_metrics["profiles"]:
        system_metrics["profiles"]["Market Pulse"] = {"tokens": 0, "cost_usd": 0}

    system_metrics["total_tokens"] += pulse_tokens_used
    system_metrics["total_cost_usd"] += pulse_tokens_used / 1000 * 0.002
    system_metrics["profiles"]["Market Pulse"]["tokens"] += pulse_tokens_used
    system_metrics["profiles"]["Market Pulse"]["cost_usd"] += pulse_tokens_used / 1000 * 0.002

    # Log in profile_usage too
    profile_usage["Market Pulse"] = {
        "tokens_this_run": pulse_tokens_used,
        "estimated_cost_this_run": round(pulse_tokens_used / 1000 * 0.002, 4)
    }

    print(f"✅ Market pulse report saved. Tokens used: {pulse_tokens_used}")

except Exception as e:
    print(f"❌ Failed to generate market pulse: {e}")
    profile_usage["Market Pulse"] = "Failed"
