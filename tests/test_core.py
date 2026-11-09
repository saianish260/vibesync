"""Run with:  python -m unittest discover tests"""
import tempfile
import unittest
from pathlib import Path

from core import cards, data
from core.emoji import expand
from core.store import ProfileStore, RoomHub, normalize_code, poll_winner


class FakeClock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class RoomHubTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "rooms.json"
        self.clock = FakeClock()
        self.hub = RoomHub(self.path, clock=self.clock)

    def tearDown(self):
        self.dir.cleanup()

    def test_create_join_chat_and_persist(self):
        code = self.hub.create_room("BB night", "Anish")
        self.assertEqual(len(code), 6)
        self.assertTrue(self.hub.join(code.lower(), "Ravi"))         # codes are case-insensitive
        self.assertFalse(self.hub.join("NOPE00", "Ravi"))
        self.assertTrue(self.hub.post(code, "Ravi", "who's getting evicted :evicted:", "hot"))
        self.assertFalse(self.hub.post(code, "Ravi", "   "))
        reloaded = RoomHub(self.path, clock=self.clock)                # survives a restart
        room = reloaded.snapshot(code)
        self.assertEqual(room["members"], ["Anish", "Ravi"])
        self.assertEqual(room["messages"][-1]["badge"], "hot")

    def test_votes_are_one_per_person_and_toggle(self):
        code = self.hub.create_room("", "A")
        self.assertFalse(self.hub.create_poll(code, "A", "q", ["Only one", "only ONE"]))  # dupes collapse
        self.assertTrue(self.hub.create_poll(code, "A", "q", ["Pushpa 2", "Frieren", "BBT10"]))
        self.hub.vote(code, "A", 0)
        self.hub.vote(code, "B", 0)
        self.hub.vote(code, "A", 1)          # A switches vote
        poll = self.hub.snapshot(code)["poll"]
        self.assertEqual([len(o["votes"]) for o in poll["options"]], [1, 1, 0])
        self.hub.vote(code, "A", 1)          # tapping again removes it
        poll = self.hub.snapshot(code)["poll"]
        self.assertEqual(poll_winner(poll), "Pushpa 2")

    def test_presence_window_and_cleanup(self):
        code = self.hub.create_room("", "A")
        self.hub.heartbeat(code, "B")
        self.assertEqual(self.hub.online(code), ["A", "B"])
        self.clock.t += 60
        self.hub.heartbeat(code, "B")
        self.assertEqual(self.hub.online(code), ["B"])
        self.clock.t += 25 * 3600
        self.assertEqual(self.hub.cleanup(), 1)
        self.assertFalse(self.hub.exists(code))

    def test_message_cap(self):
        code = self.hub.create_room("", "A")
        for i in range(260):
            self.hub.post(code, "A", f"m{i}")
        msgs = self.hub.snapshot(code)["messages"]
        self.assertEqual(len(msgs), 200)
        self.assertEqual(msgs[-1]["text"], "m259")

    def test_normalize_code(self):
        self.assertEqual(normalize_code(" ab-12 c "), "AB12C")


class ProfileTests(unittest.TestCase):
    def test_tracker_and_favorites(self):
        with tempfile.TemporaryDirectory() as d:
            p = ProfileStore(Path(d) / "profile.json")
            self.assertEqual(p.favorites(["x"]), ["x"])
            p.set_favorites([])
            self.assertEqual(p.favorites(["x"]), [])                   # empty list is respected
            self.assertTrue(p.toggle_watched("bbt10", "2026-11-09"))
            self.assertFalse(p.toggle_watched("bbt10", "2026-11-09"))
            p.add_update("bbt10", "Captaincy task chaos", "Captaincy", "2026-11-09")
            again = ProfileStore(Path(d) / "profile.json")
            self.assertEqual(again.tracker("bbt10")["updates"][0]["tag"], "Captaincy")


class CardTests(unittest.TestCase):
    def test_catalog_integrity(self):
        ids = [i["id"] for i in data.CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        for item in data.CATALOG:
            self.assertIn(item["kind"], cards.KIND_TAG)
            self.assertEqual(len(item["colors"]), 2)
        for mood in data.MOODS:
            self.assertGreaterEqual(len(data.items_for_mood(mood)), 4, mood)
        self.assertTrue(all(BY in data.BY_ID for BY in data.default_favorites()))

    def test_html_is_single_line_and_escaped(self):
        for item in data.CATALOG:
            out = cards.card_html(item)
            self.assertNotIn("\n", out)                                  # markdown-safe
        msg = {"id": 1, "ts": 1_700_000_000, "user": "<b>x</b>", "text": "<script>alert(1)</script> :fire:",
               "kind": "msg", "badge": "spoiler"}
        out = cards.message_html(msg, "me")
        self.assertNotIn("<script>", out)
        self.assertIn("🔥", out)
        self.assertIn("vs-spoiler", out)

    def test_browse_groups_cover_catalog(self):
        grouped = [i for rows in data.GROUPS.values() for _, ids in rows for i in ids]
        self.assertEqual(sorted(grouped), sorted(data.BY_ID))                # every item in exactly one row
        for cat, rows in data.GROUPS.items():
            self.assertIn(cat, data.CATEGORIES)
            for _, ids in rows:
                self.assertTrue(all(data.BY_ID[i]["kind"] == cat for i in ids), cat)
        self.assertIn("vs-rail", cards.rail_html(data.CATALOG[:3]))
        self.assertNotIn("\n", cards.wide_card_html(data.BY_ID["bbt10"]))

    def test_filters(self):
        self.assertTrue(all(i["telugu"] for i in data.filter_items(telugu_only=True)))
        self.assertEqual([i["id"] for i in data.filter_items("anime", query="nobita's dinosaur")],
                         ["doraemon-dinosaur"])
        self.assertTrue(data.filter_items(platforms=["JioHotstar"]))       # '*' suffix ignored

    def test_expand(self):
        self.assertEqual(expand(":goat: :unknown:"), "🐐 :unknown:")


if __name__ == "__main__":
    unittest.main()
