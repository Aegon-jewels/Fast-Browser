import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # Bypasses Akamai bot detection

# ─────────────────────────────────────────────────────────────
# AD BLOCKER: Only block confirmed ad/tracker domains
# ─────────────────────────────────────────────────────────────
AD_DOMAINS = [
    "googlesyndication.com", "doubleclick.net", "googleadservices.com",
    "adservice.google.com", "amazon-adsystem.com", "ads.yahoo.com",
    "advertising.com", "adform.net", "adnxs.com", "pubmatic.com",
    "openx.net", "rubiconproject.com", "scorecardresearch.com",
    "quantserve.com", "adzerk.net", "taboola.com", "outbrain.com",
    "criteo.com", "bidswitch.net", "moatads.com", "yieldmanager.com",
    "adroll.com", "casalemedia.com", "smartadserver.com",
    "pagead2.googlesyndication.com", "cdn.adnxs.com",
    "prebid.org", "ib.adnxs.com",
]

# ─────────────────────────────────────────────────────────────
# WHITELIST: These domains are ALWAYS allowed
# (IRCTC servers, CDNs, Indian payment gateways)
# ─────────────────────────────────────────────────────────────
WHITELIST_DOMAINS = [
    "irctc.co.in",
    "indianrail.gov.in",
    "irctcconnect.in",
    "akamaized.net",       # IRCTC uses Akamai CDN for assets
    "akamai.net",
    "edgekey.net",
    "razorpay.com",
    "payu.in",
    "paytm.com",
    "billdesk.com",
    "sbi.co.in",
    "hdfcbank.com",
    "icicibank.com",
    "npci.org.in",         # UPI payments
    "upi.npci.org.in",
]


async def ad_blocker(route, request):
    """Smart ad blocker: whitelist IRCTC/CDN first, then block ad domains."""
    url = request.url

    # STEP 1: Always allow whitelisted domains
    if any(safe in url for safe in WHITELIST_DOMAINS):
        await route.continue_()
        return

    # STEP 2: Block known ad/tracker domains
    if any(ad in url for ad in AD_DOMAINS):
        print(f"[BLOCKED AD]  {url[:90]}")
        await route.abort()
        return

    # STEP 3: Allow everything else
    await route.continue_()


async def main():
    async with async_playwright() as p:

        # ─────────────────────────────────────────────────────────────
        # LAUNCH FIREFOX
        # ─────────────────────────────────────────────────────────────
        browser = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                # COOKIES: block third-party only (IRCTC session still works)
                "network.cookie.cookieBehavior": 1,

                # DISABLE ALL CACHE
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": False,
                "browser.cache.offline.enable": False,
                "network.http.use-cache": False,
                "browser.sessionstore.privacy_level": 2,

                # TRACKING PROTECTION (social + crypto only, NOT fingerprinting
                # because stealth handles that better)
                "privacy.trackingprotection.enabled": True,
                "privacy.trackingprotection.socialtracking.enabled": True,
                "privacy.trackingprotection.cryptomining.enabled": True,
                # NOTE: fingerprinting protection OFF — stealth_async handles it
                "privacy.trackingprotection.fingerprinting.enabled": False,

                # DISABLE TELEMETRY
                "toolkit.telemetry.enabled": False,
                "datareporting.healthreport.uploadEnabled": False,
                "browser.ping-centre.telemetry": False,

                # PERFORMANCE
                "network.http.max-connections": 900,
                "network.http.max-persistent-connections-per-server": 10,

                # DISABLE ANNOYING POPUPS
                "geo.enabled": False,
                "dom.webnotifications.enabled": False,
                "dom.push.enabled": False,

                # ALLOW MIXED CONTENT (fixes "not secured" warnings)
                "security.mixed_content.block_active_content": False,
                "security.mixed_content.block_display_content": False,
            }
        )

        # ─────────────────────────────────────────────────────────────
        # BROWSER CONTEXT — FULL HD 1920x1080 + SSL errors ignored
        # ─────────────────────────────────────────────────────────────
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},  # Full HD
            screen={"width": 1920, "height": 1080},    # Match screen size too
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
                "Gecko/20100101 Firefox/124.0"
            ),
            ignore_https_errors=True,   # Fixes "Connection not secure" warning
            service_workers="block",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "DNT": "1",
            },
        )

        await context.clear_cookies()
        print("[INFO] Cookies cleared.")
        print("[INFO] Viewport: 1920x1080 Full HD.")
        print("[INFO] HTTPS errors ignored.")

        # ─────────────────────────────────────────────────────────────
        # OPEN PAGE
        # ─────────────────────────────────────────────────────────────
        page = await context.new_page()

        # APPLY STEALTH — hides Playwright from Akamai/Cloudflare bot detection
        # This fixes the "Unable to Process Request" error on IRCTC
        await stealth_async(page)
        print("[INFO] Stealth mode ON — Akamai bot detection bypassed.")

        # Attach smart ad blocker
        await page.route("**/*", ad_blocker)
        print("[INFO] Smart Ad Blocker active.")

        # ─────────────────────────────────────────────────────────────
        # GO TO IRCTC
        # ─────────────────────────────────────────────────────────────
        print("[INFO] Opening IRCTC...")
        await page.goto(
            "https://www.irctc.co.in/nget/train-search",
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Wait for Angular app to fully render
        await page.wait_for_timeout(4000)
        print("[INFO] IRCTC loaded!")
        print("[INFO] Ab manually login karein aur ticket book karein.")
        print("[INFO] CAPTCHA manually bhar dena — auto solve nahi hoga.")
        print("[INFO] Browser 10 minutes tak open rahega.")

        # Keep browser open for 10 minutes
        await page.wait_for_timeout(600_000)

        await context.close()
        await browser.close()


asyncio.run(main())
