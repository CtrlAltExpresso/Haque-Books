#!/usr/bin/env python3
"""Enumerate the full Poly eBook catalog with a WAF-safe browser.

Recovers every book (and categories/subcategories) from the API into
catalog_checkpoint.json / catalog_all_books.json.

Relies on `polyebook_api` helpers + a solved Imunify360 challenge
(the `wssplashchk` cookie) before firing API calls from inside the page.
"""
import asyncio
import base64
import hashlib
import json
import os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from paths import WORK_DIR

BASE = "https://polyebook3.polyebook.com/api/v1/"
CHECKPOINT = os.path.join(WORK_DIR, "catalog_checkpoint.json")
SALT = 55667788           # native-api salt integer


def make_data(**extra):
    sign = hashlib.md5(("viaviweb" + str(SALT)).encode()).hexdigest()
    d = {"package_name": "com.polybook.diploma", "salt": str(SALT), "sign": sign}
    d.update(extra)
    return base64.b64encode(json.dumps(d).encode()).decode()


async def api_post(page, endpoint, data, page_param=""):
    """Call the API from inside the page (same-origin fetch, WAF-clean)."""
    body = {"endpoint": endpoint, "b64": data, "page_param": page_param}
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
        }""", body)
    except Exception as e:
        print("  fetch err", endpoint, e)
        return None
    if res.get("status") != 200:
        print("  non-200", endpoint, res.get("status"), res.get("text", "")[:120])
        return None
    try:
        return json.loads(res["text"])
    except Exception:
        print("  json err", endpoint)
        return None


async def paged(page, endpoint, make_args, max_pages=60, delay=0.35):
    out = []
    for pno in range(1, max_pages + 1):
        r = await api_post(page, endpoint, make_args(), str(pno))
        if not r:
            break
        lst = r.get("EBOOK_APP", [])
        if not lst:
            break
        out.extend(lst)
        await page.wait_for_timeout(int(delay * 1000))
    return out


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US", viewport={"width": 1366, "height": 768},
        )
        await Stealth().apply_stealth_async(ctx)
        page = await ctx.new_page()
        try:
            await page.goto(BASE + "category", wait_until="domcontentloaded")
        except Exception:
            pass
        await page.wait_for_timeout(7000)   # let the WAF challenge finish

        test = await api_post(page, "category", make_data())
        cats = test.get("EBOOK_APP", []) if test else []
        print("categories:", len(cats))

        all_books = {}
        subcat_map = {}
        for c in cats:
            cid = c.get("post_id")
            print("### CAT", cid, c.get("post_title"))
            if c.get("sub_cat_status"):
                sc_r = await api_post(page, "subcategory", make_data(cat_id=str(cid)))
                scs = sc_r.get("EBOOK_APP", []) if sc_r else []
                subcat_map[str(cid)] = scs
                for sc in scs:
                    scid = sc.get("post_id")
                    scbooks = await paged(
                        page, "books_by_sub_cat",
                        lambda scid=scid: make_data(sub_cat_id=str(scid), user_id="0"))
                    for b in scbooks:
                        all_books.setdefault(b.get("post_id"), b)
                    print("   SC", scid, sc.get("post_title"), "->", len(scbooks))
                    await page.wait_for_timeout(150)
            cb = await paged(page, "books_by_cat",
                             lambda cid=cid: make_data(cat_id=str(cid), user_id="0"))
            for b in cb:
                all_books.setdefault(b.get("post_id"), b)
            print("   cat-level books:", len(cb))

        data = {"cats": cats, "subcats": subcat_map, "books": list(all_books.values())}
        print("TOTAL UNIQUE BOOKS:", len(all_books))
        with open(CHECKPOINT, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        await browser.close()
        print("saved", CHECKPOINT)


asyncio.run(main())
