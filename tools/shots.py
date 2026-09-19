"""Render both pages at phone and desktop width, in light and dark, and save PNGs."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("shots"); OUT.mkdir(exist_ok=True)
ROOT = Path(".").resolve()
VIEWS = [("phone", 390, 900), ("desktop", 1440, 1000)]
PAGES = ["en.html", "index.html", "guardian-drowsiness.html"]

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for page_name in PAGES:
        for label, w, h in VIEWS:
            for theme in ("light", "dark"):
                ctx = browser.new_context(viewport={"width": w, "height": h},
                                          device_scale_factor=2,
                                          color_scheme=theme)
                page = ctx.new_page()
                page.goto(f"file://{ROOT / page_name}")
                page.wait_for_timeout(1200)
                full = page_name != "guardian-drowsiness.html"
                out = OUT / f"{Path(page_name).stem}-{label}-{theme}.png"
                page.screenshot(path=str(out), full_page=full)
                print("wrote", out)
                ctx.close()
    browser.close()
