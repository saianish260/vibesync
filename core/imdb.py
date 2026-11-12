"""IMDb ratings for the genre mixer.

IMDb publishes every title's current rating in a daily file (title.ratings.tsv.gz, free for personal and
non-commercial use: https://developer.imdb.com/non-commercial-datasets/). This module downloads it, keeps
it as a compact sorted table (a few MB of memory), and looks up ratings by IMDb id. TMDB's results carry
TMDB ids, so `imdb_id` asks TMDB for each title's IMDb id (cached by the caller).
"""
from __future__ import annotations

import gzip
import io
import json
import re
import urllib.parse
import urllib.request
from array import array
from bisect import bisect_left

RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
MIN_VOTES = 1           # every title IMDb shows a rating for is kept, exactly as IMDb has it


class Ratings:
    """IMDb id (tt1234567) -> (rating, votes), stored as three parallel arrays sorted by the numeric id."""

    def __init__(self, ids: array, ratings: array, votes: array):
        self.ids, self.ratings, self.votes = ids, ratings, votes

    def __len__(self) -> int:
        return len(self.ids)

    def get(self, imdb: str) -> tuple[float, int] | None:
        if not imdb or not imdb.startswith("tt"):
            return None
        try:
            n = int(imdb[2:])
        except ValueError:
            return None
        i = bisect_left(self.ids, n)
        if i < len(self.ids) and self.ids[i] == n:
            return self.ratings[i] / 10, self.votes[i]
        return None


def parse_ratings(raw: bytes, min_votes: int = MIN_VOTES) -> Ratings:
    # straight into compact arrays (the whole file is ~1.6 million titles, ~15 MB this way)
    ids, rts, vts = array("I"), array("B"), array("I")
    ordered, last = True, -1
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:
        next(f, None)                                   # header: tconst, averageRating, numVotes
        for line in f:
            parts = line.rstrip(b"\r\n").split(b"\t")
            if len(parts) != 3:
                continue
            try:
                votes = int(parts[2])
                if votes < min_votes:
                    continue
                n = int(parts[0][2:])
                ids.append(n); rts.append(round(float(parts[1]) * 10)); vts.append(min(votes, 4_000_000_000))
            except (ValueError, OverflowError):
                continue
            if n < last:
                ordered = False
            last = n
    if not ordered:                                     # IMDb's file is sorted by id; sort only if it ever isn't
        order = sorted(range(len(ids)), key=ids.__getitem__)
        ids, rts, vts = array("I", (ids[i] for i in order)), array("B", (rts[i] for i in order)), array("I", (vts[i] for i in order))
    return Ratings(ids, rts, vts)


