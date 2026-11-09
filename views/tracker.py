"""Reality TV episode tracker (used inside Browse → Reality TV)."""
from __future__ import annotations

import streamlit as st

from core import cards, config
from core.data import TRACKER_SHOWS, TRACKER_TAGS
from core.state import get_profile
from views.common import html, now_ist


def render(show_id: str) -> None:
    meta = TRACKER_SHOWS[show_id]
    profile = get_profile()
    data = profile.tracker(show_id)
    today = now_ist().strftime("%Y-%m-%d")

    m1, m2, m3 = st.columns(3)
    m1.metric("Watched", len(data["watched"]))
    m2.metric("Notes", len(data["updates"]))
    m3.metric("Last", data["watched"][-1][5:] if data["watched"] else "—")

    watched_today = today in data["watched"]
    if st.button("↩️ Unmark today" if watched_today else "✅ Watched today's episode",
                 key=f"watch_{show_id}", use_container_width=True):
        profile.toggle_watched(show_id, today)
        st.rerun()

    with st.form(f"upd_{show_id}", clear_on_submit=True, border=False):
        text = st.text_input("Log an update", placeholder="e.g. Nominations: 5 in danger zone",
                             max_chars=config.MAX_MESSAGE_LEN)
        tag = st.selectbox("Tag", TRACKER_TAGS)
        if st.form_submit_button("➕ Add note", use_container_width=True) and text.strip():
            profile.add_update(show_id, text, tag, today)
            st.rerun()

    feed = [(None, u) for u in meta["seed_updates"]] + list(enumerate(data["updates"]))
    feed.sort(key=lambda pair: pair[1]["ts"], reverse=True)
    for idx, upd in feed[:8]:
        row = st.columns([10, 1]) if idx is not None else [st.container()]
        with row[0]:
            html(f'<div class="vs-update"><span class="d">{cards.esc(upd["ts"])}</span>'
                 f'<span class="vs-utag">{cards.esc(upd["tag"])}</span><span>{cards.esc(upd["text"])}</span></div>')
        if idx is not None and row[1].button("✕", key=f"del_{show_id}_{idx}", help="Remove note"):
            profile.remove_update(show_id, idx)
            st.rerun()

    for label, url in meta["links"].items():
        st.link_button(label, url, use_container_width=True)
