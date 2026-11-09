"""Small helpers shared by the views."""
from __future__ import annotations

import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from core import cards, config
from core.data import BY_ID, CATALOG, default_favorites
from core.state import get_profile


def now_ist() -> datetime:
    return datetime.now(ZoneInfo(config.TIMEZONE))


def greeting() -> str:
    h = now_ist().hour
    if h < 5:
        return "Late-night vibes"
    if h < 12:
        return "Good morning"
    if h < 17:
        return "Good afternoon"
    if h < 21:
        return "Good evening"
    return "Night mode activated"


def go(page: str, **state) -> None:
    """Button callback: switch the top nav to `page` and preset any session values."""
    st.session_state.page = page
    st.session_state.nav_widget = page
    for key, value in state.items():
        st.session_state[key] = value


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def favorite_ids() -> list[str]:
    ids = get_profile().favorites(default_favorites())
    return [i for i in ids if i in BY_ID]


def surprise(scope: str, pool: list[dict] | None = None) -> None:
    """Pick a random item (from favourites by default) and remember it for the spotlight."""
    st.session_state.spotlight_scope = scope
    if pool is None:
        pool = [BY_ID[i] for i in favorite_ids()] or CATALOG
    current = st.session_state.get("spotlight")
    choices = [i for i in pool if i["id"] != current] or pool
    st.session_state.spotlight = random.choice(choices)["id"]
    st.session_state.confetti_seed = time.time_ns()


def render_spotlight(scope: str) -> None:
    """Show the last Surprise Me pick (only in the view that triggered it)."""
    if st.session_state.get("spotlight_scope") != scope:
        return
    item = BY_ID.get(st.session_state.get("spotlight", ""))
    if not item:
        return
    seed = st.session_state.pop("confetti_seed", None)
    if seed is not None:                 # confetti only right after the click
        html(cards.confetti_html(seed=seed))
    html(cards.spotlight_html(item))
