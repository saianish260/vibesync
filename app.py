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
                "core.state", "core.watchlinks", "core.langs", "core.news", "core.imdb", "core.book", "views.discover", "views.lounge"]


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

if "theme" not in st.session_state:
    st.session_state.theme = "cinema"
# Invite links (?room=CODE) open straight into the Lounge
if "page" not in st.session_state:
    st.session_state.page = "lounge" if st.query_params.get("room") else "discover"


def _to_discover() -> None:
    st.session_state.page = "discover"


styles.inject(st.session_state.theme, st.session_state.page, st.session_state.get("title_palette"))

if st.session_state.page == "lounge":
    top_l, top_r = st.columns([1, 1], vertical_alignment="center")
    with top_l:
        st.markdown('<div class="vs-mark">Vibe<i>Sync</i></div>', unsafe_allow_html=True)
    with top_r:
        st.button("← Discover", key="back_discover", on_click=_to_discover)
    lounge.render()
else:
    # The Discover screen reports {theme, page, n}; n is a nonce so each tap is handled exactly once
    # (a component keeps returning its last value on every rerun).
    value = discover.render(st.session_state.theme)
    if isinstance(value, dict):
        nonce = value.get("n")
        if nonce is None or nonce != st.session_state.get("_discover_nonce"):
            st.session_state._discover_nonce = nonce
            changed = False
            picked = value.get("theme")
            if picked in styles.THEMES and picked != st.session_state.theme:
                st.session_state.theme = picked     # keep page chrome + Lounge in the same look
                changed = True
            if "palette" in value:                 # a title theme (or None = default look) for the Lounge too
                pal = styles.custom_palette(value.get("palette"))
                if pal != st.session_state.get("title_palette"):
                    st.session_state.title_palette = pal
            if nonce is not None and value.get("page") == "lounge":
                st.session_state.page = "lounge"
                changed = True
            if changed:
                st.rerun()
