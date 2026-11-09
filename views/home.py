"""🏠 Home: greeting, mood picker, Surprise Me, Live now, quick jumps and your picks.

Kept deliberately short: everything category-specific lives in Browse, so a tap
here re-renders only a handful of cards.
"""
from __future__ import annotations

import random

import streamlit as st

from core import cards
from core.data import BOOSTS, BY_ID, CATEGORIES, MOODS, items_for_mood
from core.state import get_profile
from views.common import favorite_ids, go, greeting, html, render_spotlight, surprise

FEED_SIZE = 6


def _mood_picks(mood: str) -> list[dict]:
    state = st.session_state.get("mood_pick")
    if not state or state[0] != mood:
        pool = items_for_mood(mood)
        ids = [i["id"] for i in random.sample(pool, min(FEED_SIZE, len(pool)))]
        st.session_state.mood_pick = (mood, ids)
    return [BY_ID[i] for i in st.session_state.mood_pick[1]]


def _reshuffle() -> None:
    st.session_state.pop("mood_pick", None)


def _jump() -> None:
    cat = st.session_state.get("home_jump")
    st.session_state.home_jump = None
    if cat:
        go("browse", br_cat=cat)


def render() -> None:
    if "boost" not in st.session_state:
        st.session_state.boost = random.choice(BOOSTS)
    html(cards.hello_html(greeting(), get_profile().name(), st.session_state.boost))

    # 1) Mood → instant feed
    mood = st.pills("How are you feeling right now?", options=list(MOODS),
                    format_func=lambda k: MOODS[k]["label"], key="mood", on_change=_reshuffle)
    if mood:
        html(cards.mood_banner_html(MOODS[mood]["line"]))
        html(cards.grid_html(_mood_picks(mood)))
        st.button("🔀 Shuffle these picks", on_click=_reshuffle)

    # 2) Surprise Me
    st.button("🎲  SURPRISE ME", key="home_surprise", use_container_width=True,
              on_click=surprise, args=("home",))
    render_spotlight("home")

    # 3) Live now
    html(cards.section_html("🔴", "Live now"))
    html(cards.wide_card_html(BY_ID["bbt10"]))
    st.button("📋 Open episode tracker", on_click=go, args=("browse",), kwargs={"br_cat": "reality"})

    # 4) Jump into a category
    html(cards.section_html("🧭", "Browse by category"))
    st.pills("Browse by category", options=list(CATEGORIES), format_func=CATEGORIES.get,
             key="home_jump", on_change=_jump, label_visibility="collapsed")

    # 5) Your favourites
    favs = [BY_ID[i] for i in favorite_ids()]
    if favs:
        html(cards.section_html("⭐", "Your favourites", "Swipe →"))
        html(cards.rail_html(favs))
