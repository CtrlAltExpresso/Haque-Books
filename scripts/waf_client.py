#!/usr/bin/env python3
"""Solve the Imunify360 challenge and run WAF-safe API calls.

The API is protected by Imunify360: a JS challenge is served and headless
browsers are detected. After the challenge runs, the context holds a
`wssplashchk` cookie that unlocks the session. We drive a real (stealth)
headless Chromium and fire API calls from inside the page so they inherit
the cleared session. Re-solves and retries on 429/403/block pages.
"""
import json

BASE = "https://polyebook3.polyebook.com/api/v1/"

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


async def solve_challenge(page, ctx, first_url=None):
    """Load the base URL and wait for the WAF challenge to complete."""
    url = first_url or (BASE + "category")
    try:
        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
    except Exception:
        pass
    await page.wait_for_timeout(7000)
    cookies = await ctx.cookies()
    return any(c["name"] == "wssplashchk" for c in cookies)


async def api_post(page, ctx, endpoint, data, page_param="", retries=4):
    """POST an endpoint from inside the page; re-solve the WAF on block."""
    for attempt in range(retries):
        try:
            res = await page.evaluate("""async (a) => {
                const url = a.page_param ? (a.endpoint + "?page=" + a.page_param) : a.endpoint;
                const resp = await fetch(url, {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    body: "data=" + encodeURIComponent(a.b64)
                });
                const text = await resp.text();
                return {status: resp.status, text: text};
            }""", {"endpoint": endpoint, "b64": data, "page_param": page_param})
        except Exception as e:
            print("  fetch err", repr(e))
            await page.wait_for_timeout(3000)
            continue
        if res["status"] == 200:
            try:
                return json.loads(res["text"])
            except Exception:
                print("  non-json 200", res["text"][:120])
                return None
        blocked = (res["status"] in (429, 403)
                   or "One moment" in res["text"]
                   or "just a moment" in res["text"]
                   or "<!DOCTYPE" in res["text"])
        if blocked:
            print("  blocked (status %s), re-solving..." % res["status"])
            await solve_challenge(page, ctx)
            await page.wait_for_timeout(2500)
            continue
        print("  status", res["status"], res["text"][:120])
        return None
    return None
