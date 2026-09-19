"""Generate the overfit-gap chart used on the Guardian card.

One measure (macro-F1) under two conditions, so the second series is drawn as a
reference tick in the text-ink colour rather than a second categorical hue - the
two are separated by mark shape as well as colour. Checked with the dataviz
validator: normal-vision dE 29.3 light / 22.4 dark, CVD dE 29.1 / 20.8, both well
clear of the 15 floor. The validator's lightness-band and chroma-floor checks are
reported as failures for the ink colour; they scope to categorical *fills*, and
this is an annotation mark, not a series fill.

Numbers come from docs/opendata/rldd_report.md in the guardian-co-pilot repo:
five-fold subject-disjoint cross-validation over 60 drivers.
"""
from __future__ import annotations

ROWS = [
    ("GRU (sequence)",      0.5325, 0.7287),
    ("Hand-written rule",   0.5095, 0.5192),
    ("Gradient boosting",   0.5089, 0.9997),
    ("Logistic regression", 0.4729, 0.5392),
    ("Majority class",      0.2685, 0.3018),
]

W, H = 664, 252
X0, X1 = 172, 596          # plot area
Y0, PITCH, BAR = 52, 34, 15


def x(v: float) -> float:
    return X0 + (X1 - X0) * v


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    p: list[str] = []
    add = p.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
        f'role="img" aria-label="Held-out macro-F1 against in-sample macro-F1 for five '
        f'predictors on 60 unseen drivers. Gradient boosting scores 1.00 in sample and '
        f'0.51 held out; the GRU scores 0.73 and 0.53; the hand-written rule 0.52 and 0.51.">')
    add('<style>'
        '.g-ink{fill:var(--ink,#17191C)}.g-sub{fill:var(--sub,#4E535B)}'
        '.g-faint{fill:var(--faint,#6A7079)}.g-bar{fill:var(--accent,#2445B8)}'
        '.g-tick{stroke:var(--ink,#17191C)}.g-grid{stroke:var(--line,#E4E1DA)}'
        '.g-span{stroke:var(--line-2,#CFCAC0)}'
        '</style>')

    # gridlines, recessive, behind the marks
    for v in (0, .25, .5, .75, 1.0):
        add(f'<line x1="{x(v):.1f}" y1="38" x2="{x(v):.1f}" y2="{Y0 + PITCH * len(ROWS) - 8:.0f}" '
            f'class="g-grid" stroke-width="1"/>')
        add(f'<text x="{x(v):.1f}" y="{Y0 + PITCH * len(ROWS) + 8:.0f}" font-size="10.5" '
            f'text-anchor="middle" class="g-faint" font-family="IBM Plex Mono, monospace">'
            f'{v:.2f}</text>')

    for i, (name, held, insample) in enumerate(ROWS):
        y = Y0 + i * PITCH
        mid = y + BAR / 2
        add(f'<text x="{X0 - 12}" y="{mid + 4:.1f}" font-size="12" text-anchor="end" '
            f'class="g-sub">{esc(name)}</text>')
        # the gap, drawn only where in-sample exceeds held-out
        if insample > held:
            add(f'<line x1="{x(held):.1f}" y1="{mid:.1f}" x2="{x(insample):.1f}" y2="{mid:.1f}" '
                f'class="g-span" stroke-width="1" stroke-dasharray="3 3"/>')
        add(f'<rect x="{X0}" y="{y}" width="{max(x(held) - X0, 0.1):.1f}" height="{BAR}" '
            f'rx="3" class="g-bar"><title>{esc(name)}: held out {held:.2f}, '
            f'in sample {insample:.2f}</title></rect>')
        # in-sample reference: a tick, so the two series differ in shape, not only hue
        add(f'<line x1="{x(insample):.1f}" y1="{y - 3}" x2="{x(insample):.1f}" y2="{y + BAR + 3}" '
            f'class="g-tick" stroke-width="2"/>')
        add(f'<text x="{x(max(held, insample)) + 10:.1f}" y="{mid + 4:.1f}" font-size="11.5" '
            f'class="g-ink" font-family="IBM Plex Mono, monospace">{held:.2f}</text>')

    # legend - present because there are two series
    add(f'<rect x="{X0}" y="14" width="22" height="9" rx="2" class="g-bar"/>')
    add(f'<text x="{X0 + 30}" y="22.5" font-size="11.5" class="g-sub">held out '
        f'(60 unseen drivers)</text>')
    add(f'<line x1="{X0 + 210}" y1="12" x2="{X0 + 210}" y2="26" class="g-tick" stroke-width="2"/>')
    add(f'<text x="{X0 + 220}" y="22.5" font-size="11.5" class="g-sub">in sample</text>')
    add('</svg>')
    return "".join(p)


if __name__ == "__main__":
    from pathlib import Path
    Path("assets/overfit.svg").write_text(build(), encoding="utf-8")
    print("wrote assets/overfit.svg")
