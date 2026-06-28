#!/usr/bin/env python3
"""
Claude Code statusline for subscription (Pro/Max) users.

Shows how much of your rolling usage limits remain — the 5-hour window and the
weekly (7-day) window — instead of meaningless per-token dollar estimates.

Data comes from the JSON Claude Code pipes to the statusline command on stdin,
specifically `rate_limits.{five_hour,seven_day}` (same source as `/usage`).

Output example:
    🤖 Opus 4.8 | ⏳ 5h 🟢82% left (4h21m) | 📅 wk 🟢78% left (91h) | 🧠 12%

Set CC_QUOTA_DEBUG=/path/to/file.json to dump the raw stdin payload for
inspection.
"""
import sys, json, time, os


def fmt_reset(ts):
    """Return a compact 'until reset' string like '4h21m' or '12m'."""
    if not ts:
        return ""
    ts = float(ts)
    if ts > 1e12:  # milliseconds
        ts /= 1000.0
    secs = int(ts - time.time())
    if secs <= 0:
        return ""
    h, m = secs // 3600, (secs % 3600) // 60
    return f"{h}h{m}m" if h else f"{m}m"


def window_segment(emoji, label, win):
    """Format one usage window (5h / weekly) as 'emoji label 🟢NN% left (reset)'."""
    if not win:
        return None
    used = win.get("used_percentage")
    if used is None:
        return None
    left = max(0, 100 - used)
    icon = "🟢" if left > 30 else ("🟡" if left > 10 else "🔴")
    s = f"{emoji} {label} {icon}{left:.0f}% left"
    reset = fmt_reset(win.get("resets_at"))
    if reset:
        s += f" ({reset})"
    return s


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("🤖 …")
        return

    debug_path = os.environ.get("CC_QUOTA_DEBUG")
    if debug_path:
        try:
            with open(os.path.expanduser(debug_path), "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    parts = []

    model = (data.get("model") or {}).get("display_name") or "Claude"
    parts.append(f"🤖 {model}")

    rl = data.get("rate_limits") or {}
    s5 = window_segment("⏳", "5h", rl.get("five_hour"))
    s7 = window_segment("📅", "wk", rl.get("seven_day"))
    if s5:
        parts.append(s5)
    if s7:
        parts.append(s7)
    if not s5 and not s7:
        parts.append("📊 usage limits not available yet")

    cw = data.get("context_window") or {}
    size = cw.get("context_window_size")
    cur = (cw.get("current_usage") or {}).get("input_tokens")
    if size and cur is not None:
        parts.append(f"🧠 {cur / size * 100:.0f}%")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
