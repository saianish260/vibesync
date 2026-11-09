"""VibeSync: instant mood-boost entertainment hub.

Run with:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="VibeSync", page_icon="🎧", layout="wide",
                   initial_sidebar_state="collapsed")

from core import styles                       # noqa: E402  (page config must come first)
from core.state import get_profile            # noqa: E402
from views import browse, home, lounge        # noqa: E402
from views.common import html                 # noqa: E402

PAGES = {"home": "🏠 Home", "browse": "🧭 Browse", "lounge": "🛋️ Lounge"}
RENDER = {"home": home.render, "browse": browse.render, "lounge": lounge.render}

styles.inject()

# Open straight into the Lounge when someone follows an invite link (?room=CODE)
if "page" not in st.session_state:
    st.session_state.page = "lounge" if st.query_params.get("room") else "home"
if "nav_widget" not in st.session_state:
    st.session_state.nav_widget = st.session_state.page


def _on_nav() -> None:
    choice = st.session_state.nav_widget
    if choice:                       # ignore "deselect" clicks, keep current page
        st.session_state.page = choice
    else:
        st.session_state.nav_widget = st.session_state.page


brand, nav = st.columns([1, 2], vertical_alignment="center")
with brand:
    html('<div class="vs-brand">VIBESYNC</div>')
with nav:
    st.segmented_control("Navigate", options=list(PAGES), format_func=PAGES.get, key="nav_widget",
                         on_change=_on_nav, label_visibility="collapsed")

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    profile = get_profile()
    name = st.text_input("Your name (for greetings)", value=profile.name(), max_chars=20)
    if name != profile.name():
        profile.set_name(name)
    st.caption("Favourites: Browse → Manage favourites.")
    st.caption("Made with 💜 + Streamlit")

RENDER.get(st.session_state.page, home.render)()
