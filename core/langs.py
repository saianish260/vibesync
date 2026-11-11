"""Audio and subtitle languages per streaming app in India, from JustWatch's public GraphQL API.

JustWatch lists, for every offer (app x title), the audio languages and subtitle languages the app
carries. This is the same data JustWatch shows on its site. Titles or apps that don't list languages
come back with empty lists; VibeSync then says so instead of guessing.
"""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.request

API = "https://apis.justwatch.com/graphql"
QUERY = """
query GetSearchTitles($searchTitlesFilter: TitleFilter!, $country: Country!, $language: Language!, $first: Int!, $filter: OfferFilter!) {
  popularTitles(country: $country, filter: $searchTitlesFilter, first: $first, sortBy: POPULAR, sortRandomSeed: 0) {
    edges { node {
      id objectType
      content(country: $country, language: $language) { title originalReleaseYear originalReleaseDate externalIds { imdbId tmdbId } }
      offers(country: $country, platform: WEB, filter: $filter) {
        monetizationType presentationType audioLanguages subtitleLanguages standardWebURL
        package { clearName technicalName shortName }
      }
    } }
  }
}
"""


def _key(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"(.)\1+", r"\1", re.sub(r"[^a-z0-9]", "", s))


def build_request(title: str, kind: str) -> dict:
    return {"operationName": "GetSearchTitles", "query": QUERY,
            "variables": {"first": 8, "country": "IN", "language": "en", "filter": {"bestOnly": False},
                          "searchTitlesFilter": {"searchQuery": title, "includeTitlesWithoutUrl": True,
                                                 "objectTypes": ["SHOW"] if kind == "tv" else ["MOVIE"]}}}


def pick(edges: list, title: str, year: int | None, tmdb_id: int | None) -> dict | None:
    """The search result that is this exact title: same TMDB id, else same name and year (±1)."""
    nodes = [e.get("node") or {} for e in edges or []]
    if tmdb_id:
        for n in nodes:
            ext = ((n.get("content") or {}).get("externalIds") or {})
            if str(ext.get("tmdbId") or "") == str(tmdb_id):
                return n
    want = _key(title.split(":")[0])
    for n in nodes:
        c = n.get("content") or {}
        same = _key(c.get("title", "")) == _key(title) or _key(c.get("title", "").split(":")[0]) == want
        if same and (not year or not c.get("originalReleaseYear") or abs(int(c["originalReleaseYear"]) - int(year)) <= 1):
            return n
    return None


def summarize(node: dict | None) -> dict:
    """{date, apps: [{name, tech, types, audio, subs}]}, one entry per app, languages merged across offers."""
    if not node:
        return {"found": False}
    apps: dict[str, dict] = {}
    for o in node.get("offers") or []:
        pkg = o.get("package") or {}
        name = pkg.get("clearName") or pkg.get("shortName") or ""
        if not name:
            continue
        a = apps.setdefault(name, {"name": name, "tech": pkg.get("technicalName", ""), "types": [], "audio": [], "subs": [], "url": ""})
        # this app's own link to the title (the Watch buttons use it); a streaming offer's link first
        stream = o.get("monetizationType") in ("FLATRATE", "FREE", "ADS")
        if o.get("standardWebURL") and (not a["url"] or (stream and not a.get("_s"))):
            a["url"], a["_s"] = o["standardWebURL"], stream
        for k, src in (("types", [o.get("monetizationType")]), ("audio", o.get("audioLanguages")), ("subs", o.get("subtitleLanguages"))):
            for v in src or []:
                if v and v not in a[k]:
                    a[k].append(v)
    for a in apps.values():
        a.pop("_s", None)
    c = node.get("content") or {}
    return {"found": True, "date": c.get("originalReleaseDate") or "", "year": c.get("originalReleaseYear"), "apps": list(apps.values())}


def fetch_langs(title: str, year: int | None, tmdb_id: int | None, kind: str, timeout: float = 8.0) -> dict:
    req = urllib.request.Request(API, data=json.dumps(build_request(title, kind)).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (VibeSync)",
                                          "Accept-Language": "en-IN,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    edges = (((data.get("data") or {}).get("popularTitles") or {}).get("edges")) or []
    return summarize(pick(edges, title, year, tmdb_id))
