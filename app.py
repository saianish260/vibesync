"""VibeSync: pick something to watch in seconds, then open it straight in its app.

Run with:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="VibeSync", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

from core import styles             # noqa: E402  (page config must come first)
from views import discover, lounge  # noqa: E402

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
