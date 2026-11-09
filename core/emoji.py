"""Custom chat emojis (shortcodes), message badges and quick reactions."""
from __future__ import annotations

import re

SHORTCODES = {
    ":fire:": "🔥", ":lol:": "😂", ":skull:": "💀", ":goat:": "🐐", ":popcorn:": "🍿",
    ":cry:": "😭", ":clap:": "👏", ":mind:": "🤯", ":heart:": "💜", ":sus:": "🤨",
    ":hype:": "⚡", ":bb:": "👁️", ":evicted:": "🚪", ":nominated:": "🎯", ":captain:": "👑",
    ":six:": "🏏", ":goal:": "⚽", ":out:": "☝️", ":anya:": "🥜", ":dora:": "🔔",
    ":gg:": "🎮", ":tea:": "🍵", ":mass:": "💥", ":whistle:": "😗🎶",
}

# key -> (label shown on the chip, css modifier)
BADGES = {
    "none":    ("💬 Chat", ""),
    "hot":     ("🌶️ Hot take", "hot"),
    "spoiler": ("⚠️ Spoiler", "spoiler"),
    "hype":    ("⚡ Hype", "hype"),
    "elim":    ("🚪 Elimination", "elim"),
}

REACTIONS = ["🔥", "😂", "💀", "🐐", "🍿", "😭", "🤯", "👏"]

_CODE_RE = re.compile(r":[a-z0-9_]+:")


def expand(text: str) -> str:
    """Replace :shortcodes: with emojis. Unknown codes are left untouched."""
    return _CODE_RE.sub(lambda m: SHORTCODES.get(m.group(0), m.group(0)), text)
