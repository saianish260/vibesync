"""Book tickets: find a movie's own page on a ticketing site and give it in that site's official link format.

The page has only the title, year and the person's city, and the sites' title ids (BookMyShow ET00…, PVR's
session id, District MV…) aren't public data, so this asks a web search (DuckDuckGo's plain HTML page, then
Bing) for the site's page and rebuilds the link the way the site itself writes it:
  BookMyShow  https://in.bookmyshow.com/movies/<city>/<name>/ET00521598
  PVR INOX    https://www.pvrcinemas.com/moviesessions/<name>/35308
  Cinépolis   https://cinepolisindia.com/movie-details/<NAME>-HO00003185
  District    https://www.district.in/movies/<name>-movie-tickets-MV233661
"""
from __future__ import annotations

import base64
import html as _html
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"

# BookMyShow writes some cities its own way
BMS_CITY = {"delhi ncr": "national-capital-region-ncr", "delhi": "national-capital-region-ncr", "new delhi": "national-capital-region-ncr",
            "ncr": "national-capital-region-ncr", "gurgaon": "national-capital-region-ncr", "gurugram": "national-capital-region-ncr",
            "noida": "national-capital-region-ncr", "visakhapatnam": "vizag-visakhapatnam", "vizag": "vizag-visakhapatnam",
            "bangalore": "bengaluru", "cochin": "kochi", "bombay": "mumbai", "calcutta": "kolkata", "madras": "chennai"}


