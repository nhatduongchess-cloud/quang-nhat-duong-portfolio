"""Check every link and anchor on the site.

Internal targets must exist on disk; in-page anchors must match a real id;
external links are listed but not fetched.
"""
from __future__ import annotations
import re, sys
from html.parser import HTMLParser
from pathlib import Path

PAGES = ["index.html", "en.html", "guardian-drowsiness.html"]


class Collect(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag in ("img", "script", "source", "video") and a.get("src"):
            self.srcs.append(a["src"])
        if tag == "video" and a.get("poster"):
            self.srcs.append(a["poster"])
        if tag == "link" and a.get("href"):
            self.srcs.append(a["href"])


def main() -> int:
    problems = 0
    external = set()
    for page in PAGES:
        path = Path(page)
        if not path.exists():
            print(f"MISSING PAGE  {page}")
            problems += 1
            continue
        c = Collect()
        c.feed(path.read_text(encoding="utf-8"))
        for href in c.hrefs + c.srcs:
            if href.startswith(("http://", "https://")):
                external.add(href)
            elif href.startswith("mailto:"):
                pass
            elif href.startswith("#"):
                if href[1:] not in c.ids:
                    print(f"DEAD ANCHOR   {page} -> {href}")
                    problems += 1
            else:
                target = (path.parent / href.split("#", 1)[0]).resolve()
                if not target.exists():
                    print(f"DEAD FILE     {page} -> {href}")
                    problems += 1
        print(f"checked {page}: {len(c.hrefs)} links, {len(c.srcs)} assets, {len(c.ids)} ids")

    print(f"\nexternal links ({len(external)}), not fetched:")
    for url in sorted(external):
        print(f"  {url}")
    print(f"\n{problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