def fetch_ratings(timeout: float = 90.0) -> Ratings:
    req = urllib.request.Request(RATINGS_URL, headers={"User-Agent": "VibeSync"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return parse_ratings(r.read())


def imdb_id(tmdb_key: str, kind: str, tmdb_id: int, timeout: float = 8.0) -> str:
    """The IMDb id TMDB has for a movie / series ("" if none)."""
    kind = "tv" if kind == "tv" else "movie"
    url = f"https://api.themoviedb.org/3/{kind}/{int(tmdb_id)}/external_ids?api_key={tmdb_key}"
    req = urllib.request.Request(url, headers={"User-Agent": "VibeSync"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return str(json.loads(r.read().decode("utf-8")).get("imdb_id") or "")


_LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.S)
_GQL = "https://caching.graphql.imdb.com/"


def _graphql(imdb: str, timeout: float) -> dict | None:
    """IMDb's own live data for one title. {"r", "v"} when it's rated, {"none": True} when IMDb has the title but no
    rating yet, None if IMDb couldn't be reached."""
    body = json.dumps({"query": 'query{title(id:"%s"){id ratingsSummary{aggregateRating voteCount}}}' % imdb}).encode()
    req = urllib.request.Request(_GQL, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 VibeSync",
                                                           "x-imdb-client-name": "imdb-web-next-localized", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        t = (json.loads(r.read().decode("utf-8")).get("data") or {}).get("title")
    if not t:
        return None
    s = t.get("ratingsSummary") or {}
    if s.get("aggregateRating"):
        return {"r": float(s["aggregateRating"]), "v": int(s.get("voteCount") or 0)}
    return {"none": True}


def live_rating(imdb: str, omdb_key: str = "", table: "Ratings | None" = None, timeout: float = 10.0) -> dict:
    """One title's latest IMDb rating: IMDb's own live data first, then its title page, then OMDb (if a key is set),
    then IMDb's daily ratings file. Returns {"r": 7.3, "v": 152340, "src": "imdb"|"omdb"|"daily"},
    {"none": True} when IMDb itself has no rating for the title yet, or {} if none of them could be reached."""
    if not re.fullmatch(r"tt\d{5,10}", imdb or ""):
        return {}
    unrated = False
    for _ in range(2):                                   # one retry: a single slow answer shouldn't fail the tap
        try:
            g = _graphql(imdb, timeout)
            if g and g.get("r"):
                remember(imdb, g["r"], g["v"])
                return {"r": g["r"], "v": g["v"], "src": "imdb"}
            if g and g.get("none"):
                unrated = True
            break
        except Exception:
            continue
    try:
        req = urllib.request.Request(f"https://www.imdb.com/title/{imdb}/", headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
            "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            page = r.read(3_000_000).decode("utf-8", "replace")
        for block in _LD.findall(page):
            try:
                data = json.loads(block)
            except ValueError:
                continue
            agg = data.get("aggregateRating") if isinstance(data, dict) else None
            if agg and agg.get("ratingValue"):
                r, v = float(agg["ratingValue"]), int(agg.get("ratingCount") or 0)
                remember(imdb, r, v)
                return {"r": r, "v": v, "src": "imdb"}
    except Exception:
        pass
    if omdb_key:
        try:
            url = f"https://www.omdbapi.com/?i={imdb}&apikey={urllib.parse.quote(omdb_key)}"
            with urllib.request.urlopen(url, timeout=timeout) as r:
                o = json.loads(r.read().decode("utf-8"))
            if o.get("imdbRating") not in (None, "", "N/A"):
                return {"r": float(o["imdbRating"]), "v": int(str(o.get("imdbVotes", "0")).replace(",", "") or 0), "src": "omdb"}
        except Exception:
            pass
    got = rating(table, imdb)
    if got:
        return {"r": got[0], "v": got[1], "src": "daily"}
    return {"none": True} if unrated else {}


# ───────────── kept in memory on the server, refreshed once a day ─────────────
import threading as _threading
import time as _time

_STATE = {"table": None, "day": "", "busy": False, "failed_at": 0.0, "cur": {}, "cur_day": "", "cur_busy": False,
          "ticker": False}
_FRESH: dict[str, tuple[float, int, float]] = {}   # IMDb id -> (rating, votes, when): ratings fetched live, newer than the file
_IDS: dict[str, str] = {}               # library title -> IMDb id (found once, kept)
_LOCK = _threading.Lock()


def _today() -> str:
    return _time.strftime("%Y-%m-%d", _time.gmtime(_time.time() + 5.5 * 3600))   # India's date


def remember(imdb: str, r: float, v: int) -> None:
    """A rating just fetched live from IMDb: every device asking about this title gets it from now on."""
    _FRESH[imdb] = (float(r), int(v), _time.time())
    if len(_FRESH) > 5000:
        _FRESH.pop(next(iter(_FRESH)))


def rating(table: "Ratings | None", imdb: str) -> "tuple[float, int] | None":
    """A title's current IMDb rating: a live one fetched since the ratings file was downloaded, else the file's."""
    f = _FRESH.get(imdb or "")
    if f and f[2] >= _STATE.get("loaded_at", 0):
        return f[0], f[1]
    return table.get(imdb) if table is not None else None


def _ticker() -> None:
    """While the server is running, download the new day's file right after midnight (India)."""
    while True:
        now = _time.time() + 5.5 * 3600
        _time.sleep(86400 - now % 86400 + 60)           # a minute past India's midnight
        try:
            ratings_table()
        except Exception:
            pass


def ratings_table(block: bool = False) -> "Ratings | None":
    """IMDb's ratings file, downloaded once a day (India's date), and when the server starts. The download runs in
    the background (yesterday's table keeps serving meanwhile); with block=True and nothing loaded yet, it waits
    for the first one. A failed download is tried again 10 minutes later."""
    today, now = _today(), _time.time()
    with _LOCK:
        if not _STATE["ticker"]:
            _STATE["ticker"] = True
            _threading.Thread(target=_ticker, daemon=True).start()
        start = _STATE["day"] != today and not _STATE["busy"] and now - _STATE["failed_at"] > 600
        if start:
            _STATE["busy"] = True

    def work():
        try:
            _STATE["table"] = fetch_ratings()
            _STATE["loaded_at"] = _time.time()
            _STATE["cur_day"] = ""                       # the library's ratings are worked out again from the new file
            _STATE["day"] = today
        except Exception:
            _STATE["failed_at"] = _time.time()
        finally:
            _STATE["busy"] = False

    if start:
        if block and _STATE["table"] is None:
            work()
        else:
            _threading.Thread(target=work, daemon=True).start()
    elif block and _STATE["table"] is None and _STATE["busy"]:
        for _ in range(120):                             # someone else is downloading it: wait for that
            if not _STATE["busy"]:
                break
            _time.sleep(0.5)
    return _STATE["table"]


def _loose(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def find_imdb_id(tmdb_key: str, title: str, year: str, is_movie: bool, timeout: float = 8.0) -> str:
    """A library title's IMDb id, through TMDB's search (only when TMDB's top match has the same name)."""
    kind = "movie" if is_movie else "tv"
    q = {"api_key": tmdb_key, "query": title}
    y = (re.search(r"\d{4}", str(year or "")) or [None])[0]
    if y:
        q["year" if is_movie else "first_air_date_year"] = y
    url = f"https://api.themoviedb.org/3/search/{kind}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "VibeSync"}), timeout=timeout) as r:
        res = json.loads(r.read().decode("utf-8")).get("results") or []
    want = _loose(title.split(":")[0])
    for hit in res[:3]:
        names = {_loose(hit.get("title") or hit.get("name") or ""), _loose(hit.get("original_title") or hit.get("original_name") or "")}
        if any(n and (n == _loose(title) or n.startswith(want)) for n in names):
            return imdb_id(tmdb_key, kind, hit["id"], timeout)
    return ""


def library_ratings(items: list, tmdb_key: str) -> dict:
    """{library id: today's IMDb rating} for the hand-picked library. Worked out in the background once a day;
    returns what's ready (empty at first, then the app gets today's numbers on its next load)."""
    today = _today()
    with _LOCK:
        start = tmdb_key and _STATE["cur_day"] != today and not _STATE["cur_busy"]
        if start:
            _STATE["cur_busy"] = True
    if start:
        todo = [(it["id"], it["title"], it.get("year", ""), it.get("kind"), it.get("meta", "")) for it in items if it.get("kind") != "sports"]

        def work():
            try:
                from concurrent.futures import ThreadPoolExecutor
                table = ratings_table(block=True)
                if table is None:
                    return

                def one(t):
                    iid, title, year, kind, meta = t
                    if iid not in _IDS:
                        movie = kind == "movie" or (kind == "anime" and re.search(r"\d+h|\d+ ?min|film|movie", meta or "", re.I) is not None)
                        try:
                            _IDS[iid] = find_imdb_id(tmdb_key, title, year, movie)
                        except Exception:
                            return iid, None
                    got = rating(table, _IDS.get(iid, ""))
                    return iid, (got[0] if got else None)

                with ThreadPoolExecutor(max_workers=8) as pool:
                    out = {iid: r for iid, r in pool.map(one, todo) if r}
                _STATE["cur"] = out
                _STATE["cur_day"] = today
            finally:
                _STATE["cur_busy"] = False

        _threading.Thread(target=work, daemon=True).start()
    out = dict(_STATE["cur"])
    for iid, tt in list(_IDS.items()):                  # ratings fetched live since then win
        f = _FRESH.get(tt or "")
        if f and f[2] >= _STATE.get("loaded_at", 0):
            out[iid] = f[0]
    return out
