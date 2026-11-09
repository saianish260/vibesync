"""🧭 Browse: category tabs with grouped rows, search, filters, favourites.

Only the selected category is rendered (pills, not st.tabs), which keeps every
tap light on phones.
"""
from __future__ import annotations

import streamlit as st

from core import cards
from core.data import (BY_ID, CATALOG, CATEGORIES, GROUPS, TRACKER_SHOWS, all_genres, all_platforms,
                       filter_items)
from core.state import get_profile
from views import tracker
from views.common import favorite_ids, html, render_spotlight, surprise


def _matches(item: dict, genres, platforms, telugu: bool) -> bool:
    if genres and not set(genres) & set(item["genres"]):
        return False
    if platforms and not set(platforms) & {p.rstrip("*") for p in item["platforms"]}:
        return False
    return not telugu or item["telugu"]


def _filters() -> tuple[list, list, bool]:
    active = bool(st.session_state.get("br_genres") or st.session_state.get("br_platforms")
                  or st.session_state.get("br_telugu"))
    with st.expander("⚙️ Filters" + (" · on" if active else ""), expanded=False):
        genres = st.multiselect("Genre", all_genres(), key="br_genres", placeholder="Any genre")
        platforms = st.multiselect("Platform", all_platforms(), key="br_platforms", placeholder="Any platform")
        telugu = st.toggle("Telugu audio only", key="br_telugu")
    return genres, platforms, telugu


def _keep_cat() -> None:
    """Tapping the selected category again would clear it; keep the last one instead."""
    if st.session_state.get("br_cat"):
        st.session_state.br_cat_last = st.session_state.br_cat
    else:
        st.session_state.br_cat = st.session_state.get("br_cat_last", "anime")


def render() -> None:
    query = st.text_input("Search", placeholder="🔍 Search titles, genres…", key="br_query",
                          label_visibility="collapsed").strip()
    if "br_cat" not in st.session_state:
        st.session_state.br_cat = "anime"
    cat = st.pills("Category", options=list(CATEGORIES), format_func=CATEGORIES.get,
                   key="br_cat", on_change=_keep_cat, label_visibility="collapsed") or "anime"
    st.session_state.br_cat_last = cat
    genres, platforms, telugu = _filters()

    # Search mode: one grid across everything
    if query:
        results = filter_items("all", query, genres, platforms, telugu)
        html(cards.section_html("🔍", f'Results for "{query}"', f"{len(results)} found"))
        html(cards.grid_html(results))
        return

    # Category mode: grouped rows
    in_cat = [i for i in CATALOG if i["kind"] == cat and _matches(i, genres, platforms, telugu)]
    st.button(f"🎲  Surprise me with {CATEGORIES[cat].split(' ', 1)[1]}", key="surprise",
              use_container_width=True, disabled=not in_cat, on_click=surprise, args=("browse", in_cat))
    render_spotlight("browse")

    shown = 0
    for title, ids in GROUPS[cat]:
        row = [BY_ID[i] for i in ids if _matches(BY_ID[i], genres, platforms, telugu)]
        if row:
            shown += len(row)
            html(cards.section_html("", title, f"{len(row)} · swipe →" if len(row) > 2 else ""))
            html(cards.rail_html(row))
    if not shown:
        html(cards.EMPTY)

    if cat == "reality":
        html(cards.section_html("📋", "Episode tracker"))
        show = st.pills("Show", options=list(TRACKER_SHOWS), format_func=lambda s: TRACKER_SHOWS[s]["title"],
                        default="bbt10", key="br_show", label_visibility="collapsed") or "bbt10"
        tracker.render(show)

    with st.expander("⭐ Manage favourites (used by Surprise Me on Home)"):
        chosen = st.multiselect("Favourites", options=[i["id"] for i in CATALOG], default=favorite_ids(),
                                format_func=lambda i: f"{BY_ID[i]['emoji']} {BY_ID[i]['title']}",
                                label_visibility="collapsed")
        if st.button("💾 Save favourites"):
            get_profile().set_favorites(chosen)
            st.toast("Favourites saved")
