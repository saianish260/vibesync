"""✨ Discover: a client-side Streamlit component (components/discover/index.html).

Everything on this screen (tabs, search, mood picks, detail sheets, favourites,
episode tracker, theme switch) runs in the browser, so taps feel instant
instead of waiting on a Python rerun.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit.components.v1 as components

from core.data import catalog_payload

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


def render(theme: str) -> dict | None:
    payload = catalog_payload()
    _write_catalog(payload)
    return _component(catalog=payload, theme=theme, key="discover", default=None)
