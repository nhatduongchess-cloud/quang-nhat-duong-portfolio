"""Prove the motion layer can never hide content.

Animation on a page is only safe if its failure modes are safe. Four are
tested, and each one asserts the same thing: the words are on the screen.

  1. normal          - JS runs, reveals fire
  2. reduced motion  - prefers-reduced-motion: reduce
  3. no JavaScript   - scripts disabled entirely
  4. no observer     - IntersectionObserver deleted before the script runs
                       (old browsers, and any future bug in that branch)

"Visible" here means the browser reports a non-zero opacity for a sample of
real content nodes, not that the element merely exists in the DOM.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGES = ["en.html", "index.html"]
SAMPLE = """() => {
  const sel = ['.hero-name', '.hero-lead', '.evidence .ev', '.case-title',
               '.case-lede', '.metric', '.entry .role', '.contact-line',
               '.band-item h3', '.award .t'];
  const bad = [];
  let checked = 0;
  for (const s of sel) {
    for (const el of document.querySelectorAll(s)) {
      checked++;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (parseFloat(cs.opacity) < 0.99 || cs.visibility === 'hidden' ||
          cs.display === 'none' || r.width === 0)
        bad.push(s + ' :: ' + el.textContent.trim().slice(0, 40));
    }
  }
  return {checked, bad};
}"""


def main() -> int:
    root = Path(".").resolve()
    failures = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for page_name in PAGES:
            url = f"file://{root / page_name}"
            cases = [
                ("normal", {}, None),
                ("reduced motion", {"reduced_motion": "reduce"}, None),
                ("no JavaScript", {"java_script_enabled": False}, None),
                ("no IntersectionObserver", {},
                 "delete window.IntersectionObserver;"),
            ]
            for label, ctx_args, init in cases:
                ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                                          **ctx_args)
                if init:
                    ctx.add_init_script(init)
                page = ctx.new_page()
                page.goto(url)
                # Scroll the whole page so anything gated on scroll has had
                # its chance to fire before we look.
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1400)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(900)
                res = page.evaluate(SAMPLE)
                ok = not res["bad"]
                failures += not ok
                print(f"  {'PASS' if ok else 'FAIL'}  {page_name:<11} {label:<24} "
                      f"{res['checked']} nodes checked")
                for b in res["bad"][:6]:
                    print(f"          hidden: {b}")
                ctx.close()
        browser.close()
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
