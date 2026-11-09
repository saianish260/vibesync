"""VibeSync: pick something to watch in seconds, then open it straight in its app.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="VibeSync", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# Streamlit Cloud hot-reloads app.py after a git push but can keep old copies of our own
# modules in memory, which breaks imports of anything new. Reload any module whose file
# changed since it was loaded (dependency order matters).
_OWN_MODULES = ["core.config", "core.emoji", "core.data", "core.store", "core.cards", "core.styles",
                "core.state", "views.discover", "views.lounge"]


def _file_mtime(mod) -> float | None:
    try:
        return Path(mod.__file__).stat().st_mtime
    except (AttributeError, TypeError, OSError):
        return None


for _name in _OWN_MODULES:
    _mod = sys.modules.get(_name)
    if _mod is not None and getattr(_mod, "__vs_mtime__", None) != _file_mtime(_mod):
        try:
            importlib.reload(_mod)
        except Exception:            # a broken reload should surface on the import below, not here
            pass

from core import styles             # noqa: E402  (page config must come first)
from views import discover, lounge  # noqa: E402

for _name in _OWN_MODULES:          # remember which version of each file is loaded
    if _name in sys.modules:
        sys.modules[_name].__vs_mtime__ = _file_mtime(sys.modules[_name])

PAGES = {"discover": "Discover", "lounge": "Lounge"}

if "theme" not in st.session_state:
    st.session_state.theme = "cinema"
# Invite links (?room=CODE) open straight into the Lounge
if "page" not in st.session_state:
    st.session_state.page = "lounge" if st.query_params.get("room") else "discover"
if "nav_widget" not in st.session_state:
    st.session_state.nav_widget = st.session_state.page


def _on_nav() -> None:
    if st.session_state.nav_widget:
        st.session_state.page = st.session_state.nav_widget
    else:                                   # tapping the active option again keeps it selected
        st.session_state.nav_widget = st.session_state.page


styles.inject(st.session_state.theme)
st.segmented_control("Navigate", options=list(PAGES), format_func=PAGES.get, key="nav_widget",
                     on_change=_on_nav, label_visibility="collapsed")

if st.session_state.page == "lounge":
    lounge.render()
else:
    value = discover.render(st.session_state.theme)
    picked = value.get("theme") if isinstance(value, dict) else None
    if picked in styles.THEMES and picked != st.session_state.theme:
        st.session_state.theme = picked     # keep page chrome + Lounge in the same look
        st.rerun()
