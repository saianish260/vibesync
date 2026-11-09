"""Pure HTML builders for the custom UI (no Streamlit import, so they are testable).

Everything is emitted as compact single-line HTML. Streamlit's markdown renderer
treats indented lines as code blocks, so we never put newlines or leading
indentation inside these strings.
"""
from __future__ import annotations

import hashlib
import html
import random
from datetime import datetime
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

from . import config
from .emoji import BADGES, expand

KIND_TAG = {"movie": "MOVIE", "series": "SERIES", "anime": "ANIME", "reality": "REALITY", "sports": "SPORTS"}
NEON = ["#22D3EE", "#7C5CFF", "#FF4D8D", "#34D399", "#FBBF24", "#60A5FA"]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def trailer_url(item: dict) -> str:
    if item.get("trailer_query"):
        q = item["trailer_query"]
    elif item["kind"] == "sports":
        q = f"{item['title']} latest"
    else:
        q = f"{item['title']} official trailer"
    return "https://www.youtube.com/results?search_query=" + quote_plus(q)


def play_label(item: dict) -> str:
    return {"sports": "▶ Highlights", "reality": "▶ Promos"}.get(item["kind"], "▶ Trailer")


def poster_html(item: dict) -> str:
    c1, c2 = item["colors"]
    style = f"--c1:{c1};--c2:{c2};"
    art = f'<span class="vs-emoji">{item["emoji"]}</span>'
    if item.get("poster"):
        style += f"background:url('{esc(item['poster'])}') center/cover;"
        art = ""
    status = item.get("status")
    if status == "live":
        badge = '<span class="vs-live"><i></i>LIVE</span>'
    elif status:
        badge = f'<span class="vs-status">{esc(status.upper())}</span>'
    else:
        badge = ""
    tel = '<span class="vs-tel">తెలుగు</span>' if item.get("telugu") else ""
    return (f'<div class="vs-poster" style="{style}"><span class="vs-kind">{KIND_TAG[item["kind"]]}</span>'
            f'{badge}{tel}{art}</div>')


def _meta(item: dict) -> str:
    return esc(item.get("meta") or item.get("year", ""))


def _body_html(item: dict) -> str:
    tags = "".join(f'<span class="vs-tag">{esc(g)}</span>' for g in item["genres"][:3])
    plats = " · ".join(esc(p) for p in item["platforms"])
    return (f'<div class="vs-body"><div class="vs-title">{esc(item["title"])}</div>'
            f'<div class="vs-meta">{_meta(item)}</div><div class="vs-tags">{tags}</div>'
            f'<p class="vs-syn">{esc(item["synopsis"])}</p>'
            f'<div class="vs-plat"><b>Watch on</b> {plats}</div>'
            f'<a class="vs-play" href="{esc(trailer_url(item))}" target="_blank" rel="noopener noreferrer">'
            f'{play_label(item)}</a></div>')


def card_html(item: dict) -> str:
    return f'<div class="vs-card">{poster_html(item)}{_body_html(item)}</div>'


EMPTY = '<div class="vs-empty">Nothing matches. Try clearing the filters or a different search.</div>'


def grid_html(items: list[dict]) -> str:
    if not items:
        return EMPTY
    return '<div class="vs-grid">' + "".join(card_html(it) for it in items) + "</div>"


def rail_html(items: list[dict]) -> str:
    """One horizontally scrolling row (swipe on phones)."""
    if not items:
        return ""
    return '<div class="vs-rail">' + "".join(card_html(it) for it in items) + "</div>"


def wide_card_html(item: dict) -> str:
    return f'<div class="vs-wide">{poster_html(item)}{_body_html(item)}</div>'


def spotlight_html(item: dict) -> str:
    return (f'<div class="vs-spotlight"><div class="vs-spot-label">🎲 YOUR PICK</div>'
            f'<div class="vs-spot-inner">{poster_html(item)}{_body_html(item)}</div></div>')


def confetti_html(n: int = 36, seed: int | None = None) -> str:
    rng = random.Random(seed)
    bits = []
    for _ in range(n):
        bits.append(
            f'<i style="left:{rng.uniform(0, 100):.1f}%;background:{rng.choice(NEON)};'
            f'animation-delay:{rng.uniform(0, .5):.2f}s;animation-duration:{rng.uniform(1.4, 2.2):.2f}s"></i>')
    return '<div class="vs-confetti">' + "".join(bits) + "</div>"


