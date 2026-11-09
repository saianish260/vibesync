"""Thread-safe JSON-backed stores.

Streamlit gives every browser tab its own session, but all sessions run in the
same Python process. RoomHub is created once (via st.cache_resource in
core/state.py) and shared, so friends connected to the same server see the same
rooms, chat and polls. Data is mirrored to JSON so a restart doesn't wipe rooms.

This module has no Streamlit imports, so it can be unit-tested directly.
"""
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from copy import deepcopy
from pathlib import Path
from typing import Callable

from . import config

CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # no 0/O, 1/I/L confusion
CODE_LEN = 6


def normalize_code(code: str) -> str:
    return "".join(ch for ch in (code or "").upper() if ch.isalnum())


def clean_name(name: str) -> str:
    return " ".join((name or "").split())[: config.MAX_NAME_LEN]


class JsonFile:
    def __init__(self, path: Path, default: dict):
        self.path = Path(path)
        self._lock = threading.RLock()
        self.data = self._load(default)

    def _load(self, default: dict) -> dict:
        try:
            with open(self.path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            return loaded if isinstance(loaded, dict) else deepcopy(default)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return deepcopy(default)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)   # atomic swap, no half-written files


# ───────────────────────── personal profile ─────────────────────────
class ProfileStore(JsonFile):
    """Your own settings: display name, favourites and episode-tracker logs."""

    def __init__(self, path: Path):
        super().__init__(path, {"name": "", "favorites": None, "trackers": {}})

    def name(self) -> str:
        return self.data.get("name", "")

    def set_name(self, name: str) -> None:
        with self._lock:
            self.data["name"] = clean_name(name)
            self.save()

    def favorites(self, default: list[str]) -> list[str]:
        favs = self.data.get("favorites")
        return list(default) if favs is None else list(favs)

    def set_favorites(self, ids: list[str]) -> None:
        with self._lock:
            self.data["favorites"] = list(ids)
            self.save()

    def _tracker(self, show: str) -> dict:
        return self.data.setdefault("trackers", {}).setdefault(show, {"watched": [], "updates": []})

    def tracker(self, show: str) -> dict:
        with self._lock:
            return deepcopy(self._tracker(show))

    def toggle_watched(self, show: str, day: str) -> bool:
        """Mark/unmark a day as watched. Returns the new state."""
        with self._lock:
            watched = self._tracker(show)["watched"]
            if day in watched:
                watched.remove(day)
                state = False
            else:
                watched.append(day)
                watched.sort()
                state = True
            self.save()
            return state

    def add_update(self, show: str, text: str, tag: str, day: str) -> None:
        text = (text or "").strip()[: config.MAX_MESSAGE_LEN]
        if not text:
            return
        with self._lock:
            self._tracker(show)["updates"].append({"ts": day, "tag": tag, "text": text})
            self.save()

    def remove_update(self, show: str, index: int) -> None:
        with self._lock:
            updates = self._tracker(show)["updates"]
            if 0 <= index < len(updates):
                updates.pop(index)
                self.save()


