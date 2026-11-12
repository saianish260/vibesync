"""Book tickets: find a movie's own page on a ticketing site and give it in that site's official link format.

The page has only the title, year and the person's city, and the sites' title ids (BookMyShow ET00…, PVR's
session id, District MV…) aren't public data, so this asks a web search (DuckDuckGo's plain HTML page, then
Bing) for the site's page and rebuilds the link the way the site itself writes it:
  BookMyShow  https://in.bookmyshow.com/movies/<city>/<name>/ET00521598
  PVR INOX    https://www.pvrcinemas.com/moviesessions/<City>/<NAME>/35308
  Cinépolis   https://cinepolisindia.com/movie-details/<NAME>-HO00003185
  District    https://www.district.in/movies/<name>-movie-tickets-MV233661
"""
from __future__ import annotations

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
PVR_CITY = {"delhi ncr": "Delhi-NCR", "delhi": "Delhi-NCR", "new delhi": "Delhi-NCR", "bangalore": "Bengaluru", "vizag": "Visakhapatnam"}


def _loose(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def bms_city(city: str) -> str:
    c = (city or "").strip().lower()
    return BMS_CITY.get(c) or _slug(c)


def pvr_city(city: str) -> str:
    c = (city or "").strip()
    return PVR_CITY.get(c.lower()) or "-".join(w[:1].upper() + w[1:].lower() for w in re.split(r"[\s-]+", c) if w)


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
        m = re.search(r"/moviesessions/([^/]+)/([^/]+)/(\d+)", path, re.I)
        if not m:
            return ""
        c = pvr_city(city) if city else m.group(1)
        return "https://www.pvrcinemas.com/moviesessions/{}/{}/{}".format(
            urllib.parse.quote(c), urllib.parse.quote(m.group(2)), m.group(3))
    if host.endswith("district.in"):
        # https://www.district.in/movies/<name>-movie-tickets-MV233661 (a found "-in-<city>" part is dropped)
        m = re.search(r"/movies/([a-z0-9-]+?)-movie-tickets(?:-in-[a-z0-9-]+?)?-(MV\d+)", path, re.I)
        return f"https://www.district.in/movies/{m.group(1).lower()}-movie-tickets-{m.group(2).upper()}" if m else ""
    if host.endswith("cinepolisindia.com"):
        # https://cinepolisindia.com/movie-details/<NAME>-HO00003185 (its ?cid= city number is left out: the site asks)
        m = re.search(r"/movie-details/([^/?#]+-HO\d+)", path, re.I)
        return "https://cinepolisindia.com/movie-details/" + urllib.parse.quote(m.group(1), safe="-._") if m else ""
    return ""


def _get(url: str, timeout: float) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(1_500_000).decode("utf-8", "replace")


def _candidates(q: str, timeout: float) -> list[str]:
    out: list[str] = []
    try:
        page = _get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q), timeout)
        out += [urllib.parse.unquote(m) for m in re.findall(r"uddg=([^&\"']+)", page)]
    except Exception:
        pass
    if not out:
        try:
            page = _get("https://www.bing.com/search?setlang=en-IN&cc=IN&q=" + urllib.parse.quote(q), timeout)
            out += [_html.unescape(m) for m in re.findall(r'<a[^>]+href="(https?://[^"]+)"', page)]
        except Exception:
            pass
    return out


def find(site: str, title: str, year: str = "", city: str = "", timeout: float = 8.0) -> str:
    """The movie's page on one ticketing site, in its official format ("" if it couldn't be found)."""
    name = (title or "").split(":")[0].strip()
    want = _loose(name)
    if not want:
        return ""
    for q in (f"site:{site} {name} {year} {city}", f"site:{site} {name} {year}", f"site:{site} {name} movie tickets"):
        for url in _candidates(re.sub(r"\s+", " ", q).strip(), timeout):
            host = (urllib.parse.urlparse(url).hostname or "").lower()
            if not (host == site or host.endswith("." + site)):
                continue
            if want not in _loose(urllib.parse.unquote(urllib.parse.urlparse(url).path)):
                continue
            got = official(url, city)
            if got:
                return got
    return ""
