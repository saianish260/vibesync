"""VibeSync catalog: verified against JustWatch India on 2026-11-09.

Each item:
  id, title, kind (movie | series | anime | reality | sports), year, meta (short line)
  genres, synopsis (our own words), moods (mood-picker tags), telugu (Telugu-language title)
  imdb (rating at time of check), poster (JustWatch poster id + slug, or None)
  offers: list of (provider key, exact URL that opens this title)   -> PROVIDERS below
  note: optional honesty note, e.g. not streaming in India right now
  status: optional "live" / "wrapped", trailer_query: optional YouTube search text

Streaming availability changes. Re-check on justwatch.com/in and edit the offers.
"""
from __future__ import annotations

UPDATED = "9 Nov 2026"

# Provider key -> display name, brand colour, Android package (for "open in app / Play Store")
PROVIDERS = {
    "netflix":     {"name": "Netflix",     "color": "#E50914", "pkg": "com.netflix.mediaclient"},
    "prime":       {"name": "Prime Video", "color": "#1A98FF", "pkg": "com.amazon.avod.thirdpartyclient"},
    "hotstar":     {"name": "JioHotstar",  "color": "#7B61FF", "pkg": "in.startv.hotstar"},
    "crunchyroll": {"name": "Crunchyroll", "color": "#F47521", "pkg": "com.crunchyroll.crunchyroid"},
    "sonyliv":     {"name": "Sony LIV",    "color": "#D4A017", "pkg": "com.sonyliv"},
    "zee5":        {"name": "ZEE5",        "color": "#8230C6", "pkg": "com.graymatrix.did"},
    "fancode":     {"name": "FanCode",     "color": "#F8A01B", "pkg": "com.dream11sportsguru"},
    "youtube":     {"name": "YouTube",     "color": "#FF0033", "pkg": "com.google.android.youtube"},
}

KIND_LABELS = {"anime": "Anime", "movie": "Movies", "series": "Series", "reality": "Reality TV", "sports": "Sports"}


def _p(pid: int, slug: str) -> dict:
    return {"id": pid, "slug": slug}


