"""🎛️ Entertainment Matrix: filters, search, Surprise Me and favourites."""
from __future__ import annotations

import streamlit as st

from core import cards
from core.data import BY_ID, CATALOG, KIND_LABELS, all_genres, all_platforms, filter_items
from core.state import get_profile
from views.common import favorite_ids, html, render_spotlight, surprise


def render() -> None:
    html(cards.section_html("🎛️", "Entertainment Matrix", "Filter, search, or let fate decide"))

    kind = st.pills("Category", options=list(KIND_LABELS), format_func=KIND_LABELS.get,
                    default="all", key="mx_kind", label_visibility="collapsed") or "all"

    c1, c2, c3 = st.columns([2, 2, 2])
    query = c1.text_input("Search", placeholder="🔍 Search titles, genres, vibes…", label_visibility="collapsed")
    genres = c2.multiselect("Genres", all_genres(), placeholder="🏷️ Any genre", label_visibility="collapsed")
    platforms = c3.multiselect("Platforms", all_platforms(), placeholder="📡 Any platform", label_visibility="collapsed")
    telugu = st.toggle("తెలుగు  Telugu audio only", key="mx_telugu")

    results = filter_items(kind, query, genres, platforms, telugu)

    s1, s2 = st.columns([3, 1])
    with s1:
        if st.button("🎲  SURPRISE ME!", key="surprise", use_container_width=True,
                     help="Random pick from your favourites"):
            surprise("matrix")
    with s2:
        if st.button("🎯 Surprise from filters", use_container_width=True, disabled=not results,
                     help="Random pick from what's on screen right now"):
            surprise("matrix", results)
    render_spotlight("matrix")

    st.caption(f"{len(results)} pick{'s' if len(results) != 1 else ''} in the matrix")
    html(cards.grid_html(results))

    with st.expander("⭐ Manage my favourites (the Surprise Me! pool)"):
        current = favorite_ids()
        chosen = st.multiselect("Favourites", options=[i["id"] for i in CATALOG], default=current,
                                format_func=lambda i: f"{BY_ID[i]['emoji']} {BY_ID[i]['title']}",
                                label_visibility="collapsed")
        if st.button("💾 Save favourites"):
            get_profile().set_favorites(chosen)
            st.toast("Favourites saved 💜")
