"""✨ Discover: a client-side Streamlit component (components/discover/index.html).

Everything on this screen (tabs, search, mood picks, detail sheets, favourites,
episode tracker, theme switch) runs in the browser, so taps feel instant
instead of waiting on a Python rerun.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

import streamlit.components.v1 as components

from core.data import catalog_payload
from core.imdb import imdb_id, library_ratings, live_rating, ratings_table
from core.langs import fetch_langs
from core.news import fetch_news
from core.watchlinks import fetch_watch_links, is_watch_url

DIR = Path(__file__).resolve().parent.parent / "components" / "discover"
_component = components.declare_component("vibesync_discover", path=str(DIR))


def _write_catalog(payload: dict) -> None:
    """Also keep catalog.json next to index.html (used if the component is opened directly)."""
    text = json.dumps(payload, ensure_ascii=False)
    path = DIR / "catalog.json"
    try:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
    except OSError:
        pass


def tmdb_key() -> str:
    """Free TMDB API key from Streamlit secrets (or the TMDB_API_KEY env var). Empty = hand-picked library only."""
    try:
        key = st.secrets.get("TMDB_API_KEY", "")
    except Exception:                       # no secrets file configured
        key = ""
    return str(key or os.environ.get("TMDB_API_KEY", "")).strip()


def youtube_key() -> str:
    """Optional YouTube Data API key (secret YOUTUBE_API_KEY) for finding each title's official soundtrack.
    Without it the screen uses the open-source Piped / Invidious search APIs."""
    try:
        key = st.secrets.get("YOUTUBE_API_KEY", "")
    except Exception:
        key = ""
    return str(key or os.environ.get("YOUTUBE_API_KEY", "")).strip()


def omdb_key() -> str:
    """Optional OMDb API key (secret OMDB_API_KEY) for IMDb, Rotten Tomatoes and Metascore ratings."""
    try:
        key = st.secrets.get("OMDB_API_KEY", "")
    except Exception:
        key = ""
    return str(key or os.environ.get("OMDB_API_KEY", "")).strip()


def firebase_config() -> dict:
    """Google sign-in + cloud save. Set FIREBASE_API_KEY, FIREBASE_PROJECT_ID and GOOGLE_CLIENT_ID
    (the Web client ID from Firebase > Authentication > Google) in Streamlit secrets. Empty = no sign-in."""
    def get(name: str) -> str:
        try:
            v = st.secrets.get(name, "")
        except Exception:
            v = ""
        return str(v or os.environ.get(name, "")).strip()
    cfg = {"apiKey": get("FIREBASE_API_KEY"), "projectId": get("FIREBASE_PROJECT_ID"), "clientId": get("GOOGLE_CLIENT_ID")}
    return cfg if all(cfg.values()) else {}


@st.cache_data(ttl=12 * 3600, max_entries=600, show_spinner=False)
def _langs(title: str, year: int | None, tmdb_id: int | None, kind: str) -> dict:
    try:
        return fetch_langs(title, year, tmdb_id, kind)
    except Exception:           # JustWatch unreachable: the page says so (and the Android app tries itself)
        return {"error": True}


@st.cache_data(ttl=2 * 3600, max_entries=400, show_spinner=False)   # news refreshes every 2 hours
def _news(query: str) -> list:
    try:
        return fetch_news(query)
    except Exception:           # Google News unreachable: the page shows TMDB's own OTT card
        return []


def _imdb_ratings():
    """IMDb's ratings file, downloaded again every day (kept in memory; None if IMDb can't be reached)."""
    return ratings_table(block=True)


@st.cache_data(ttl=60, max_entries=200, show_spinner=False)     # "refresh IMDb rating" on one title
def _imdb_live(imdb: str) -> dict:
    return live_rating(imdb, omdb_key(), _imdb_ratings())


@st.cache_data(ttl=30 * 24 * 3600, max_entries=50000, show_spinner=False)
def _imdb_id(kind: str, tmdb_id: int) -> str:
    try:
        return imdb_id(tmdb_key(), kind, tmdb_id)
    except Exception:
        return ""


def _imdb_for(refs: list) -> dict:
    """{"movie:123": [7.4, 120345], ...} for the genre mixer (titles IMDb has no rating for are left out)."""
    from concurrent.futures import ThreadPoolExecutor
    table = _imdb_ratings()
    if table is None:
        return {"error": True}
    pairs = []
    for r in refs[:120]:
        kind, _, tid = str(r).partition(":")
        if kind in ("movie", "tv") and tid.isdigit():
            pairs.append((kind, int(tid)))
    with ThreadPoolExecutor(max_workers=8) as pool:
        ids = list(pool.map(lambda p: _imdb_id(*p), pairs))
    out = {}
    for (kind, tid), iid in zip(pairs, ids):
        got = table.get(iid)
        if got:
            out[f"{kind}:{tid}"] = [got[0], got[1]]
    return out


@st.cache_data(ttl=6 * 3600, max_entries=400, show_spinner=False)
def _watch_links(url: str) -> dict[str, str]:
    try:
        return fetch_watch_links(url)
    except Exception:           # offline, blocked or changed page: the buttons keep their fallback link
        return {}


def render(theme: str) -> dict | None:
    payload = catalog_payload()
    # the hand-picked library's IMDb ratings: today's numbers from IMDb's daily file (worked out in the background)
    today = library_ratings(payload["items"], tmdb_key())
    for it in payload["items"]:
        if it["id"] in today:
            it["imdb"] = round(float(today[it["id"]]), 1)
    _write_catalog(payload)
    resolved = st.session_state.setdefault("vs_resolved", {})
    langs = st.session_state.setdefault("vs_langs", {})
    news = st.session_state.setdefault("vs_news", {})
    imdb = st.session_state.setdefault("vs_imdb", {})
    value = _component(catalog=payload, theme=theme, tmdbKey=tmdb_key(), ytKey=youtube_key(), omdbKey=omdb_key(), firebase=firebase_config(), resolved=resolved, langs=langs, news=news,
                       imdb=imdb, key="discover", default=None)
    # When a live title's sheet opens, the screen asks for that title's exact per-app links.
    req = value.get("resolve") if isinstance(value, dict) else None
    if req and value.get("n") != st.session_state.get("_resolve_n"):
        st.session_state._resolve_n = value.get("n")
        if is_watch_url(req) and req not in resolved:
            resolved[req] = _watch_links(req)
            while len(resolved) > 40:                   # keep the payload small
                resolved.pop(next(iter(resolved)))
            st.rerun()
    # ...and which audio / subtitle languages each app has it in
    lq = value.get("langs") if isinstance(value, dict) else None
    if isinstance(lq, dict) and value.get("n") != st.session_state.get("_langs_n"):
        st.session_state._langs_n = value.get("n")
        k = str(lq.get("key", ""))[:80]
        if k and k not in langs:
            try:
                year = int(str(lq.get("year") or "0")[:4]) or None
            except ValueError:
                year = None
            tid = lq.get("tmdb") if isinstance(lq.get("tmdb"), int) else None
            langs[k] = _langs(str(lq.get("title", ""))[:120], year, tid, "tv" if lq.get("type") == "tv" else "movie")
            while len(langs) > 30:
                langs.pop(next(iter(langs)))
            st.rerun()
    # ...and the latest news headlines about its OTT release (the page reads the app and date out of them)
    nq = value.get("news") if isinstance(value, dict) else None
    if isinstance(nq, dict) and value.get("n") != st.session_state.get("_news_n"):
        st.session_state._news_n = value.get("n")
        k, q = str(nq.get("key", ""))[:80], str(nq.get("q", ""))[:200]
        if k and q and k not in news:
            news[k] = _news(q)
            while len(news) > 30:
                news.pop(next(iter(news)))
            st.rerun()
    # ...and the genre mixer's IMDb ratings for the titles it found
    iq = value.get("imdb") if isinstance(value, dict) else None
    if isinstance(iq, dict) and value.get("n") != st.session_state.get("_imdb_n"):
        st.session_state._imdb_n = value.get("n")
        k, refs, one = str(iq.get("key", ""))[:80], iq.get("ids"), str(iq.get("one", ""))[:20]
        daily = iq.get("daily")
        if k and isinstance(daily, list) and k not in imdb:      # a title page: today's IMDb rating by IMDb id
            table = _imdb_ratings()
            imdb[k] = {"error": True} if table is None else {i: list(table.get(i)) for i in map(str, daily[:40]) if table.get(i)}
            while len(imdb) > 12:
                imdb.pop(next(iter(imdb)))
            st.rerun()
        if k and one and k not in imdb:
            imdb[k] = _imdb_live(one)
            while len(imdb) > 12:
                imdb.pop(next(iter(imdb)))
            st.rerun()
        if k and isinstance(refs, list) and k not in imdb and tmdb_key():
            imdb[k] = _imdb_for(refs)
            while len(imdb) > 12:
                imdb.pop(next(iter(imdb)))
            st.rerun()
    return value
