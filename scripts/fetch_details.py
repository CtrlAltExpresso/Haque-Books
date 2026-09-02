#!/usr/bin/env python3
"""Fetch per-book details (incl. PDF url `post_file_url`) -> book_details.json.

Resumable: skips ids already in the details file.
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
DETAILS_FILE = os.path.join(WORK_DIR, "book_details.json")
SALT = 55667788
REQ_DELAY = 1.0


def make_data(**extra):
    sign = hashlib.md5(("viaviweb" + str(SALT)).encode()).hexdigest()
    d = {"package_name": "com.polybook.diploma", "salt": str(SALT), "sign": sign}
    d.update(extra)
    return base64.b64encode(json.dumps(d).encode()).decode()


async def main():
    books = json.load(open(os.path.join(WORK_DIR, "catalog_all_books.json")))
    details = {}
    if os.path.exists(DETAILS_FILE):
        details = json.load(open(DETAILS_FILE))

    todo = [str(b["post_id"]) for b in books if str(b["post_id"]) not in details]
    print("to fetch:", len(todo))

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

        for i, pid in enumerate(todo):
            r = await api_post(page, ctx, "books_details",
                               make_data(book_id=pid, user_id=""))
            if r:
                lst = r.get("EBOOK_APP")
                item = lst[0] if isinstance(lst, list) and lst else lst
                details[pid] = item
            if (i + 1) % 40 == 0:
                json.dump(details, open(DETAILS_FILE, "w"), ensure_ascii=False, indent=2)
                print("progress", i + 1, len(details))
            await page.wait_for_timeout(int(REQ_DELAY * 1000))
        await browser.close()

    json.dump(details, open(DETAILS_FILE, "w"), ensure_ascii=False, indent=2)
    print("DONE details:", len(details))


asyncio.run(main())
