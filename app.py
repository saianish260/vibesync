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
                "core.watchlinks", "core.langs", "core.news", "core.imdb", "core.book", "views.discover"]


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
from views import discover  # noqa: E402

for _name in _OWN_MODULES:          # remember which version of each file is loaded
    if _name in sys.modules:
        sys.modules[_name].__vs_mtime__ = _file_mtime(sys.modules[_name])

if "theme" not in st.session_state:
    st.session_state.theme = "cinema"
styles.inject(st.session_state.theme, "discover", st.session_state.get("title_palette"))

# Discover reports {theme, palette, n}; n is a nonce so each change is handled exactly once (a component keeps
# returning its last value on every rerun).
value = discover.render(st.session_state.theme)
if isinstance(value, dict):
    nonce = value.get("n")
    if nonce is None or nonce != st.session_state.get("_discover_nonce"):
        st.session_state._discover_nonce = nonce
        if "palette" in value:                 # a title theme (or None = default look)
            pal = styles.custom_palette(value.get("palette"))
            if pal != st.session_state.get("title_palette"):
                st.session_state.title_palette = pal
        picked = value.get("theme")
        if picked in styles.THEMES and picked != st.session_state.theme:
            st.session_state.theme = picked     # keep the page around it in the same look
            st.rerun()
