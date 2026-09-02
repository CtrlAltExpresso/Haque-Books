#!/usr/bin/env python3
"""Full-catalog crawl (with WAF re-solve) -> catalog_all_books.json.

Reachable for resuming: loads what's already been found and appends.
"""
import asyncio
import base64
import hashlib
import json
import os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from paths import WORK_DIR
from waf_client import solve_challenge, api_post

BASE = "https://polyebook3.polyebook.com/api/v1/"
BOOKS_FILE = os.path.join(WORK_DIR, "catalog_all_books.json")
META_FILE = os.path.join(WORK_DIR, "catalog_meta.json")
SALT = 55667788
REQ_DELAY = 1.1
MAX_BOOKS = 2000


def make_data(**extra):
    sign = hashlib.md5(("viaviweb" + str(SALT)).encode()).hexdigest()
    d = {"package_name": "com.polybook.diploma", "salt": str(SALT), "sign": sign}
    d.update(extra)
    return base64.b64encode(json.dumps(d).encode()).decode()


async def paged_subcat(page, ctx, scid):
    out = []
    for pno in range(1, 61):
        r = await api_post(page, ctx, "books_by_sub_cat",
                           make_data(sub_cat_id=str(scid), user_id="0"), str(pno))
        if not r:
            break
        lst = r.get("EBOOK_APP", [])
        if not lst:
            break
        out.extend(lst)
        await page.wait_for_timeout(int(REQ_DELAY * 1000))
    return out


async def main():
    books = {}
    if os.path.exists(BOOKS_FILE):
        books = {str(b["post_id"]): b for b in json.load(open(BOOKS_FILE))}
    meta = json.load(open(META_FILE)) if os.path.exists(META_FILE) else {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US", viewport={"width": 1366, "height": 768},
        )
        await Stealth().apply_stealth_async(ctx)
        page = await ctx.new_page()
        await solve_challenge(page, ctx)

        if not meta.get("cats"):
            r = await api_post(page, ctx, "category", make_data())
            meta["cats"] = r.get("EBOOK_APP", []) if r else []
            json.dump(meta, open(META_FILE, "w"), ensure_ascii=False, indent=2)
        cats = meta["cats"]

        for c in cats:
            cid = str(c.get("post_id"))
            if not c.get("sub_cat_status"):
                continue
            subcats = await api_post(page, ctx, "subcategory", make_data(cat_id=cid))
            scs = subcats.get("EBOOK_APP", []) if subcats else []
            for sc in scs:
                scid = str(sc.get("post_id"))
                lst = await paged_subcat(page, ctx, scid)
                for b in lst:
                    books[str(b.get("post_id"))] = b
                print("CAT %s | SC %s %s -> %d books (total %d)"
                      % (cid, scid, sc.get("post_title"), len(lst), len(books)))
                json.dump(list(books.values()), open(BOOKS_FILE, "w"),
                          ensure_ascii=False, indent=2)
                if len(books) >= MAX_BOOKS:
                    return
        await browser.close()

    json.dump(list(books.values()), open(BOOKS_FILE, "w"), ensure_ascii=False, indent=2)
    print("DONE. TOTAL BOOKS:", len(books))


asyncio.run(main())
