"""🏠 Mood Feed: hero, mood picker, quick-picks, reality TV central and the vault."""
from __future__ import annotations

import random

import streamlit as st

from core import cards, config
from core.data import (BOOSTS, BY_ID, MOODS, TRACKER_SHOWS, TRACKER_TAGS, items_for_mood, items_of)
from core.state import get_profile
from views.common import greeting, html, now_ist, render_spotlight, surprise

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


def _hero() -> None:
    if "boost" not in st.session_state:
        st.session_state.boost = random.choice(BOOSTS)
    html(cards.hero_html(greeting(), get_profile().name(), config.TAGLINE, st.session_state.boost))


def _mood_section() -> None:
    mood = st.pills("How are you feeling right now?", options=list(MOODS),
                    format_func=lambda k: MOODS[k]["label"], key="mood", on_change=_reshuffle)
    if not mood:
        st.caption("👆 Tap a vibe and your feed builds itself instantly.")
        return
    html(cards.mood_banner_html(MOODS[mood]["line"]))
    html(cards.grid_html(_mood_picks(mood)))
    c1, c2, _ = st.columns([1, 1, 2])
    c1.button("🔀 Reshuffle feed", on_click=_reshuffle, use_container_width=True)
    if c2.button("✨ New boost line", use_container_width=True):
        st.session_state.boost = random.choice([b for b in BOOSTS if b != st.session_state.get("boost")])
        st.rerun()


def _tracker(show_id: str) -> None:
    meta = TRACKER_SHOWS[show_id]
    profile = get_profile()
    data = profile.tracker(show_id)
    today = now_ist().strftime("%Y-%m-%d")

    m1, m2, m3 = st.columns(3)
    m1.metric("Episodes watched", len(data["watched"]))
    m2.metric("Your notes", len(data["updates"]))
    m3.metric("Last watched", data["watched"][-1][5:] if data["watched"] else "—")

    watched_today = today in data["watched"]
    if st.button("↩️ Unmark today's episode" if watched_today else "✅ Watched today's episode",
                 key=f"watch_{show_id}", use_container_width=True):
        profile.toggle_watched(show_id, today)
        st.rerun()

    with st.form(f"upd_{show_id}", clear_on_submit=True, border=False):
        c1, c2 = st.columns([3, 1])
        text = c1.text_input("Log an update", placeholder="e.g. Nominations: 5 in danger zone 😬",
                             label_visibility="collapsed", max_chars=config.MAX_MESSAGE_LEN)
        tag = c2.selectbox("Tag", TRACKER_TAGS, label_visibility="collapsed")
        if st.form_submit_button("➕ Add to tracker", use_container_width=True) and text.strip():
            profile.add_update(show_id, text, tag, today)
            st.rerun()

    mine = [(i, u) for i, u in enumerate(data["updates"])]
    feed = [(None, u) for u in meta["seed_updates"]] + mine
    feed.sort(key=lambda pair: pair[1]["ts"], reverse=True)
    for idx, upd in feed[:8]:
        cols = st.columns([12, 1]) if idx is not None else [st.container()]
        with cols[0]:
            html(f'<div class="vs-update"><span class="d">{cards.esc(upd["ts"])}</span>'
                 f'<span class="vs-utag">{cards.esc(upd["tag"])}</span><span>{cards.esc(upd["text"])}</span></div>')
        if idx is not None and cols[1].button("✕", key=f"del_{show_id}_{idx}", help="Remove this note"):
            profile.remove_update(show_id, idx)
            st.rerun()

    link_cols = st.columns(len(meta["links"]))
    for col, (label, url) in zip(link_cols, meta["links"].items()):
        col.link_button(label, url, use_container_width=True)


def render() -> None:
    _hero()
    _mood_section()

    st.write("")
    if st.button("🎲  SURPRISE ME!", key="home_surprise", use_container_width=True):
        surprise("home")
    render_spotlight("home")

    # Anime & animation
    html(cards.section_html("🍥", "Anime & Animation", "Top-tier series + nostalgic comfort watches"))
    anime = items_of("anime")
    html(cards.grid_html([a for a in anime if not a["telugu"]]))
    html(cards.section_html("🔔", "Doraemon Comfort Zone · Telugu audio",
                            "Movie nights straight out of childhood. *Telugu dub availability varies by title"))
    html(cards.grid_html([a for a in anime if a["telugu"]]))

    # Reality TV central
    html(cards.section_html("👁️", "Reality TV Central", "Bigg Boss Telugu 10 is live. Track every episode and twist"))
    reality = items_of("reality")
    left, right = st.columns([1, 2], gap="large")
    with left:
        html(cards.grid_html(reality))
    with right:
        tabs = st.tabs([f"📋 {TRACKER_SHOWS[s]['title']}" for s in TRACKER_SHOWS])
        for tab, show_id in zip(tabs, TRACKER_SHOWS):
            with tab:
                _tracker(show_id)

    # Cinephile & sports vault
    html(cards.section_html("🎬", "Cinephile & Sports Vault", "Movies, binge-worthy series and live sports highlights"))
    t_movies, t_series, t_sports = st.tabs(["🎬 Movies", "📺 Series", "🏏 Sports"])
    with t_movies:
        html(cards.grid_html(items_of("movie")))
    with t_series:
        html(cards.grid_html(items_of("series")))
    with t_sports:
        html(cards.grid_html(items_of("sports")))
    st.caption("Platforms are for India and change often. * = check your region or language menu.")
