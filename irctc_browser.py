import asyncio
from playwright.async_api import async_playwright

# ─────────────────────────────────────────────
# AD BLOCKER: list of known ad/tracker domains
# ─────────────────────────────────────────────
AD_DOMAINS = [
    "googlesyndication.com", "doubleclick.net", "googleadservices.com",
    "adservice.google.com", "amazon-adsystem.com", "ads.yahoo.com",
    "advertising.com", "adform.net", "adnxs.com", "pubmatic.com",
    "openx.net", "rubiconproject.com", "scorecardresearch.com",
    "quantserve.com", "adzerk.net", "taboola.com", "outbrain.com",
    "criteo.com", "bidswitch.net", "moatads.com", "yieldmanager.com",
    "adroll.com", "casalemedia.com", "smartadserver.com",
    "pagead2.googlesyndication.com", "cdn.adnxs.com", "ads.pubmatic.com",
    "prebid.org", "ib.adnxs.com", "ads.linkedin.com",
]

async def ad_blocker(route, request):
    """Block requests from known ad/tracker domains."""
    url = request.url
    if any(ad in url for ad in AD_DOMAINS):
        print(f"[BLOCKED AD] {url[:80]}")
        await route.abort()
    elif request.resource_type in ["image", "media"] and any(
        ad in url for ad in ["adimg", "ads", "track", "pixel", "banner"]
    ):
        await route.abort()
    else:
        await route.continue_()


async def main():
    async with async_playwright() as p:

        # ─────────────────────────────────────────────
        # LAUNCH FIREFOX with custom about:config prefs
        # ─────────────────────────────────────────────
        browser = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                # --- COOKIE SETTINGS ---
                # 1 = Block THIRD-PARTY cookies only
                # (keeps IRCTC login session cookies working!)
                "network.cookie.cookieBehavior": 1,

                # --- DISABLE ALL CACHE ---
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": False,
                "browser.cache.offline.enable": False,
                "network.http.use-cache": False,
                "browser.sessionstore.privacy_level": 2,

                # --- ENHANCED TRACKING PROTECTION (Strict mode) ---
                "privacy.trackingprotection.enabled": True,
                "privacy.trackingprotection.socialtracking.enabled": True,
                "privacy.trackingprotection.cryptomining.enabled": True,
                "privacy.trackingprotection.fingerprinting.enabled": True,
                "browser.contentblocking.category": "strict",

                # --- DISABLE TELEMETRY & BACKGROUND NOISE ---
                "toolkit.telemetry.enabled": False,
                "datareporting.healthreport.uploadEnabled": False,
                "browser.ping-centre.telemetry": False,

                # --- PERFORMANCE TWEAKS ---
                "network.http.max-connections": 900,
                "network.http.max-persistent-connections-per-server": 10,

                # --- DISABLE GEO & NOTIFICATIONS (less popups) ---
                "geo.enabled": False,
                "dom.webnotifications.enabled": False,
                "dom.push.enabled": False,
            }
        )

        # ─────────────────────────────────────────────
        # CREATE BROWSER CONTEXT
        # ─────────────────────────────────────────────
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) "
                "Gecko/20100101 Firefox/120.0"
            ),
            service_workers="block",
        )

        # Clear any leftover cookies before starting
        await context.clear_cookies()
        print("[INFO] Cookies cleared.")

        # ─────────────────────────────────────────────
        # OPEN PAGE + ATTACH AD BLOCKER
        # ─────────────────────────────────────────────
        page = await context.new_page()
        await page.route("**/*", ad_blocker)
        print("[INFO] Ad blocker active via network route interception.")

        # ─────────────────────────────────────────────
        # GO TO IRCTC
        # ─────────────────────────────────────────────
        print("[INFO] Opening IRCTC...")
        await page.goto(
            "https://www.irctc.co.in/nget/train-search",
            wait_until="domcontentloaded",
            timeout=60000
        )
        print("[INFO] IRCTC loaded! Login manually and book your ticket.")
        print("[INFO] CAPTCHA bhi manually fill karna hoga.")

        # Keep browser open for 10 minutes (manual booking time)
        await page.wait_for_timeout(600_000)

        await context.close()
        await browser.close()


# Run the script
asyncio.run(main())
