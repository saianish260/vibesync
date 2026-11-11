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


class CatalogTests(unittest.TestCase):
    def test_catalog_integrity(self):
        ids = [i["id"] for i in data.CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        for item in data.CATALOG:
            self.assertIn(item["kind"], data.KIND_LABELS)
            for prov, url in item["offers"]:
                self.assertIn(prov, data.PROVIDERS, item["id"])
                self.assertTrue(url.startswith("https://"), url)
            if item["poster"]:
                self.assertIsInstance(item["poster"]["id"], int)
        for mood in data.MOODS:
            self.assertGreaterEqual(len(data.items_for_mood(mood)), 4, mood)

    def test_rows_cover_catalog_once(self):
        grouped = [i for rows in data.ROWS.values() for _, ids in rows for i in ids]
        self.assertEqual(sorted(grouped), sorted(data.BY_ID))
        for kind, rows in data.ROWS.items():
            for _, ids in rows:
                self.assertTrue(all(data.BY_ID[i]["kind"] == kind for i in ids), kind)
        self.assertTrue(all(i in data.BY_ID for i in data.FEATURED))

    def test_verified_facts(self):
        """Spot-checks from the JustWatch India research (Nov 2026)."""
        offers = lambda i: {p for p, _ in data.BY_ID[i]["offers"]}
        self.assertEqual(offers("spiderverse"), {"sonyliv"})
        self.assertEqual(offers("kalki"), {"prime", "netflix"})
        self.assertEqual(offers("hanuman"), {"zee5", "hotstar"})
        self.assertEqual(offers("doraemon-sky-utopia"), set())
        self.assertIn("netflix.com/title/82006666", dict(data.BY_ID["pushpa2"]["offers"])["netflix"])
        self.assertEqual(dict(data.BY_ID["magadheera"]["offers"]), {"aha": "https://www.aha.video/movie/magadheera"})
        self.assertEqual(data.PROVIDERS["aha"]["pkg"], "ahaflix.tv")
        self.assertGreaterEqual(len(data.CATALOG), 80)

    def test_payload_is_json(self):
        import json
        payload = data.catalog_payload()
        text = json.dumps(payload)
        self.assertEqual(len(payload["items"]), len(data.CATALOG))
        self.assertTrue(all(i["trailer"].startswith("https://www.youtube.com/") for i in payload["items"]))
        self.assertLess(len(text), 90000)


class LoungeHtmlTests(unittest.TestCase):
    def test_messages_escaped(self):
        msg = {"id": 1, "ts": 1_700_000_000, "user": "<b>x</b>", "text": "<script>alert(1)</script> :fire:",
               "kind": "msg", "badge": "spoiler"}
        out = cards.message_html(msg, "me")
        self.assertNotIn("<script>", out)
        self.assertIn("🔥", out)
        self.assertIn("vs-spoiler", out)
        self.assertNotIn("\n", cards.chat_html([msg], "me"))

    def test_styles_format_for_every_theme(self):
        import sys
        import types
        sys.modules.setdefault("streamlit", types.SimpleNamespace(markdown=lambda *a, **k: None))  # not needed to format CSS
        from core import styles
        for name, pal in styles.THEMES.items():
            css = styles.CSS % pal
            self.assertIn(pal["accent"], css, name)
            self.assertNotIn("%(", css)

    def test_expand(self):
        self.assertEqual(expand(":goat: :unknown:"), "🐐 :unknown:")


if __name__ == "__main__":
    unittest.main()


class WatchLinkTests(unittest.TestCase):
    def test_parse_watch_page(self):
        from core.watchlinks import parse_watch_page, is_watch_url
        page = (
            '<ul class="providers"><li><a href="https://click.justwatch.com/a?cx=abc&amp;r=https%3A%2F%2Fwww.netflix.com%2Ftitle%2F81234567&amp;uct_country=in" '
            'title="Watch Some Film on Netflix"><img src="/n.jpg" alt="Netflix"></a></li>'
            '<li><a href="https://click.justwatch.com/a?r=https%3A%2F%2Fwww.hotstar.com%2Fin%2Fmovies%2Fsome-film%2F1271234567&amp;uct_country=in">'
            '<img alt="JioHotstar" src="/h.jpg"></a></li>'
            '<li><a href="https://click.justwatch.com/a?r=https%3A%2F%2Fwww.netflix.com%2Fbrowse" title="Rent Some Film on Netflix"></a></li>'
            '<a href="https://www.themoviedb.org/movie/1" title="Not a provider">x</a>'
            '<a href="https://click.justwatch.com/a?r=javascript%3Aalert(1)" title="Watch on Evil"></a></ul>')
        links = parse_watch_page(page)
        self.assertEqual(links["netflix"], "https://www.netflix.com/title/81234567")       # first listing wins
        self.assertEqual(links["jiohotstar"], "https://www.hotstar.com/in/movies/some-film/1271234567")
        self.assertNotIn("evil", links)                                                    # only http(s) destinations
        self.assertTrue(is_watch_url("https://www.themoviedb.org/movie/1100099-some-film/watch?locale=IN"))
        self.assertTrue(is_watch_url("https://www.themoviedb.org/tv/1399/watch?locale=IN"))
        for bad in ["https://evil.example/movie/1/watch", "https://www.themoviedb.org.evil.com/movie/1/watch",
                    "http://www.themoviedb.org/movie/1/watch", "https://www.themoviedb.org/movie/1/watch?locale=IN&x=1"]:
            self.assertFalse(is_watch_url(bad), bad)

    def test_custom_palette_validation(self):
        from core import styles
        ok = {"bg": "#0a0b10", "s1": "#11131a", "s2": "#191c26", "text": "#f2f4fa", "muted": "#a9b0c2",
              "accent": "#f0b44c", "on_accent": "#1a1205", "hot": "#ff4d5e"}
        pal = styles.custom_palette(ok)
        self.assertEqual(pal["accent"], "#f0b44c")
        self.assertIn("rgba(242,244,250", pal["line"])
        self.assertIn("#0a0b10", styles.CSS % styles.palette("cinema", pal))
        self.assertIsNone(styles.custom_palette(dict(ok, bg="red;}</style><script>")))
        self.assertIsNone(styles.custom_palette({"bg": "#000000"}))
        self.assertIsNone(styles.custom_palette(None))



class LangsTest(unittest.TestCase):
    def test_pick_and_summarize(self):
        from core import langs
        edges = [{"node": {"content": {"title": "Baahubali: The Beginning", "originalReleaseYear": 2015, "originalReleaseDate": "2015-07-10",
                                       "externalIds": {"tmdbId": "256040"}},
                           "offers": [{"monetizationType": "FLATRATE", "audioLanguages": ["te", "hi"], "subtitleLanguages": ["en"],
                                       "package": {"clearName": "JioHotstar", "technicalName": "jiohotstar"}},
                                      {"monetizationType": "FLATRATE", "audioLanguages": ["ta", "te"], "subtitleLanguages": [],
                                       "package": {"clearName": "JioHotstar", "technicalName": "jiohotstar"}},
                                      {"monetizationType": "RENT", "audioLanguages": [], "subtitleLanguages": [],
                                       "package": {"clearName": "Apple TV", "technicalName": "itunes"}}]}},
                 {"node": {"content": {"title": "Baahubali 2", "originalReleaseYear": 2017, "externalIds": {"tmdbId": "350312"}}, "offers": []}}]
        node = langs.pick(edges, "Bāhubali: The Beginning", 2015, None)
        self.assertEqual(node["content"]["externalIds"]["tmdbId"], "256040")
        self.assertEqual(langs.pick(edges, "x", None, 350312)["content"]["title"], "Baahubali 2")
        s = langs.summarize(node)
        hot = [a for a in s["apps"] if a["name"] == "JioHotstar"][0]
        self.assertEqual(hot["audio"], ["te", "hi", "ta"])
        self.assertEqual(s["date"], "2015-07-10")
        self.assertFalse(langs.summarize(None)["found"])
        self.assertEqual(langs.build_request("Vikram", "movie")["variables"]["searchTitlesFilter"]["objectTypes"], ["MOVIE"])


class NewsTest(unittest.TestCase):
    def test_parse_rss(self):
        from core.news import parse
        xml = ('<rss><channel><item><title>Ranabaali to stream on Netflix from November 13 - NewsBytes</title>'
               '<link>https://n/1</link><pubDate>Tue, 10 Nov 2026 10:00:00 GMT</pubDate><source url="x">NewsBytes</source></item>'
               '<item><title>A &amp; B</title></item></channel></rss>')
        items = parse(xml)
        self.assertEqual(items[0]["s"], "NewsBytes")
        self.assertIn("November 13", items[0]["t"])
        self.assertEqual(items[1]["t"], "A & B")
