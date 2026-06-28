# Claude Code Quota Statusline

A tiny [Claude Code](https://claude.com/claude-code) statusline for **subscription (Pro/Max) users**.

It shows how much of your **usage limits** are left — the rolling **5-hour window** and the **weekly (7-day) window** — instead of the per-token dollar estimates that tools like `ccusage` show (which don't mean anything on a subscription plan).

![Claude Code quota statusline preview](preview.png)

```
🤖 Opus 4.8 | ⏳ 5h 🟢82% left (4h21m) | 📅 wk 🟢78% left (3d19h) | 🧠 12%
```

| Segment | Meaning |
| --- | --- |
| 🤖 | Active model |
| ⏳ 5h | Remaining quota in the rolling 5-hour window + time until reset (h/m) |
| 📅 wk | Remaining quota in the weekly (7-day) window + time until reset (d/h) |
| 🧠 | Current context-window usage |
| 🟢 / 🟡 / 🔴 | >50% / 20–50% / <20% remaining |

## How it works

Claude Code pipes a JSON payload to the statusline command on stdin. On recent
versions (verified on `2.1.195`) that payload includes a `rate_limits` field:

```json
{
  "rate_limits": {
    "five_hour": { "used_percentage": 18, "resets_at": 1782630000 },
    "seven_day": { "used_percentage": 22, "resets_at": 1782943200 }
  }
}
```

This is the same data the `/usage` command shows. The script reads it and renders
the remaining percentages. No network calls, no API key, no dependencies — just
Python 3 (standard library only).

## Install

1. Save `statusline-quota.py` somewhere, e.g.:

   ```bash
   mkdir -p ~/.claude/scripts
   curl -fsSL https://raw.githubusercontent.com/luckbug0817/claude-code-quota-statusline/main/statusline-quota.py \
     -o ~/.claude/scripts/statusline-quota.py
   ```

2. Point your statusline at it in `~/.claude/settings.json`:

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 /ABSOLUTE/PATH/TO/statusline-quota.py"
     }
   }
   ```

3. The statusline updates on the next refresh.

> **Note:** `rate_limits` is only injected once your session has received it from
> the API. If you see `📊 usage limits not available yet`, send a few messages and
> it will populate.

## Chinese labels

Set `CC_QUOTA_LANG=zh` for Chinese labels (default is English):

```json
{
  "statusLine": {
    "type": "command",
    "command": "CC_QUOTA_LANG=zh python3 /path/to/statusline-quota.py"
  }
}
```

```
🤖 Opus 4.8 | ⏳ 5h 🟢76%剩 (4h12m重置) | 📅 周 🟢78%剩 (3d19h重置) | 🧠 9%
```

## Debugging

Set `CC_QUOTA_DEBUG` to a file path to dump the raw stdin payload so you can see
exactly what Claude Code is sending:

```json
{
  "statusLine": {
    "type": "command",
    "command": "CC_QUOTA_DEBUG=~/cc-statusline-input.json python3 /path/to/statusline-quota.py"
  }
}
```

## License

MIT — see [LICENSE](LICENSE).