def section_html(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<span class="vs-sec-sub">{esc(subtitle)}</span>' if subtitle else ""
    return (f'<div class="vs-section"><div class="vs-sec-title"><span class="ic">{icon}</span>{esc(title)}</div>'
            f'{sub}</div>')


def hello_html(greeting: str, name: str, boost: str) -> str:
    who = f", {esc(name)}" if name else ""
    return (f'<div class="vs-hello"><div><h2>{esc(greeting)}{who} 👋</h2>'
            f'<div class="sub">What are we watching today?</div></div>'
            f'<div class="vs-boost">{esc(boost)}</div></div>')


def mood_banner_html(line: str) -> str:
    return f'<div class="vs-moodline">{esc(line)}</div>'


# ───────────────────────── Lounge ─────────────────────────
def _color_for(name: str) -> str:
    return NEON[int(hashlib.md5(name.encode()).hexdigest(), 16) % len(NEON)]


def _clock(ts: float) -> str:
    return datetime.fromtimestamp(ts, ZoneInfo(config.TIMEZONE)).strftime("%I:%M %p").lstrip("0")


def message_html(msg: dict, me: str) -> str:
    kind = msg.get("kind", "msg")
    if kind == "system":
        return f'<div class="vs-sys">{esc(msg["text"])}</div>'
    if kind == "reaction":
        return f'<div class="vs-sys"><b>{esc(msg["user"])}</b> reacted <span class="vs-r">{esc(msg["text"])}</span></div>'
    label, mod = BADGES.get(msg.get("badge") or "none", BADGES["none"])
    chip = f'<span class="vs-chip {mod}">{esc(label)}</span>' if mod else ""
    text = expand(esc(msg["text"]))
    if mod == "spoiler":
        text = f'<span class="vs-spoiler" tabindex="0">{text}</span>'
    mine = " mine" if msg["user"] == me else ""
    color = _color_for(msg["user"])
    initial = esc(msg["user"][:1].upper() or "?")
    return (f'<div class="vs-msg{mine}"><span class="vs-av" style="--av:{color}">{initial}</span>'
            f'<div class="vs-bubble"><div class="vs-mhead"><b style="color:{color}">{esc(msg["user"])}</b>'
            f'{chip}<span class="vs-time">{_clock(msg["ts"])}</span></div>'
            f'<div class="vs-mtext">{text}</div></div></div>')


def chat_html(messages: list[dict], me: str) -> str:
    """Newest-first inside a column-reverse box, so the scroll naturally sits at the bottom."""
    if not messages:
        inner = '<div class="vs-sys">No messages yet. Say hi 👋</div>'
    else:
        inner = "".join(message_html(m, me) for m in reversed(messages))
    return f'<div class="vs-chat">{inner}</div>'


def floating_reactions_html(messages: list[dict], now: float, window: float = 4.0) -> str:
    recent = [m for m in messages if m.get("kind") == "reaction" and now - m["ts"] <= window]
    if not recent:
        return ""
    spans = []
    for m in recent[-12:]:
        rng = random.Random(m["id"])
        spans.append(f'<span style="left:{rng.uniform(5, 90):.0f}%;animation-delay:{rng.uniform(0, .3):.2f}s">'
                     f'{esc(m["text"])}</span>')
    return '<div class="vs-floaters">' + "".join(spans) + "</div>"


def poll_html(poll: dict, me: str) -> str:
    total = sum(len(o["votes"]) for o in poll["options"]) or 1
    top = max(len(o["votes"]) for o in poll["options"])
    rows = []
    for opt in poll["options"]:
        n = len(opt["votes"])
        pct = round(100 * n / total)
        lead = " lead" if n and n == top else ""
        mine = " ✓" if me in opt["votes"] else ""
        rows.append(f'<div class="vs-pollrow{lead}"><div class="vs-pollfill" style="width:{pct}%"></div>'
                    f'<span class="vs-polllabel">{esc(opt["label"])}{mine}</span>'
                    f'<span class="vs-pollpct">{n} · {pct}%</span></div>')
    return (f'<div class="vs-poll"><div class="vs-pollq">🗳️ {esc(poll["question"])}</div>'
            + "".join(rows) + "</div>")


def members_html(online: list[str], members: list[str], host: str) -> str:
    chips = []
    for name in members:
        on = name in online
        crown = " 👑" if name == host else ""
        cls = "vs-member on" if on else "vs-member"
        chips.append(f'<span class="{cls}" style="--av:{_color_for(name)}"><i></i>{esc(name)}{crown}</span>')
    return f'<div class="vs-members"><div class="vs-online">{len(online)} online</div>' + "".join(chips) + "</div>"


def countdown_component_html(title: str, start_at: float) -> str:
    """Self-contained page for st.components.v1.html. Counts down client-side from an absolute timestamp."""
    t = esc(title)
    return f"""<!doctype html><html><head><style>
body{{margin:0;font-family:'Segoe UI',system-ui,sans-serif;background:transparent;color:#EEF0FA}}
.box{{border:1px solid rgba(124,92,255,.5);border-radius:16px;padding:14px 16px;text-align:center;
background:#151827}}
.t{{font-size:13px;letter-spacing:.12em;color:#9AA0B8;text-transform:uppercase}}
.n{{font-size:44px;font-weight:800;margin:4px 0;color:#22D3EE}}
.s{{font-size:15px}}
</style></head><body><div class="box"><div class="t">Sync watch</div><div class="n" id="n">…</div>
<div class="s">{t}</div></div><script>
const start={start_at * 1000:.0f};
function tick(){{const left=Math.ceil((start-Date.now())/1000);const n=document.getElementById('n');
if(left>0){{n.textContent=left;}}else if(left>-900){{n.textContent='▶ PLAY NOW';n.style.color='#34D399';}}else{{n.textContent='Done';}}}}
tick();setInterval(tick,250);
</script></body></html>"""
