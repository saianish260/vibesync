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
MIN_VOTES = 50          # fewer votes than this isn't a meaningful rating


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
    rows = []
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
                rows.append((int(parts[0][2:]), round(float(parts[1]) * 10), min(votes, 4_000_000_000)))
            except ValueError:
                continue
    rows.sort()
    return Ratings(array("L", (r[0] for r in rows)), array("B", (r[1] for r in rows)), array("L", (r[2] for r in rows)))


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


def live_rating(imdb: str, omdb_key: str = "", table: "Ratings | None" = None, timeout: float = 10.0) -> dict:
    """One title's latest IMDb rating: IMDb's own title page first (exact, live), then OMDb (if a key is set),
    then IMDb's daily ratings file. Returns {"r": 7.3, "v": 152340, "src": "imdb"|"omdb"|"daily"} or {}."""
    if not re.fullmatch(r"tt\d{5,10}", imdb or ""):
        return {}
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
                return {"r": float(agg["ratingValue"]), "v": int(agg.get("ratingCount") or 0), "src": "imdb"}
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
    got = table.get(imdb) if table is not None else None
    return {"r": got[0], "v": got[1], "src": "daily"} if got else {}
