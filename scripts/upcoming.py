"""Once a day (GitHub Actions): every streaming app's upcoming movies, series and new seasons in India, from JustWatch.

Writes upcoming.json:
  {"generated": "...", "packs": {"Netflix": [{t, title, year, tmdb, imdb, date, label, season, poster, path, jw}, ...], ...}}
  t: "movie" or "tv"; date: YYYY-MM-DD ("" when only a month/year is known, see label); season: number for a new season;
  poster: "<id>/<slug>" for images.justwatch.com; tmdb: TMDB id (the show's id for a season) or null.
Notes for anything that went wrong are printed as GitHub annotations (::warning::) so they can be read without logs.
"""
import datetime, json, urllib.error, urllib.request

API = "https://apis.justwatch.com/graphql"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (VibeSync daily)", "Accept-Language": "en-IN,en;q=0.8"}
SKIP = ("amazon channel", "apple tv channel", "with ads", "store", "justwatch tv", "mls", "google play", "youtube", "bookmyshow", "amazon video")


def ask(query, variables=None):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(), headers=H, method="POST")
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:1500]
            if e.code in (400, 422):
                return {"errors": [{"message": body}]}
        except Exception as e:
            body = repr(e)
    return {"errors": [{"message": "network: " + body}]}


def note(kind, title, msg):
    print(f"::{kind} title={title}::" + str(msg).replace("%", "%25").replace("\n", " ")[:3500])


CONTENT = 'title originalReleaseYear fullPath posterUrl externalIds { tmdbId imdbId } upcomingReleases { releaseDate releaseType label package { shortName clearName } }'
FULL = """id objectType content(country: IN, language: "en") { %s ... on SeasonContent { seasonNumber } }
  ... on Season { show { id content(country: IN, language: "en") { title originalReleaseYear fullPath posterUrl externalIds { tmdbId imdbId } } } }""" % CONTENT
PLAIN = 'id objectType content(country: IN, language: "en") { %s }' % CONTENT
Q = """query Q($date: Date!, $f: TitleFilter, $after: String) { newTitles(country: IN, date: $date, filter: $f, first: 100, after: $after, pageType: UPCOMING, priceDrops: false) {
  totalCount pageInfo { endCursor hasNextPage } edges { node { %s } } } }"""


def poster(url):        # "/poster/356889892/{profile}/season-1.{format}" -> "356889892/season-1"
    p = (url or "").split("/")
    return f"{p[2]}/{p[4].split('.')[0]}" if len(p) >= 5 and p[1] == "poster" else ""


def item(node, short):
    c = node.get("content") or {}
    rel = [u for u in c.get("upcomingReleases") or [] if (u.get("package") or {}).get("shortName") == short]
    if not rel:
        return None
    today = datetime.date.today().isoformat()
    dated = sorted(u["releaseDate"] for u in rel if u.get("releaseDate") and u.get("label") in (None, "DATE"))
    u = rel[0]
    if dated:
        date, label = dated[0], "DATE"
        if date <= today:                       # out already (today counts as out)
            return None
    else:
        date, label = (u.get("releaseDate") or "")[:10], u.get("label") or "SOON"
    kind = node.get("objectType")
    show = (node.get("show") or {}).get("content") or {}
    tmdb_raw = str(((show or c).get("externalIds") or {}).get("tmdbId") or (c.get("externalIds") or {}).get("tmdbId") or "")
    tmdb = int(tmdb_raw.split(":")[0]) if tmdb_raw.split(":")[0].isdigit() else None
    season = c.get("seasonNumber")
    if season is None and kind == "SHOW_SEASON" and ":" in tmdb_raw and tmdb_raw.split(":")[1].isdigit():
        season = int(tmdb_raw.split(":")[1])
    base = show or c
    return {"t": "movie" if kind == "MOVIE" else "tv", "title": base.get("title") or c.get("title") or "",
            "year": base.get("originalReleaseYear") or c.get("originalReleaseYear"), "tmdb": tmdb,
            "imdb": ((base.get("externalIds") or {}).get("imdbId")) or None, "date": date, "label": label,
            "season": season if kind == "SHOW_SEASON" else None, "poster": poster(base.get("posterUrl") or c.get("posterUrl")),
            "path": base.get("fullPath") or c.get("fullPath") or "", "jw": node.get("id")}


def main():
    today = datetime.date.today().isoformat()
    packs = ((ask('query { packages(country: IN, platform: WEB) { clearName shortName monetizationTypes } }').get("data") or {}).get("packages")) or []
    packs = [p for p in packs if set(p.get("monetizationTypes") or []) & {"FLATRATE", "FREE", "ADS"} and not any(s in p["clearName"].lower() for s in SKIP)]
    node = FULL
    out = {}
    for p in packs:
        items, after, seen = [], None, set()
        for _ in range(10):                     # up to 1,000 upcoming titles per app
            r = ask(Q % node, {"date": today, "f": {"packages": [p["shortName"]]}, "after": after})
            if r.get("errors") and node is FULL:   # the season/show part isn't accepted: carry on without it
                note("warning", "season fields", r["errors"][0].get("message"))
                node = PLAIN
                r = ask(Q % node, {"date": today, "f": {"packages": [p["shortName"]]}, "after": after})
            if r.get("errors"):
                note("warning", p["clearName"], r["errors"][0].get("message"))
                break
            nt = (r.get("data") or {}).get("newTitles") or {}
            for e in nt.get("edges") or []:
                it = item(e.get("node") or {}, p["shortName"])
                if it and it["jw"] not in seen:
                    seen.add(it["jw"]); items.append(it)
            pi = nt.get("pageInfo") or {}
            if not pi.get("hasNextPage"):
                break
            after = pi.get("endCursor")
        if items:
            items.sort(key=lambda x: (x["date"] or "9999", x["title"]))
            out[p["clearName"]] = items
    summary = ", ".join(f"{k}: {len(v)}" for k, v in out.items())
    note("notice", "upcoming", f"{sum(len(v) for v in out.values())} titles · {summary}")
    if out.get("Netflix"):
        note("notice", "sample", json.dumps(out["Netflix"][:12]))
    json.dump({"generated": datetime.datetime.utcnow().isoformat() + "Z", "packs": out}, open("upcoming.json", "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
