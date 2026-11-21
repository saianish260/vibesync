"""Probe JustWatch's GraphQL for India's upcoming titles (run on GitHub Actions; writes probe.json)."""
import json, urllib.request, datetime

API = "https://apis.justwatch.com/graphql"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (VibeSync)", "Accept-Language": "en-IN,en;q=0.8"}


def ask(query, variables=None):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http": e.code, "body": e.read().decode()[:3000]}
    except Exception as e:
        return {"exc": repr(e)}


out = {}
out["packages"] = ask('query { packages(country: IN, platform: WEB) { packageId clearName technicalName shortName monetizationTypes } }')
today = datetime.date.today().isoformat()
NODE = """id objectType content(country: IN, language: "en") { title originalReleaseYear originalReleaseDate fullPath posterUrl
  externalIds { tmdbId imdbId } upcomingReleases { releaseDate releaseType label package { shortName clearName technicalName } } }"""
for pt in ("UPCOMING", "NEW"):
    out["newTitles_" + pt] = ask("""query Q($date: Date!, $f: TitleFilter) { newTitles(country: IN, date: $date, filter: $f, first: 5, pageType: %s, priceDrops: false, platform: WEB) {
      totalCount edges { node { %s } } } }""" % (pt, NODE), {"date": today, "f": {"packages": ["nfx"]}})
out["newTitleBuckets_UPCOMING"] = ask("""query { newTitleBuckets(country: IN, first: 3, pageType: UPCOMING, priceDrops: false, platform: WEB, filter: {packages: ["nfx"]}) {
  edges { key node { totalCount } } } }""")
out["popular_upcoming_field"] = ask("""query { popularTitles(country: IN, first: 3, filter: {packages: ["nfx"]}) { edges { node { %s } } } }""" % NODE)
out["type_NewPageType"] = ask('query { __type(name: "NewPageType") { enumValues { name } } }')
out["type_UpcomingRelease"] = ask('query { __type(name: "UpcomingRelease") { fields { name } } }')
out["type_Query"] = ask('query { __type(name: "Query") { fields { name args { name } } } }')
json.dump(out, open("probe.json", "w"), indent=1)
print(json.dumps(out)[:4000])
