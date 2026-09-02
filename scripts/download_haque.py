#!/usr/bin/env python3
"""Download all matched Haque PDFs (resumable).

Strategy:
  - skip URLs already downloaded (state file + on-disk %PDF + size check)
  - solve the Imunify360 challenge once on the first URL
  - for each remaining URL: goto -> expect_download -> save_as
  - record OK/FAIL in a state file so a crash restarts cleanly
"""
import asyncio
import json
import os
import re
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from paths import WORK_DIR, DEST_DIR

STATE = os.path.join(WORK_DIR, "haque_all_state.json")


def sanitize(n):
    return re.sub(r'[^\w\-\.]+', '_', n).strip('_').rstrip('_')


def build_jobs():
    """Build the (filename, url) download list from match_result + manifest."""
    try:
        match = json.load(open(os.path.join(WORK_DIR, "match_result.json")))["matched"]
    except FileNotFoundError:
        match = []
    jobs = []
    seen = set()
    for m in match:
        mm, b = m["missing"], m["book"]
        code = mm.get("code")
        name = mm.get("name") or (b.get("name_clean") or "book")
        fname = sanitize(f"{code}_{name}") if code and code != "No Code" else sanitize(name)
        fname = fname.rstrip('_') + ".pdf"
        # avoid collisions
        if fname in seen:
            fname = sanitize(f"{fname[:-4]}_{b['post_id']}") + ".pdf"
        seen.add(fname)
        jobs.append({"code": code, "filename": fname, "url": b["post_file_url"]})
    return jobs


async def main():
    jobs = build_jobs()
    print("total jobs:", len(jobs))

    # mark already-downloaded
    done_urls = set()
    manifest = os.path.join(WORK_DIR, "haque_collection_manifest.json")
    if os.path.exists(manifest):
        for r in json.load(open(manifest)):
            if r.get("url"):
                done_urls.add(r["url"])
    todo = [j for j in jobs if j["url"] not in done_urls]
    print("already done:", len(jobs) - len(todo), "to download:", len(todo))

    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE))

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US", viewport={"width": 1366, "height": 768}, accept_downloads=True,
        )
        await Stealth().apply_stealth_async(ctx)
        page = await ctx.new_page()

        # solve challenge once on the first URL
        if todo:
            try:
                await page.goto(todo[0]["url"], wait_until="domcontentloaded")
            except Exception:
                pass
            await page.wait_for_timeout(8000)

        for i, j in enumerate(todo):
            fn, url = j["filename"], j["url"]
            if fn in state:
                continue
            path = os.path.join(DEST_DIR, fn)
            ok = False
            for _ in range(3):
                try:
                    async with page.expect_download(timeout=240000) as di:
                        try:
                            await page.goto(url, wait_until="domcontentloaded")
                        except Exception:
                            pass
                    d = await di.value
                    await d.save_as(path)
                    if (os.path.getsize(path) > 1000
                            and open(path, 'rb').read(5).startswith(b'%PDF')):
                        ok = True
                        break
                except Exception as e:
                    print("  attempt err", repr(e)[:100])
                    await page.wait_for_timeout(3000)
            state[fn] = os.path.getsize(path) if ok else "FAIL"
            print("[%d/%d] %s (%s)" % (i + 1, len(todo), fn, ("OK" if ok else "FAIL")))
            json.dump(state, open(STATE, "w"), indent=2)
        await browser.close()

    print("DONE. OK:", sum(1 for v in state.values() if isinstance(v, int)),
          "FAIL:", sum(1 for v in state.values() if v == "FAIL"))


asyncio.run(main())
