"""Exact "open this title in <app>" links for live (TMDB) titles.

TMDB's API only gives one link per title: its watch page, where JustWatch lists each streaming app.
Every app button on that page is a JustWatch link that carries the real destination in its `r=`
parameter (e.g. https://www.netflix.com/title/81234567). When someone opens a title in VibeSync we
read that one page, on demand, and hand the real per-app links to the buttons, so a tap goes straight
to the title in the app instead of through the watch page.
"""
from __future__ import annotations

import html as htmllib
import re
import urllib.request
from urllib.parse import parse_qs, urlsplit

# Only ever fetch TMDB watch pages (never an arbitrary URL from the browser).
WATCH_URL = re.compile(r"^https://www\.themoviedb\.org/(movie|tv)/\d+[A-Za-z0-9\-]*/watch(\?locale=[A-Z]{2})?$")
_A_TAG = re.compile(r"<a\b[^>]*>", re.I | re.S)
_ATTR = re.compile(r'([a-zA-Z_:-]+)\s*=\s*"([^"]*)"')
_IMG_ALT = re.compile(r'<img\b[^>]*\balt="([^"]+)"', re.I)


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def is_watch_url(url: str) -> bool:
    return bool(WATCH_URL.match(url or ""))


def parse_watch_page(page: str) -> dict[str, str]:
    """{normalised provider name: destination URL}. First listing wins (TMDB lists Stream before Rent/Buy)."""
    links: dict[str, str] = {}
    for m in _A_TAG.finditer(page):
        attrs = {k.lower(): htmllib.unescape(v) for k, v in _ATTR.findall(m.group(0))}
        href = attrs.get("href", "")
        if "justwatch.com" not in href:
            continue
        dest = (parse_qs(urlsplit(href).query).get("r") or [""])[0]
        if not dest.startswith(("https://", "http://")):
            continue
        title = attrs.get("title", "")
        name = title.rsplit(" on ", 1)[1] if " on " in title else ""
        if not name:                                    # fall back to the logo's alt text inside the link
            alt = _IMG_ALT.search(page, m.end(), m.end() + 600)
            name = alt.group(1) if alt else ""
        key = norm(name)
        if key and key not in links:
            links[key] = dest
    return links


def fetch_watch_links(url: str, timeout: float = 6.0) -> dict[str, str]:
    if not is_watch_url(url):
        return {}
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Mobile Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        page = r.read(1_500_000).decode("utf-8", "replace")
    return parse_watch_page(page)
