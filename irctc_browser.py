import asyncio
from playwright.async_api import async_playwright

# ─────────────────────────────────────────────────────────────
# AD BLOCKER: Only block pure ad/tracker domains
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
# WHITELIST: These domains must NEVER be blocked
# (IRCTC's own servers, CDNs, payment gateways)
# ─────────────────────────────────────────────────────────────
WHITELIST_DOMAINS = [
    "irctc.co.in",
    "indianrail.gov.in",
    "irctcconnect.in",
    "razorpay.com",
    "payu.in",
    "paytm.com",
    "billdesk.com",
    "sbi.co.in",
    "axis.bank",
    "hdfcbank.com",
    "icicibank.com",
]


async def ad_blocker(route, request):
    """Smart ad blocker — whitelist IRCTC first, then block known ad domains."""
    url = request.url

    # STEP 1: Always allow whitelisted domains (IRCTC, payment gateways)
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
        # LAUNCH FIREFOX with custom about:config prefs
        # ─────────────────────────────────────────────────────────────
        browser = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                # --- COOKIE SETTINGS ---
                # 1 = Block THIRD-PARTY cookies only
                # IRCTC's own session cookies still work!
                "network.cookie.cookieBehavior": 1,

                # --- DISABLE ALL CACHE ---
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": False,
                "browser.cache.offline.enable": False,
                "network.http.use-cache": False,
                "browser.sessionstore.privacy_level": 2,

                # --- TRACKING PROTECTION ---
                "privacy.trackingprotection.enabled": True,
                "privacy.trackingprotection.socialtracking.enabled": True,
                "privacy.trackingprotection.cryptomining.enabled": True,
                "privacy.trackingprotection.fingerprinting.enabled": True,
                "browser.contentblocking.category": "strict",

                # --- DISABLE TELEMETRY ---
                "toolkit.telemetry.enabled": False,
                "datareporting.healthreport.uploadEnabled": False,

                # --- PERFORMANCE TWEAKS ---
                "network.http.max-connections": 900,
                "network.http.max-persistent-connections-per-server": 10,

                # --- DISABLE POPUPS ---
                "geo.enabled": False,
                "dom.webnotifications.enabled": False,
                "dom.push.enabled": False,
            }
        )

        # ─────────────────────────────────────────────────────────────
        # CREATE BROWSER CONTEXT WITH PROPER VIEWPORT (1366x768 HD)
        # ─────────────────────────────────────────────────────────────
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},   # <-- FIXED resolution
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) "
                "Gecko/20100101 Firefox/122.0"
            ),
            service_workers="block",
            locale="en-IN",                             # Indian locale
            timezone_id="Asia/Kolkata",                 # IST timezone
        )

        # Clear leftover cookies before starting
        await context.clear_cookies()
        print("[INFO] Cookies cleared.")
        print("[INFO] Viewport set to 1366x768.")

        # ─────────────────────────────────────────────────────────────
        # OPEN PAGE + ATTACH SMART AD BLOCKER
        # ─────────────────────────────────────────────────────────────
        page = await context.new_page()

        # Smart ad blocker (whitelists IRCTC so UI doesn't break)
        await page.route("**/*", ad_blocker)
        print("[INFO] Smart Ad Blocker active — IRCTC domains whitelisted.")

        # ─────────────────────────────────────────────────────────────
        # GO TO IRCTC
        # ─────────────────────────────────────────────────────────────
        print("[INFO] Opening IRCTC...")
        await page.goto(
            "https://www.irctc.co.in/nget/train-search",
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Wait for IRCTC Angular app to fully load
        await page.wait_for_timeout(3000)
        print("[INFO] IRCTC loaded successfully!")
        print("[INFO] Login karein manually aur ticket book karein.")
        print("[INFO] CAPTCHA manually fill karna hoga.")

        # Keep browser open for 10 minutes
        await page.wait_for_timeout(600_000)

        await context.close()
        await browser.close()


# Run
asyncio.run(main())
