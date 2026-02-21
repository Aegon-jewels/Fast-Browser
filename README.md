# Fast-Browser 🚀

A **Playwright Firefox** browser pre-configured for fast, clean, ad-free browsing — optimized for **IRCTC ticket booking**.

## Features
- 🕵️ **Stealth Mode** — Bypasses Akamai/Cloudflare bot detection (`playwright-stealth`)
- 🚫 **Smart Ad Blocker** — Blocks 30+ ad/tracker domains, whitelists IRCTC & payment gateways
- 🍪 **Third-party cookies blocked** — Ads can't track; IRCTC session works fine
- 🗑️ **Cache fully disabled** — No stale data, always fresh loads
- 📺 **Full HD 1920×1080** — Proper resolution so all UI elements show correctly
- 🔓 **HTTPS errors ignored** — No more "Connection not secure" warnings
- 🇮🇳 **Indian locale + IST timezone** — en-IN locale, Asia/Kolkata timezone

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/Aegon-jewels/Fast-Browser.git
cd Fast-Browser

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Firefox for Playwright
playwright install firefox

# 4. Run!
python3 irctc_browser.py
```

## What Was Fixed (v3)

| Problem | Root Cause | Fix |
|---|---|---|
| "Unable to Process Request" error | Akamai bot detection blocked Playwright | `playwright-stealth` hides automation fingerprints |
| "Connection not secured" | Mixed content / SSL cert mismatch | `ignore_https_errors=True` + mixed content unblocked |
| Bad resolution / broken layout | No viewport set | `1920x1080` viewport + screen size set |
| UI elements missing | Ad blocker too aggressive | IRCTC + Akamai CDN domains whitelisted |

## How the Smart Ad Blocker Works

```
Request comes in
      ↓
Is it irctc.co.in / akamaized.net / razorpay etc? → ✅ ALLOW
      ↓
Is it doubleclick / taboola / criteo etc?          → ❌ BLOCK
      ↓
Everything else                                    → ✅ ALLOW
```

## IRCTC Booking Tips
- Login **10–15 min before** tatkal window opens
- **Pre-fill all passenger details**
- Solve **CAPTCHA manually**
- Use **UPI** — fastest payment method
- Do NOT change `cookieBehavior` to `2` — it will log you out!

## Requirements
- Python 3.8+
- Linux / Windows / macOS
- `playwright` + `playwright-stealth`

## License
MIT