CATALOG: list[dict] = [
    # ───────────── Anime ─────────────
    dict(id="jjk", title="Jujutsu Kaisen", kind="anime", year=2020, meta="4 seasons",
         genres=["Action", "Supernatural", "Shonen"], imdb=8.5, poster=_p(307266835, "jujutsu-kaisen"),
         synopsis="A high-schooler swallows a cursed finger and is pulled into a hidden war between sorcerers and curses. The fights play like boss battles.",
         moods=["hype", "action"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00173871PLPL"),
                 ("netflix", "https://www.netflix.com/title/81278456"),
                 ("prime", "https://www.primevideo.com/detail?gti=amzn1.dv.gti.8eaa8725-6a7a-4099-9a33-b505f7fca0d6"),
                 ("sonyliv", "https://www.sonyliv.com/shows/jujutsu-kaisen-1790007268/ryomen-sukuna-1090509378"),
                 ("hotstar", "https://www.hotstar.com/in/1271461642")]),
    dict(id="demon-slayer", title="Demon Slayer", kind="anime", year=2019, meta="5 seasons",
         genres=["Action", "Historical", "Shonen"], imdb=8.5, poster=_p(255390803, "demon-slayer-kimetsu-no-yaiba"),
         synopsis="Tanjiro becomes a demon hunter to turn his sister human again. Each sword fight looks like a moving painting.",
         moods=["hype", "action"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00336262PLPL"),
                 ("netflix", "https://www.netflix.com/title/81091393"),
                 ("hotstar", "https://www.hotstar.com/in/1971041196")]),
    dict(id="solo-leveling", title="Solo Leveling", kind="anime", year=2024, meta="2 seasons",
         genres=["Action", "Fantasy", "Gaming"], imdb=8.5, poster=_p(310154566, "solo-leveling-2024"),
         synopsis="The weakest hunter alive gets a mysterious system that lets only him level up. Pure power-fantasy fuel.",
         moods=["hype", "action"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00320669PLPL")]),
    dict(id="frieren", title="Frieren: Beyond Journey's End", kind="anime", year=2023, meta="2 seasons",
         genres=["Fantasy", "Drama", "Adventure"], imdb=8.9, poster=_p(308526633, "frieren-beyond-journeys-end"),
         synopsis="An elf mage outlives the hero party she travelled with and slowly learns what those ten years meant. Quiet and beautiful.",
         moods=["chill", "mind", "comfort"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00324920ARSA"),
                 ("netflix", "https://www.netflix.com/title/81726714")]),
    dict(id="one-piece", title="One Piece", kind="anime", year=1999, meta="1000+ episodes",
         genres=["Adventure", "Comedy", "Shonen"], imdb=9.0, poster=_p(248497985, "one-piece"),
         synopsis="Luffy and the Straw Hat crew sail for the greatest treasure in the world. Endless arcs, loyal friends, huge payoffs.",
         moods=["fun", "hype", "comfort"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00380778JAJP"),
                 ("sonyliv", "https://www.sonyliv.com/shows/one-piece-1790007664/the-new-beginning-the-straw-hats-reunite-1090525937")]),
    dict(id="spy-family", title="Spy x Family", kind="anime", year=2022, meta="3 seasons",
         genres=["Comedy", "Action", "Family"], imdb=8.2, poster=_p(350199189, "spy-x-family"),
         synopsis="A spy, an assassin and a mind-reading kid fake being a family, and none of them knows the others' secrets.",
         moods=["fun", "comfort", "chill"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00166410PLPL"),
                 ("netflix", "https://www.netflix.com/title/81511410"),
                 ("sonyliv", "https://www.sonyliv.com/shows/spy-x-family-1790007376/operation-strix-1090522629"),
                 ("hotstar", "https://www.hotstar.com/in/1971076957")]),
    dict(id="haikyu", title="Haikyu!!", kind="anime", year=2014, meta="4 seasons",
         genres=["Sports", "Comedy", "Drama"], imdb=8.7, poster=_p(306807849, "haikyu"),
         synopsis="A short kid with a huge jump joins a fallen volleyball team. You'll want to run through a wall after every episode.",
         moods=["hype", "fun", "social"],
         offers=[("crunchyroll", "https://www.crunchyroll.com/watch/GE00111979THTH"),
                 ("netflix", "https://www.netflix.com/title/80090673"),
                 ("sonyliv", "https://www.sonyliv.com/shows/haikyu-1790007041/the-end-and-the-beginning-1090513697"),
                 ("hotstar", "https://www.hotstar.com/in/1271498279")]),
    dict(id="aot", title="Attack on Titan", kind="anime", year=2013, meta="4 seasons",
         genres=["Action", "Dark Fantasy", "Mystery"], imdb=9.1, poster=_p(306747132, "attack-on-titan"),
         synopsis="Humanity hides behind giant walls from man-eating Titans, until the truth about the walls changes everything.",
         moods=["mind", "action"],
         offers=[("prime", "https://app.primevideo.com/detail?gti=amzn1.dv.gti.57cdfd42-0c7f-4c3f-b35a-f776cae96d9d")],
         note="On Prime Video through the Anime Times channel add-on."),

    # ── Doraemon ──
    dict(id="sbm-doraemon", title="Stand By Me Doraemon", kind="anime", year=2014, meta="1h 34m · movie",
         genres=["Animation", "Family", "Comfort"], imdb=7.4, poster=_p(293474753, "stand-by-me-doraemon"),
         synopsis="The CGI retelling of how Doraemon arrived from the future and how Nobita grows up. Keep tissues nearby.",
         moods=["nostalgia", "comfort", "chill"],
         offers=[("netflix", "https://www.netflix.com/title/80158156")],
         note="Audio languages vary; check the audio menu in Netflix for a dub."),
    dict(id="sbm-doraemon-2", title="Stand By Me Doraemon 2", kind="anime", year=2020, meta="1h 36m · movie",
         genres=["Animation", "Family", "Comfort"], imdb=7.5, poster=_p(293464661, "stand-by-me-doraemon-2"),
         synopsis="Nobita travels back to see his grandmother, then has to show up for his own wedding.",
         moods=["nostalgia", "comfort"],
         offers=[("netflix", "https://www.netflix.com/title/81451264")],
         note="Audio languages vary; check the audio menu in Netflix for a dub."),
    dict(id="doraemon-new-dinosaur", title="Doraemon: Nobita's New Dinosaur", kind="anime", year=2020, meta="1h 51m · movie",
         genres=["Animation", "Adventure", "Family"], imdb=7.1, poster=_p(308757535, "doraemon-nobitas-new-dinosaur"),
         synopsis="Nobita hatches twin dinosaurs and has to find them a home in their own era.",
         moods=["nostalgia", "fun"], offers=[],
         note="Not streaming in India right now. The trailer button still works."),
    dict(id="doraemon-sky-utopia", title="Doraemon: Nobita's Sky Utopia", kind="anime", year=2023, meta="1h 47m · movie",
         genres=["Animation", "Fantasy", "Family"], imdb=6.7, poster=_p(309265530, "eiga-doraemon-nobita-to-sora-no-utopia"),
         synopsis="The gang flies to a 'perfect' floating city in the sky that turns out to be anything but.",
         moods=["nostalgia", "chill"], offers=[],
         note="Not streaming in India right now. The trailer button still works."),
    dict(id="doraemon-earth-symphony", title="Doraemon: Nobita's Earth Symphony", kind="anime", year=2024, meta="1h 55m · movie",
         genres=["Animation", "Music", "Family"], imdb=6.6, poster=_p(321402779, "eiga-doraemon-nobita-no-chikyu-symphony"),
         synopsis="A music-loving adventure where the gang has to save a world that runs on melody.",
         moods=["nostalgia", "comfort"], offers=[],
         note="Not streaming in India right now. The trailer button still works."),

    # ───────────── Reality TV ─────────────
    dict(id="bbt10", title="Bigg Boss Telugu 10", kind="reality", year=2026, meta="Star Maa · Host: Nagarjuna",
         genres=["Reality", "Drama", "Telugu"], imdb=None, poster=_p(320958387, "bigg-boss-telugu"),
         synopsis="Nagarjuna is back for Season 10: nominations, captaincy tasks, weekend verdicts and the full house chaos.",
         moods=["drama", "social", "fun"], telugu=True, status="live",
         offers=[("hotstar", "https://www.hotstar.com/in/shows/bigg-boss/14714")],
         trailer_query="Bigg Boss Telugu 10 latest promo"),
    dict(id="bbjodi2", title="BB Jodi Season 2", kind="reality", year=2026, meta="Star Maa · Host: Pradeep Machiraju",
         genres=["Reality", "Dance", "Telugu"], imdb=None, poster=None,
         synopsis="Bigg Boss alumni pair up for a dance battle judged by Sridevi, Sadha and Sekhar. Maanas and Shrasti Verma took the title.",
         moods=["social", "fun", "nostalgia"], telugu=True, status="wrapped",
         offers=[("hotstar", "https://www.hotstar.com/in")],
         note="Season finished. Search 'BB Jodi' inside JioHotstar for full episodes.",
         emoji="💃", colors=["#BE185D", "#6D28D9"], trailer_query="BB Jodi Season 2 best performances"),

    # ───────────── Movies ─────────────
    dict(id="pushpa2", title="Pushpa 2: The Rule", kind="movie", year=2024, meta="3h 21m",
         genres=["Action", "Crime", "Drama"], imdb=None, poster=_p(322095005, "pushpa-the-rule-part-2"),
         synopsis="Pushpa Raj's red-sandalwood empire keeps growing, and so does the swagger. Peak whistle-in-the-theatre energy.",
         moods=["hype", "action", "social"], telugu=True,
         offers=[("netflix", "https://www.netflix.com/title/82006666")]),
    dict(id="kalki", title="Kalki 2898 AD", kind="movie", year=2024, meta="3h 0m",
         genres=["Sci-Fi", "Mythology", "Action"], imdb=7.1, poster=_p(318017051, "kalki-2898-ad"),
         synopsis="A dystopian future collides with Mahabharata myth. Huge world-building and a wild final act.",
         moods=["hype", "mind", "action"], telugu=True,
         offers=[("prime", "https://www.primevideo.com/detail?gti=amzn1.dv.gti.5e6a95ea-424a-49e0-b1db-3a6097ec03f9"),
                 ("netflix", "https://www.netflix.com/title/81726031")]),
    dict(id="devara", title="Devara: Part 1", kind="movie", year=2024, meta="2h 56m",
         genres=["Action", "Drama", "Thriller"], imdb=6.0, poster=_p(311782013, "ntr-30"),
         synopsis="A coastal strongman rules the sea through fear. Years later, his gentle son inherits the legend.",
         moods=["action", "hype"], telugu=True,
         offers=[("netflix", "https://www.netflix.com/title/81728598")]),
    dict(id="lucky-baskhar", title="Lucky Baskhar", kind="movie", year=2024, meta="2h 28m",
         genres=["Crime", "Thriller", "Drama"], imdb=8.0, poster=_p(316797635, "lucky-baskhar"),
         synopsis="A broke bank cashier in 1990s Bombay finds a loophole in the system. A slick money thriller.",
         moods=["mind", "chill"], telugu=True,
         offers=[("netflix", "https://www.netflix.com/title/81902035")]),
    dict(id="hanuman", title="HanuMan", kind="movie", year=2024, meta="2h 39m",
         genres=["Superhero", "Fantasy", "Action"], imdb=7.7, poster=_p(302388715, "hanu-man"),
         synopsis="A small-town thief gains superpowers from a sacred gem. A homegrown superhero film with heart.",
         moods=["fun", "hype", "action"], telugu=True,
         offers=[("zee5", "https://www.zee5.com/movies/details/watch-hanuman-2024-full-hanu-man-movie-online-on-zee5/0-0-1z5531939"),
                 ("hotstar", "https://www.hotstar.com/in/1971007527")]),
    dict(id="interstellar", title="Interstellar", kind="movie", year=2014, meta="2h 49m",
         genres=["Sci-Fi", "Drama", "Space"], imdb=8.7, poster=_p(449990, "interstellar"),
         synopsis="A pilot leaves his children to find humanity a new home through a wormhole, where time itself hurts.",
         moods=["mind", "chill"],
         offers=[("netflix", "https://www.netflix.com/title/70305903"),
                 ("prime", "https://www.primevideo.com/detail?gti=amzn1.dv.gti.002e9637-838c-46be-ab16-e3afdcb578fe"),
                 ("hotstar", "https://www.hotstar.com/in/movies/interstellar/1971000531")]),
    dict(id="spiderverse", title="Spider-Man: Across the Spider-Verse", kind="movie", year=2023, meta="Animated feature",
         genres=["Animation", "Superhero", "Action"], imdb=8.5, poster=_p(305309017, "spider-man-into-the-spider-verse-2"),
         synopsis="Miles crashes into a multiverse of Spider-People who have very different ideas about destiny.",
         moods=["hype", "fun", "action"],
         offers=[("sonyliv", "https://www.sonyliv.com/movies/spider-man-across-the-spider-verse-1000292994")]),

    # ───────────── Series ─────────────
    dict(id="panchayat", title="Panchayat", kind="series", year=2020, meta="4 seasons",
         genres=["Comedy", "Drama", "Village life"], imdb=9.0, poster=_p(316699631, "panchayat"),
         synopsis="An engineering graduate takes a job as secretary of a tiny village office. The warmest show in India.",
         moods=["chill", "comfort", "fun"],
         offers=[("prime", "https://www.primevideo.com/detail?gti=amzn1.dv.gti.ceb88881-6a77-d28d-bd17-31c18d185b72")]),
    dict(id="family-man", title="The Family Man", kind="series", year=2019, meta="3 seasons",
         genres=["Spy", "Action", "Comedy"], imdb=8.6, poster=_p(146823074, "the-family-man"),
         synopsis="A middle-class dad is secretly a top intelligence officer, juggling terror plots and parent-teacher meetings.",
         moods=["action", "fun"],
         offers=[("prime", "https://www.primevideo.com/detail?gti=amzn1.dv.gti.2cb6867e-4128-f2d8-aa87-a8d47de77735")]),
    dict(id="kota-factory", title="Kota Factory", kind="series", year=2019, meta="3 seasons",
         genres=["Drama", "Student life", "Comedy"], imdb=9.0, poster=_p(302477389, "kota-factory"),
         synopsis="IIT aspirants survive coaching-centre pressure with Jeetu Bhaiya's advice. A little too relatable.",
         moods=["comfort", "chill", "mind"],
         offers=[("netflix", "https://www.netflix.com/title/81249783")]),
    dict(id="arcane", title="Arcane", kind="series", year=2021, meta="2 seasons",
         genres=["Animation", "Steampunk", "Drama"], imdb=9.0, poster=_p(255388636, "arcane"),
         synopsis="Two sisters end up on opposite sides of a war between a gleaming city and its underground. Every frame is art.",
         moods=["mind", "action", "hype"],
         offers=[("netflix", "https://www.netflix.com/title/81435684")]),
    dict(id="stranger-things", title="Stranger Things", kind="series", year=2016, meta="5 seasons",
         genres=["Sci-Fi", "Horror", "Mystery"], imdb=8.6, poster=_p(301444843, "stranger-things"),
         synopsis="Kids on bikes against monsters from the Upside Down. Synth music, loyal friends and a lot of waffles.",
         moods=["fun", "nostalgia", "social"],
         offers=[("netflix", "https://www.netflix.com/title/80057281")]),
    dict(id="squid-game", title="Squid Game", kind="series", year=2021, meta="3 seasons",
         genres=["Thriller", "Survival", "Drama"], imdb=7.9, poster=_p(305500204, "squid-game"),
         synopsis="Desperate players compete in deadly versions of children's games for a giant cash prize.",
         moods=["drama", "social", "mind"],
         offers=[("netflix", "https://www.netflix.com/title/81040344")]),
    dict(id="breaking-bad", title="Breaking Bad", kind="series", year=2008, meta="5 seasons",
         genres=["Crime", "Drama", "Thriller"], imdb=9.5, poster=_p(300604431, "breaking-bad"),
         synopsis="A chemistry teacher slowly becomes a drug kingpin. Every season is tighter than the last.",
         moods=["mind", "drama"],
         offers=[("netflix", "https://www.netflix.com/title/70143836")]),

    # ───────────── Sports (no posters: live events) ─────────────
    dict(id="ipl", title="IPL", kind="sports", year=2026, meta="Cricket · T20",
         genres=["Cricket", "T20"], imdb=None, poster=None, emoji="🏏", colors=["#1D4ED8", "#F59E0B"],
         synopsis="Live matches stream on JioHotstar during the season. Off-season, catch last-over finishes and best catches in highlights.",
         moods=["hype", "social", "action"],
         offers=[("hotstar", "https://www.hotstar.com/in")], trailer_query="IPL highlights"),
    dict(id="team-india", title="Team India", kind="sports", year=2026, meta="Cricket · Internationals",
         genres=["Cricket", "India"], imdb=None, poster=None, emoji="🇮🇳", colors=["#1E40AF", "#F97316"],
         synopsis="Home internationals and ICC events stream on JioHotstar. Highlights of the latest match are one tap away.",
         moods=["hype", "social"],
         offers=[("hotstar", "https://www.hotstar.com/in")], trailer_query="India cricket match highlights latest"),
    dict(id="pkl", title="Pro Kabaddi League", kind="sports", year=2026, meta="Kabaddi",
         genres=["Kabaddi", "Indian sports"], imdb=None, poster=None, emoji="🤼", colors=["#9F1239", "#FACC15"],
         synopsis="Super raids, ankle holds and last-second Do-or-Die drama. Streams on JioHotstar.",
         moods=["hype", "action"],
         offers=[("hotstar", "https://www.hotstar.com/in")], trailer_query="Pro Kabaddi highlights latest"),
    dict(id="epl", title="Premier League", kind="sports", year=2026, meta="Football",
         genres=["Football", "EPL"], imdb=None, poster=None, emoji="⚽", colors=["#3B0764", "#22C55E"],
         synopsis="Matchweek goals, late winners and VAR chaos from England's top flight, streaming on JioHotstar.",
         moods=["hype", "social"],
         offers=[("hotstar", "https://www.hotstar.com/in")], trailer_query="Premier League highlights this week"),
    dict(id="f1", title="Formula 1", kind="sports", year=2026, meta="Motorsport",
         genres=["F1", "Racing"], imdb=None, poster=None, emoji="🏎️", colors=["#991B1B", "#111827"],
         synopsis="Every Grand Prix streams on FanCode in India (deal runs to 2028). Overtakes, strategy gambles and team-radio meltdowns.",
         moods=["hype", "mind"],
         offers=[("fancode", "https://www.fancode.com")], trailer_query="F1 race highlights latest"),
]

for _item in CATALOG:
    _item.setdefault("telugu", False)
    _item.setdefault("status", None)
    _item.setdefault("note", "")
    _item.setdefault("emoji", "🎬")
    _item.setdefault("colors", ["#3F2A3A", "#1B1220"])

BY_ID = {item["id"]: item for item in CATALOG}

# Discover rows: category -> ordered (row title, ids)
ROWS: dict[str, list[tuple[str, list[str]]]] = {
    "anime": [("Top anime series", ["jjk", "demon-slayer", "solo-leveling", "frieren", "one-piece", "spy-family",
                                    "haikyu", "aot"]),
              ("Doraemon movie night", ["sbm-doraemon", "sbm-doraemon-2", "doraemon-new-dinosaur",
                                        "doraemon-sky-utopia", "doraemon-earth-symphony"])],
    "movie": [("Telugu blockbusters", ["pushpa2", "kalki", "devara", "lucky-baskhar", "hanuman"]),
              ("Worth the rewatch", ["interstellar", "spiderverse"])],
    "series": [("Made in India", ["panchayat", "family-man", "kota-factory"]),
               ("Global binges", ["arcane", "stranger-things", "squid-game", "breaking-bad"])],
    "reality": [("Telugu reality", ["bbt10", "bbjodi2"])],
    "sports": [("Cricket", ["ipl", "team-india"]), ("More sports", ["pkl", "epl", "f1"])],
}

FEATURED = ["bbt10", "frieren", "pushpa2", "arcane", "panchayat"]

MOODS: dict[str, dict] = {
    "bored":     {"label": "Bored",       "emoji": "😐", "tags": ["hype", "fun"],
                  "line": "Boredom detected. Here's something loud."},
    "hyped":     {"label": "Hyped",       "emoji": "⚡", "tags": ["hype", "action"],
                  "line": "Big energy. These can keep up."},
    "chill":     {"label": "Chill",       "emoji": "😌", "tags": ["chill", "comfort"],
                  "line": "Low effort, high comfort."},
    "nostalgic": {"label": "Nostalgic",   "emoji": "🥹", "tags": ["nostalgia", "comfort"],
                  "line": "Back to the good old days."},
    "low":       {"label": "Low-key sad", "emoji": "😢", "tags": ["comfort", "fun"],
                  "line": "A soft landing. These always help."},
    "squad":     {"label": "Squad mode",  "emoji": "🎉", "tags": ["social", "drama"],
                  "line": "Group-watch picks. Open the Lounge and pull your friends in."},
    "brainy":    {"label": "Big-brain",   "emoji": "🧠", "tags": ["mind"],
                  "line": "Plot twists and slow burns."},
}

BOOSTS = [
    "Octopuses have three hearts. You only need one good episode.",
    "A group of flamingos is called a flamboyance. Be the flamboyance tonight.",
    "Sea otters hold hands while they sleep. Text your bestie.",
    "Honey never spoils, and neither does a Doraemon rewatch.",
    "Cows have best friends and get stressed apart. Respect the squad.",
]

TRACKER = {
    "bbt10": {
        "seed": [{"ts": "2026-10-29", "tag": "Buzz",
                  "text": "Rohit and Trigun reported to be pulling the most audience votes (Deccan Chronicle)."}],
        "links": [["Latest promos", "https://www.youtube.com/results?search_query=Bigg+Boss+Telugu+10+latest+promo"],
                  ["Elimination news", "https://www.google.com/search?q=Bigg+Boss+Telugu+10+elimination+this+week&tbm=nws"]],
    },
    "bbjodi2": {
        "seed": [{"ts": "2026-03-29", "tag": "Finale",
                  "text": "Maanas and Shrasti Verma won; Vishwa Raj and Neha Chowdary were runners-up."}],
        "links": [["Best performances", "https://www.youtube.com/results?search_query=BB+Jodi+Season+2+best+performances"]],
    },
}
TRACKER_TAGS = ["Highlight", "Nomination", "Elimination", "Captaincy", "Wild card", "Hot take", "Buzz", "Finale"]


def youtube_url(item: dict) -> str:
    from urllib.parse import quote_plus
    q = item.get("trailer_query") or (f"{item['title']} official trailer" if item["kind"] != "sports"
                                       else f"{item['title']} highlights")
    return "https://www.youtube.com/results?search_query=" + quote_plus(q)


def items_for_mood(mood: str) -> list[dict]:
    tags = set(MOODS[mood]["tags"])
    return [i for i in CATALOG if tags & set(i["moods"])]


def catalog_payload() -> dict:
    """Everything the Discover screen needs, as plain JSON."""
    items = []
    for it in CATALOG:
        items.append({
            "id": it["id"], "title": it["title"], "kind": it["kind"], "year": it["year"], "meta": it["meta"],
            "genres": it["genres"], "synopsis": it["synopsis"], "moods": it["moods"], "telugu": it["telugu"],
            "imdb": it["imdb"], "poster": it["poster"], "status": it["status"], "note": it["note"],
            "emoji": it["emoji"], "colors": it["colors"], "trailer": youtube_url(it),
            "offers": [{"p": p, "url": u} for p, u in it["offers"]],
        })
    return {"updated": UPDATED, "providers": PROVIDERS, "kinds": KIND_LABELS, "items": items,
            "rows": {k: [[t, ids] for t, ids in v] for k, v in ROWS.items()}, "featured": FEATURED,
            "moods": MOODS, "boosts": BOOSTS, "tracker": TRACKER, "trackerTags": TRACKER_TAGS}