def _loose(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def bms_city(city: str) -> str:
    c = (city or "").strip().lower()
    return BMS_CITY.get(c) or _slug(c)


def official(url: str, city: str = "") -> str:
    """A found ticketing link in the site's official format, for the person's city ("" if it isn't a movie page)."""
    u = urllib.parse.urlparse(url)
    host, path = (u.hostname or "").lower(), urllib.parse.unquote(u.path or "")
    if host.endswith("bookmyshow.com"):
        m = re.search(r"/([a-z0-9-]+)/(ET\d{8})(?:/|$)", path, re.I)
        if not m:
            return ""
        slug, et = m.group(1).lower(), m.group(2).upper()
        if slug in ("movies", "buytickets"):
            return ""
        segs = [s for s in path.split("/") if s]
        found = ""                                   # the city in the found link: /movies/<city>/… or /<city>/movies/…
        if len(segs) >= 4 and segs[0] == "movies":
            found = segs[1]
        elif len(segs) >= 4 and segs[1] == "movies":
            found = segs[0]
        c = bms_city(city) if city else found
        return f"https://in.bookmyshow.com/movies/{c}/{slug}/{et}" if c else ""
    if host.endswith("pvrcinemas.com"):
        # https://www.pvrcinemas.com/moviesessions/<name>/35308 (the form PVR INOX's app opens; no city in it)
        m = re.search(r"/moviesessions/(?:[^/]+/)?([^/]+)/(\d+)", path, re.I)
        return f"https://www.pvrcinemas.com/moviesessions/{urllib.parse.quote(m.group(1).lower())}/{m.group(2)}" if m else ""
    if host.endswith("district.in"):
        # https://www.district.in/movies/<name>-movie-tickets-MV233661 (a found "-in-<city>" part is dropped)
        m = re.search(r"/movies/([a-z0-9-]+?)-movie-tickets(?:-in-[a-z0-9-]+?)?-(MV\d+)", path, re.I)
        return f"https://www.district.in/movies/{m.group(1).lower()}-movie-tickets-{m.group(2).upper()}" if m else ""
    if host.endswith("cinepolisindia.com"):
        # https://cinepolisindia.com/movie-details/<NAME>-HO00003185 (its ?cid= city number is left out: the site asks)
        m = re.search(r"/movie-details/([^/?#]+-HO\d+)", path, re.I)
        return "https://cinepolisindia.com/movie-details/" + urllib.parse.quote(m.group(1), safe="-._") if m else ""
    return ""


def _get(url: str, timeout: float, data: bytes | None = None) -> str:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html",
                                                        **({"Content-Type": "application/x-www-form-urlencoded"} if data else {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(1_500_000).decode("utf-8", "replace")


def _bing_url(href: str) -> str:
    """Bing wraps results as bing.com/ck/a?…&u=a1<base64 of the address>; unwrap them."""
    href = _html.unescape(href)
    if "bing.com/ck/a" not in href:
        return href
    u = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("u", [""])[0]
    if u.startswith("a1"):
        b = u[2:]
        try:
            return base64.urlsafe_b64decode(b + "=" * (-len(b) % 4)).decode("utf-8", "replace")
        except Exception:
            return ""
    return ""


ENGINES = [   # (name, how to ask, how to read the result links)
    ("ddg", lambda q, t: _get("https://html.duckduckgo.com/html/", t, urllib.parse.urlencode({"q": q, "kl": "in-en"}).encode()),
     lambda page: [urllib.parse.unquote(m) for m in re.findall(r"uddg=([^&\"']+)", page)]),
    ("ddg-lite", lambda q, t: _get("https://lite.duckduckgo.com/lite/?kl=in-en&q=" + urllib.parse.quote(q), t),
     lambda page: [urllib.parse.unquote(m) for m in re.findall(r"uddg=([^&\"']+)", page)]
                  + [_html.unescape(m) for m in re.findall(r'href="(https?://(?!duckduckgo)[^"]+)"', page)]),
    ("bing", lambda q, t: _get("https://www.bing.com/search?setlang=en-IN&cc=IN&q=" + urllib.parse.quote(q), t),
     lambda page: [_bing_url(m) for m in re.findall(r'<a[^>]+href="(https?://[^"]+)"', page)]),
]
LAST: dict = {}          # what the last lookups ran into (shown to the page for troubleshooting)


def _candidates(q: str, timeout: float) -> list[str]:
    for name, ask, read in ENGINES:
        try:
            links = [u for u in read(ask(q, timeout)) if u.startswith("http")]
            LAST[name] = len(links)
            if links:
                return links
        except Exception as e:
            LAST[name] = type(e).__name__ + (f" {getattr(e, 'code', '')}" if getattr(e, "code", None) else "")
    return []


def _name_of(official_url: str) -> str:
    """The movie name part of an official link (to compare with the title)."""
    path = urllib.parse.unquote(urllib.parse.urlparse(official_url).path)
    m = (re.search(r"/movies/[^/]+/([^/]+)/ET\d+", path) or re.search(r"/moviesessions/([^/]+)/\d+", path)
         or re.search(r"/movie-details/(.+)-HO\d+", path) or re.search(r"/movies/(.+)-movie-tickets-MV\d+", path))
    return _loose(m.group(1)) if m else ""


def find(site: str, title: str, year: str = "", city: str = "", timeout: float = 8.0) -> str:
    """The movie's page on one ticketing site, in its official format ("" if it couldn't be found).
    The page whose movie name matches the title best wins (exactly > starts with it > contains it)."""
    name = (title or "").split(":")[0].strip()
    want = _loose(name)
    if not want:
        return ""
    best, best_score = "", 0
    for q in (f"site:{site} {name} {year} {city}", f"site:{site} {name} {year}", f"site:{site} {name} movie tickets"):
        for url in _candidates(re.sub(r"\s+", " ", q).strip(), timeout):
            host = (urllib.parse.urlparse(url).hostname or "").lower()
            if not (host == site or host.endswith("." + site)):
                continue
            got = official(url, city)
            if not got:
                continue
            n = _name_of(got)
            score = 3 if n in (want, want + _loose(year)) else 2 if n.startswith(want) and len(want) >= 4 else 1 if want in n and len(want) >= 5 else 0
            if score > best_score:
                best, best_score = got, score
            if score == 3:
                return got
        if best:
            return best
    return best
