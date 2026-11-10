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
    value = _component(catalog=payload, theme=theme, tmdbKey=tmdb_key(), resolved=resolved,
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
    return value
