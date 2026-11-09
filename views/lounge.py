"""🛋️ Peer Interactive Lounge: shared rooms, live chat, reactions, polls and sync-watch."""
from __future__ import annotations

import time

import streamlit as st
import streamlit.components.v1 as components

from core import cards, config, styles
from core.data import CATALOG
from core.emoji import BADGES, REACTIONS, SHORTCODES
from core.state import get_hub
from core.store import clean_name, normalize_code, poll_winner

REFRESH = config.CHAT_REFRESH_SECONDS


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ───────────────────────── helpers ─────────────────────────
def _me() -> str:
    return st.session_state.get("lounge_name", "")


def _code() -> str:
    return st.session_state.get("lounge_code", "")


def _enter(code: str, name: str) -> None:
    st.session_state.lounge_code = code
    st.session_state.lounge_name = name
    st.query_params["room"] = code


def _leave() -> None:
    get_hub().leave(_code(), _me())
    st.session_state.pop("lounge_code", None)
    st.query_params.pop("room", None)


def _share_link(code: str) -> str:
    try:
        headers = st.context.headers
        host = headers.get("X-Forwarded-Host") or headers.get("Host") or "localhost:8501"
        proto = headers.get("X-Forwarded-Proto") or ("http" if host.startswith(("localhost", "127.", "192.168.", "10.")) else "https")
    except Exception:                       # very old Streamlit without st.context
        host, proto = "localhost:8501", "http"
    return f"{proto}://{host}/?room={code}"


# ───────────────────────── lobby ─────────────────────────
def _lobby() -> None:
    html(cards.section_html("", "Watch together", "Open a room, share the code, vote on what to watch and chat live."))
    hub = get_hub()
    default_name = st.session_state.get("lounge_name", "")
    name = clean_name(st.text_input("Your display name", value=default_name, max_chars=config.MAX_NAME_LEN,
                                    placeholder="e.g. Anish"))
    invited = normalize_code(st.query_params.get("room", ""))

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown("#### ✨ Create a room")
            room_name = st.text_input("Room name", placeholder="BB Telugu weekend watch 👁️", max_chars=40)
            if st.button("🚀 Create room", use_container_width=True, disabled=not name):
                code = hub.create_room(room_name, name)
                _enter(code, name)
                st.rerun()
    with right:
        with st.container(border=True):
            st.markdown("#### 🔑 Join with a code")
            code_in = st.text_input("Room code", value=invited, placeholder="e.g. 7KQ2XM", max_chars=12)
            if st.button("🎟️ Join room", use_container_width=True, disabled=not (name and code_in)):
                code = normalize_code(code_in)
                if hub.join(code, name):
                    _enter(code, name)
                    st.rerun()
                else:
                    st.error("That room doesn't exist (or expired). Double-check the code.")
    if not name:
        st.caption("Enter a display name to create or join a room.")
    if invited and not hub.exists(invited):
        st.warning(f"The invite link points to room {invited}, which no longer exists.")


# ───────────────────────── live view (one fragment) ─────────────────────────
@st.fragment(run_every=REFRESH)
def _live_room() -> None:
    """Chat, members, poll and sync countdown refresh together, once every few seconds."""
    hub, code, me = get_hub(), _code(), _me()
    room = hub.snapshot(code)
    if room is None:
        st.warning("This room has closed.")
        return
    hub.heartbeat(code, me)

    chat_col, side_col = st.columns([3, 2], gap="medium")
    with chat_col:
        html(cards.floating_reactions_html(room["messages"], time.time()))
        html(cards.chat_html(room["messages"], me))
        cols = st.columns(len(REACTIONS))
        for col, emo in zip(cols, REACTIONS):
            if col.button(emo, key=f"react_{emo}", use_container_width=True):
                hub.react(code, me, emo)
                st.rerun(scope="fragment")

    with side_col:
        html(cards.members_html(hub.online(code), room["members"], room["host"]))
        poll = room.get("poll")
        if poll:
            html(cards.poll_html(poll, me))
            for i, opt in enumerate(poll["options"]):
                mine = me in opt["votes"]
                if st.button(("✅ " if mine else "🗳️ ") + opt["label"], key=f"vote_{poll['ts']}_{i}",
                             use_container_width=True):
                    hub.vote(code, me, i)
                    st.rerun(scope="fragment")
            c1, c2 = st.columns(2)
            winner = poll_winner(poll)
            if c1.button("▶ Sync-start", use_container_width=True, disabled=not winner,
                         help="Start a 10-second countdown on everyone's screen for the leading option"):
                hub.start_sync(code, me, winner)
                st.rerun(scope="fragment")
            if c2.button("🧹 Close poll", use_container_width=True):
                hub.clear_poll(code, me)
                st.rerun(scope="fragment")
        sync = room.get("sync")
        if sync and time.time() - sync["start_at"] < 15 * 60:
            components.html(cards.countdown_component_html(sync["title"], sync["start_at"], styles.palette(st.session_state.get("theme", "cinema"))), height=140)


def _new_poll_form() -> None:
    """Outside the live fragment so auto-refresh never interrupts typing."""
    hub, code, me = get_hub(), _code(), _me()
    with st.expander("🗳️ Start a watch poll"):
        with st.form("new_poll", clear_on_submit=True, border=False):
            question = st.text_input("Question", value="What are we watching tonight?", max_chars=80)
            picks = st.multiselect("Pick options", [i["title"] for i in CATALOG], max_selections=6,
                                   placeholder="Choose 2-6 titles…")
            extra = st.text_input("Or add your own (comma separated)",
                                  placeholder="BBT10 weekend episode, Nominations promo")
            if st.form_submit_button("Launch poll", use_container_width=True):
                options = picks + [x for x in extra.split(",") if x.strip()]
                if hub.create_poll(code, me, question, options):
                    st.toast("Poll is live 🗳️")
                else:
                    st.error("Add at least 2 different options.")


# ───────────────────────── room ─────────────────────────
def _room() -> None:
    hub, code, me = get_hub(), _code(), _me()
    room = hub.snapshot(code)
    if room is None:
        st.session_state.pop("lounge_code", None)
        st.query_params.pop("room", None)
        st.toast("That room has closed or expired.", icon="🚪")
        st.rerun()
    hub.join(code, me)   # no-op if already a member; restores presence after refresh

    html(f'<div class="vs-roomhead"><div><div class="vs-roomname">{cards.esc(room["name"])}</div>'
         f'<div style="color:var(--muted);font-size:.85rem">You are <b>{cards.esc(me)}</b> · host {cards.esc(room["host"])}</div></div>'
         f'<div class="vs-code">{code}</div></div>')

    _live_room()

    badge = st.pills("Message type", options=list(BADGES), format_func=lambda k: BADGES[k][0],
                     default="none", key="badge", label_visibility="collapsed") or "none"
    text = st.chat_input("Drop a hot take… (try :fire: :goat: :evicted:)", max_chars=config.MAX_MESSAGE_LEN)
    if text:
        hub.post(code, me, text, badge)
        st.rerun()

    _new_poll_form()
    with st.expander("🔗 Invite friends"):
        st.write("Share this link or just the code.")
        st.code(_share_link(code), language=None)
    with st.expander("😎 Custom emoji codes"):
        html('<div class="vs-tags">' + "".join(
            f'<span class="vs-tag">{cards.esc(k)} {v}</span>' for k, v in SHORTCODES.items()) + "</div>")
    st.button("🚪 Leave room", on_click=_leave, use_container_width=True)


def render() -> None:
    if _code() and _me():
        _room()
    else:
        _lobby()