# ───────────────────────── shared rooms ─────────────────────────
class RoomHub(JsonFile):
    def __init__(self, path: Path, clock: Callable[[], float] = time.time):
        super().__init__(path, {"rooms": {}})
        self.clock = clock
        self.presence: dict[str, dict[str, float]] = {}   # in-memory only

    # internals
    def _room(self, code: str) -> dict | None:
        return self.data["rooms"].get(normalize_code(code))

    def _touch(self, room: dict) -> None:
        room["updated"] = self.clock()
        room["version"] = room.get("version", 0) + 1

    def _append(self, room: dict, user: str, text: str, kind: str = "msg", badge: str = "none") -> None:
        room["seq"] = room.get("seq", 0) + 1
        room["messages"].append({"id": room["seq"], "ts": self.clock(), "user": user,
                                 "text": text, "kind": kind, "badge": badge})
        overflow = len(room["messages"]) - config.MAX_MESSAGES
        if overflow > 0:
            del room["messages"][:overflow]

    def _new_code(self) -> str:
        while True:
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
            if code not in self.data["rooms"]:
                return code

    # public API
    def create_room(self, name: str, host: str) -> str:
        host = clean_name(host) or "Host"
        with self._lock:
            self.cleanup()
            code = self._new_code()
            room = {"code": code, "name": (name or "").strip()[:40] or f"{host}'s room",
                    "host": host, "created": self.clock(), "members": [host],
                    "messages": [], "poll": None, "sync": None, "seq": 0}
            self._append(room, host, f"{host} opened the room. Share code {code}!", kind="system")
            self._touch(room)
            self.data["rooms"][code] = room
            self.save()
        self.heartbeat(code, host)
        return code

    def exists(self, code: str) -> bool:
        return self._room(code) is not None

    def snapshot(self, code: str) -> dict | None:
        with self._lock:
            room = self._room(code)
            return deepcopy(room) if room else None

    def join(self, code: str, user: str) -> bool:
        user = clean_name(user)
        with self._lock:
            room = self._room(code)
            if room is None or not user:
                return False
            if user not in room["members"]:
                room["members"].append(user)
                self._append(room, user, f"{user} joined the vibe ✨", kind="system")
                self._touch(room)
                self.save()
        self.heartbeat(code, user)
        return True

    def leave(self, code: str, user: str) -> None:
        code = normalize_code(code)
        with self._lock:
            self.presence.get(code, {}).pop(user, None)
            room = self._room(code)
            if room:
                self._append(room, user, f"{user} left the room 👋", kind="system")
                self._touch(room)
                self.save()

    def heartbeat(self, code: str, user: str) -> None:
        with self._lock:
            self.presence.setdefault(normalize_code(code), {})[user] = self.clock()

    def online(self, code: str) -> list[str]:
        cutoff = self.clock() - config.ONLINE_WINDOW_SECONDS
        with self._lock:
            seen = self.presence.get(normalize_code(code), {})
            return sorted(u for u, t in seen.items() if t >= cutoff)

    def post(self, code: str, user: str, text: str, badge: str = "none") -> bool:
        text = (text or "").strip()[: config.MAX_MESSAGE_LEN]
        with self._lock:
            room = self._room(code)
            if room is None or not text:
                return False
            self._append(room, user, text, badge=badge)
            self._touch(room)
            self.save()
            return True

    def react(self, code: str, user: str, emoji: str) -> bool:
        with self._lock:
            room = self._room(code)
            if room is None:
                return False
            self._append(room, user, emoji, kind="reaction")
            self._touch(room)
            self.save()
            return True

    def create_poll(self, code: str, user: str, question: str, options: list[str]) -> bool:
        seen, opts = set(), []
        for opt in options:
            opt = (opt or "").strip()[:60]
            if opt and opt.lower() not in seen:
                seen.add(opt.lower())
                opts.append(opt)
        if len(opts) < 2:
            return False
        with self._lock:
            room = self._room(code)
            if room is None:
                return False
            room["poll"] = {"question": (question or "").strip()[:80] or "What are we watching?",
                            "by": user, "ts": self.clock(),
                            "options": [{"label": o, "votes": []} for o in opts[:8]]}
            self._append(room, user, f"{user} started a poll: {room['poll']['question']}", kind="system")
            self._touch(room)
            self.save()
            return True

    def vote(self, code: str, user: str, index: int) -> bool:
        """One vote per person. Voting again for the same option removes the vote."""
        with self._lock:
            room = self._room(code)
            poll = room and room.get("poll")
            if not poll or not 0 <= index < len(poll["options"]):
                return False
            already = user in poll["options"][index]["votes"]
            for opt in poll["options"]:
                if user in opt["votes"]:
                    opt["votes"].remove(user)
            if not already:
                poll["options"][index]["votes"].append(user)
            self._touch(room)
            self.save()
            return True

    def clear_poll(self, code: str, user: str) -> None:
        with self._lock:
            room = self._room(code)
            if room and room.get("poll"):
                room["poll"] = None
                self._append(room, user, f"{user} closed the poll", kind="system")
                self._touch(room)
                self.save()

    def start_sync(self, code: str, user: str, title: str,
                   delay: int = config.SYNC_COUNTDOWN_SECONDS) -> bool:
        with self._lock:
            room = self._room(code)
            if room is None or not title:
                return False
            room["sync"] = {"title": title[:80], "by": user, "start_at": self.clock() + delay}
            self._append(room, user, f"{user} started a sync countdown for {title} ▶", kind="system")
            self._touch(room)
            self.save()
            return True

    def cleanup(self) -> int:
        cutoff = self.clock() - config.ROOM_TTL_HOURS * 3600
        with self._lock:
            stale = [c for c, r in self.data["rooms"].items() if r.get("updated", 0) < cutoff]
            for code in stale:
                self.data["rooms"].pop(code, None)
                self.presence.pop(code, None)
            if stale:
                self.save()
            return len(stale)


def poll_winner(poll: dict | None) -> str | None:
    if not poll:
        return None
    best = max(poll["options"], key=lambda o: len(o["votes"]))
    return best["label"] if best["votes"] else None
