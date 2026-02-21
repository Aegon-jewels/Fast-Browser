# Fast-Browser 🚀

A **Playwright Firefox** browser pre-configured for fast, clean, and ad-free browsing — optimized for **IRCTC ticket booking**.

## Features
- 🚫 **Ad Blocker** — Blocks 30+ known ad/tracker networks via network route interception
- 🍪 **Third-party cookies blocked** — Ads can't track you, but IRCTC session cookies still work
- 🗑️ **Cache fully disabled** — No stale data, always fresh page loads
- 🛡️ **Strict Tracking Protection** — Firefox ETP set to strict mode
- ⚡ **Performance tuned** — Max connections increased for faster loading
- 🔕 **No popups** — Geo, notifications, and push disabled

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/Aegon-jewels/Fast-Browser.git
cd Fast-Browser

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Firefox for Playwright
playwright install firefox

# 4. Run the script
python3 irctc_browser.py
```

## How It Works

| Feature | Method |
|---|---|
| Disable disk/memory cache | `firefox_user_prefs` → `browser.cache.*: False` |
| Block 3rd-party cookies | `cookieBehavior: 1` |
| Ad blocker | `page.route()` intercepts & aborts ad domains |
| Strict tracking protection | Firefox built-in ETP set to `strict` |
| Clear old cookies | `context.clear_cookies()` on every launch |

## IRCTC Booking Tips
- Login **10–15 minutes before** tatkal window opens
- **Fill passenger details in advance**
- Solve **CAPTCHA manually**
- Use **UPI payment** — fastest option
- Do NOT set `cookieBehavior: 2` (blocks ALL cookies — will log you out!)

## Requirements
- Python 3.8+
- Linux / Windows / macOS
- Playwright + Firefox

## License
MIT
