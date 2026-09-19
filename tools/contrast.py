"""WCAG AA contrast audit for the palette in styles.css.

Run it after any colour change. It reads the two theme blocks out of the
stylesheet rather than a copy of the values, so the check cannot drift
away from what the site actually serves.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

AA_NORMAL, AA_LARGE = 4.5, 3.0


def srgb(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcolor: str) -> float:
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def ratio(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def tokens(css: str, block: str) -> dict[str, str]:
    start = css.index(block)
    body = css[start:css.index("}", start)]
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", body))


# Every pair the stylesheet actually renders, with the size class it is used
# at. `None` as a threshold means the pair is reported but not gated, and the
# note has to say why -- so an exemption is always argued, never silently
# granted by turning a number down until it passes.
PAIRS = [
    ("ink", "bg", AA_NORMAL, "body text"),
    ("sub", "bg", AA_NORMAL, "lede, descriptions, metric notes"),
    ("faint", "bg", AA_NORMAL, "eyebrow, section labels, dates, footer"),
    ("accent", "bg", AA_NORMAL, "links"),
    ("accent-hover", "bg", AA_NORMAL, "hovered links"),
    ("good", "bg", AA_LARGE, "metric value (20px, 500 weight)"),
    ("warn", "bg", AA_LARGE, "metric value (20px, 500 weight)"),
    ("line", "bg", None,
     "hairline separators -- decorative. WCAG 1.4.11 covers UI components and "
     "meaningful graphics; removing these rules loses no information, because "
     "every region they bound is already identified by its own heading or "
     "label. Reported so a future colour change cannot make them invisible "
     "without someone noticing."),
    ("line-2", "bg", None,
     "card and chip borders -- decorative, same argument. A chip is read by "
     "its text, not its outline."),
]


def main() -> int:
    css = Path("styles.css").read_text(encoding="utf-8")
    themes = {
        "light": tokens(css, ":root{"),
        "dark": tokens(css, ':root[data-theme="dark"]{'),
    }
    # The dark block overrides only some tokens; inherit the rest from light.
    themes["dark"] = {**themes["light"], **themes["dark"]}

    failures = 0
    for name, t in themes.items():
        print(f"\n{name}  (bg {t['bg']})")
        for fg, bg, threshold, use in PAIRS:
            r = ratio(t[fg], t[bg])
            if threshold is None:
                print(f"  ----  {r:5.2f}:1  (not gated)  --{fg} {t[fg]}  — {use}")
                continue
            ok = r >= threshold
            failures += not ok
            print(f"  {'PASS' if ok else 'FAIL'}  {r:5.2f}:1  (needs {threshold})  "
                  f"--{fg} {t[fg]}  — {use}")
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
