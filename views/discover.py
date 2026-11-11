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


@st.cache_data(ttl=3 * 3600, max_entries=400, show_spinner=False)
def _news(query: str) -> list:
    try:
        return fetch_news(query)
    except Exception:           # Google News unreachable: the page shows TMDB's own OTT card
        return []


@st.cache_data(ttl=6 * 3600, max_entries=400, show_spinner=False)
def _watch_links(url: str) -> dict[str, str]:
    try:
        return fetch_watch_links(url)
    except Exception:           # offline, blocked or changed page: the buttons keep their fallback link
        return {}


def render(theme: str) -> dict | None:
    payload = catalog_payload()
    _write_catalog(payload)
    resolved = st.session_state.setdefault("vs_resolved", {})
    langs = st.session_state.setdefault("vs_langs", {})
    news = st.session_state.setdefault("vs_news", {})
    value = _component(catalog=payload, theme=theme, tmdbKey=tmdb_key(), ytKey=youtube_key(), omdbKey=omdb_key(), firebase=firebase_config(), resolved=resolved, langs=langs, news=news,
                       key="discover", default=None)
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
    return value
