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
from zoneinfo import ZoneInfo

from . import config
from .emoji import BADGES, expand

AVATAR_COLORS = ["#F4B942", "#5EE6B8", "#FF8A7A", "#9FB7FF", "#E9A6FF", "#7DD3FC"]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def section_html(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<span class="vs-sec-sub">{esc(subtitle)}</span>' if subtitle else ""
    return (f'<div class="vs-section"><div class="vs-sec-title"><span class="ic">{icon}</span>{esc(title)}</div>'
            f'{sub}</div>')


# ───────────────────────── Lounge ─────────────────────────
def _color_for(name: str) -> str:
    return AVATAR_COLORS[int(hashlib.md5(name.encode()).hexdigest(), 16) % len(AVATAR_COLORS)]


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


def countdown_component_html(title: str, start_at: float, pal: dict) -> str:
    """Self-contained page for st.components.v1.html. Counts down client-side from an absolute timestamp."""
    t = esc(title)
    return f"""<!doctype html><html><head><style>
body{{margin:0;font-family:system-ui,sans-serif;background:transparent;color:{pal['text']}}}
.box{{border-radius:18px;padding:14px 16px;text-align:center;background:{pal['s1']};border:1px solid {pal['line']}}}
.t{{font-size:13px;color:{pal['muted']}}}
.n{{font-size:46px;font-weight:800;margin:2px 0;color:{pal['accent']};transition:transform .2s}}
.s{{font-size:15px}}
</style></head><body><div class="box"><div class="t">Sync watch starts in</div><div class="n" id="n">…</div>
<div class="s">{t}</div></div><script>
const start={start_at * 1000:.0f};
function tick(){{const left=Math.ceil((start-Date.now())/1000);const n=document.getElementById('n');
if(left>0){{if(n.textContent!==String(left)){{n.textContent=left;n.style.transform='scale(1.15)';setTimeout(()=>n.style.transform='',150);}}}}
else if(left>-900){{n.textContent='Press play';}}else{{n.textContent='Done';}}}}
tick();setInterval(tick,250);
</script></body></html>"""
