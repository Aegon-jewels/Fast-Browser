import asyncio
from playwright.async_api import async_playwright

# playwright-stealth v2 NEW API (stealth_async was removed in v2.0.0)
from playwright_stealth import Stealth

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
# (IRCTC servers, Akamai CDN, Indian payment gateways)
# ─────────────────────────────────────────────────────────────
WHITELIST_DOMAINS = [
    "irctc.co.in",
    "indianrail.gov.in",
    "irctcconnect.in",
    "akamaized.net",
    "akamai.net",
    "edgekey.net",
    "razorpay.com",
    "payu.in",
    "paytm.com",
    "billdesk.com",
    "sbi.co.in",
    "hdfcbank.com",
    "icicibank.com",
    "npci.org.in",
    "upi.npci.org.in",
]


async def ad_blocker(route, request):
    """Smart ad blocker: whitelist IRCTC/CDN first, then block ad domains."""
    url = request.url
    if any(safe in url for safe in WHITELIST_DOMAINS):
        await route.continue_()
        return
    if any(ad in url for ad in AD_DOMAINS):
        print(f"[BLOCKED AD]  {url[:90]}")
        await route.abort()
        return
    await route.continue_()


async def main():
    async with async_playwright() as p:

        # ─────────────────────────────────────────────────────────────
        # LAUNCH FIREFOX
        # ─────────────────────────────────────────────────────────────
        browser = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                "network.cookie.cookieBehavior": 1,
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": False,
                "browser.cache.offline.enable": False,
                "network.http.use-cache": False,
                "browser.sessionstore.privacy_level": 2,
                "privacy.trackingprotection.enabled": True,
                "privacy.trackingprotection.socialtracking.enabled": True,
                "privacy.trackingprotection.cryptomining.enabled": True,
                "privacy.trackingprotection.fingerprinting.enabled": False,
                "toolkit.telemetry.enabled": False,
                "datareporting.healthreport.uploadEnabled": False,
                "browser.ping-centre.telemetry": False,
                "network.http.max-connections": 900,
                "network.http.max-persistent-connections-per-server": 10,
                "geo.enabled": False,
                "dom.webnotifications.enabled": False,
                "dom.push.enabled": False,
                "security.mixed_content.block_active_content": False,
                "security.mixed_content.block_display_content": False,
            }
        )

        # ─────────────────────────────────────────────────────────────
        # BROWSER CONTEXT — Full HD + SSL errors ignored
        # ─────────────────────────────────────────────────────────────
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            screen={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
                "Gecko/20100101 Firefox/124.0"
            ),
            ignore_https_errors=True,
            service_workers="block",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "DNT": "1",
            },
        )

        # ─────────────────────────────────────────────────────────────
        # APPLY STEALTH to CONTEXT (v2 API) — bypasses Akamai bot detection
        # In v2, stealth is applied to context so ALL pages get it automatically
        # ─────────────────────────────────────────────────────────────
        stealth = Stealth()
        await stealth.apply_stealth_async(context)   # <-- v2 NEW API
        print("[INFO] Stealth mode ON — Akamai bot detection bypassed.")

        await context.clear_cookies()
        print("[INFO] Cookies cleared.")
        print("[INFO] Viewport: 1920x1080 Full HD.")

        # Open page
        page = await context.new_page()

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
        await page.wait_for_timeout(4000)
        print("[INFO] IRCTC loaded!")
        print("[INFO] Manually login karein aur ticket book karein.")
        print("[INFO] CAPTCHA manually fill karna hoga.")
        print("[INFO] Browser 10 minutes tak open rahega.")

        await page.wait_for_timeout(600_000)

        await context.close()
        await browser.close()


asyncio.run(main())
