"""Latest Indian news headlines for a search such as "Ranabaali OTT release date".

Reads Google News India's public RSS feed and returns each item's headline, source, date and link, the
same list the VibeSync phone and TV apps fetch themselves. The page reads the streaming app and the date
out of the headlines (see the OTT card); this module only fetches and lists them.
"""
from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request

FEED = "https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
_ITEM = re.compile(r"<item>(.*?)</item>", re.S)


def _tag(x: str, name: str) -> str:
    m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", x, re.S)
    if not m:
        return ""
    v = m.group(1).replace("<![CDATA[", "").replace("]]>", "")
    return html.unescape(v).strip()


def parse(xml: str, limit: int = 25) -> list[dict]:
    out = []
    for x in _ITEM.findall(xml)[:limit]:
        out.append({"t": _tag(x, "title"), "s": _tag(x, "source"), "d": _tag(x, "pubDate"), "u": _tag(x, "link")})
    return out


def fetch_news(query: str, timeout: float = 10.0) -> list[dict]:
    query = (query or "").strip()[:200]
    if not query:
        return []
    req = urllib.request.Request(FEED.format(q=urllib.parse.quote(query)),
                                 headers={"User-Agent": "Mozilla/5.0 (VibeSync)", "Accept-Language": "en-IN,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return parse(r.read(1_500_000).decode("utf-8", "replace"))
