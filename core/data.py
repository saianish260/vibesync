"""Content catalog, moods and boost lines.

Every item is a plain dict so it's easy to edit or extend:
  id         unique slug
  title      display title
  kind       movie | series | anime | reality | sports
  year/meta  shown under the title (meta wins if present)
  genres     up to 3 shown as tags
  platforms  where to watch in India (availability changes, so double-check)
  synopsis   one or two lines
  emoji      shown on the generated poster
  colors     two hex colours for the generated poster gradient
  poster     OPTIONAL image URL; if set, it replaces the generated poster art
  moods      tags used by the mood picker (see MOODS below)
  telugu     True if Telugu audio is commonly available
  status     OPTIONAL "live" (pulsing badge) or any short label e.g. "wrapped"
  fav        True = part of the default "Surprise Me!" favourites pool
  trailer_query  OPTIONAL custom YouTube search text
"""
from __future__ import annotations

KIND_LABELS = {
    "all": "✨ All",
    "movie": "🎬 Movies",
    "series": "📺 Series",
    "anime": "🍥 Anime",
    "reality": "👁️ Reality TV",
    "sports": "🏏 Sports",
}

CATALOG: list[dict] = [
    # ───────────── Anime ─────────────
    dict(id="jjk", title="Jujutsu Kaisen", kind="anime", year=2020,
         genres=["Action", "Supernatural", "Shonen"], platforms=["Crunchyroll", "Netflix"],
         synopsis="A student swallows a cursed finger and gets pulled into a war of sorcerers. Fights animated like boss battles.",
         emoji="🩸", colors=["#3b0764", "#06b6d4"], moods=["hype", "action"], fav=True),
    dict(id="demon-slayer", title="Demon Slayer", kind="anime", year=2019,
         genres=["Action", "Historical", "Shonen"], platforms=["Crunchyroll", "Netflix"],
         synopsis="Tanjiro hunts demons to cure his sister. Breathing-style fights that look like paintings in motion.",
         emoji="🗡️", colors=["#7f1d1d", "#14b8a6"], moods=["hype", "action"], fav=True),
    dict(id="one-piece", title="One Piece", kind="anime", year=1999,
         genres=["Adventure", "Comedy", "Shonen"], platforms=["Crunchyroll", "Netflix"],
         synopsis="Luffy and the Straw Hats chase the ultimate treasure. Endless arcs, loyal crew, maximum hype moments.",
         emoji="🏴‍☠️", colors=["#b91c1c", "#f59e0b"], moods=["fun", "hype", "comfort"], fav=True),
    dict(id="frieren", title="Frieren: Beyond Journey's End", kind="anime", year=2023,
         genres=["Fantasy", "Drama", "Slice of Life"], platforms=["Crunchyroll"],
         synopsis="An elf mage outlives her hero party and learns what those years meant. Quiet, gorgeous, quietly devastating.",
         emoji="🌸", colors=["#1e3a8a", "#a5f3fc"], moods=["chill", "mind", "comfort"], fav=True),
    dict(id="solo-leveling", title="Solo Leveling", kind="anime", year=2024,
         genres=["Action", "Fantasy", "Gaming"], platforms=["Crunchyroll"],
         synopsis="The weakest hunter gets a mysterious system that lets him level up alone. Pure power-fantasy fuel.",
         emoji="⚔️", colors=["#1e1b4b", "#3b82f6"], moods=["hype", "action"], fav=True),
    dict(id="spy-family", title="Spy x Family", kind="anime", year=2022,
         genres=["Comedy", "Action", "Family"], platforms=["Crunchyroll", "Netflix"],
         synopsis="A spy, an assassin and a mind-reading kid fake a family. Anya alone is worth the watch.",
         emoji="🥜", colors=["#831843", "#10b981"], moods=["fun", "comfort", "chill"], fav=True),
    dict(id="haikyu", title="Haikyu!!", kind="anime", year=2014,
         genres=["Sports", "Comedy", "Drama"], platforms=["Crunchyroll", "Netflix"],
         synopsis="A short kid with a huge jump joins a fallen volleyball team. Will make you want to run through a wall.",
         emoji="🏐", colors=["#ea580c", "#1e293b"], moods=["hype", "fun", "social"]),
    dict(id="aot", title="Attack on Titan", kind="anime", year=2013,
         genres=["Action", "Dark Fantasy", "Mystery"], platforms=["Crunchyroll"],
         synopsis="Humanity hides behind walls from giants, until the truth behind the walls flips everything.",
         emoji="🧱", colors=["#3f2d20", "#64748b"], moods=["mind", "action"]),

    # ── Nostalgic comfort: Doraemon movies (Telugu audio) ──
    dict(id="sbm-doraemon", title="Stand By Me Doraemon", kind="anime", year=2014,
         genres=["Animation", "Family", "Comfort"], platforms=["JioHotstar*"],
         synopsis="The CGI retelling of how Doraemon arrived and how Nobita grows up. Bring tissues.",
         emoji="🔔", colors=["#0284c7", "#f8fafc"], moods=["nostalgia", "comfort", "chill"], telugu=True, fav=True,
         trailer_query="Stand By Me Doraemon Telugu"),
    dict(id="sbm-doraemon-2", title="Stand By Me Doraemon 2", kind="anime", year=2020,
         genres=["Animation", "Family", "Comfort"], platforms=["JioHotstar*"],
         synopsis="Nobita time-travels to see his grandma and has to show up for his own wedding.",
         emoji="💍", colors=["#0369a1", "#fde68a"], moods=["nostalgia", "comfort"], telugu=True, fav=True,
         trailer_query="Stand By Me Doraemon 2 Telugu"),
    dict(id="doraemon-dinosaur", title="Doraemon: Nobita's Dinosaur", kind="anime", year=2006,
         genres=["Animation", "Adventure", "Comfort"], platforms=["JioHotstar*"],
         synopsis="Nobita hatches a dinosaur egg and races to return Piisuke to his own era. Childhood in a movie.",
         emoji="🦕", colors=["#15803d", "#38bdf8"], moods=["nostalgia", "comfort", "fun"], telugu=True, fav=True,
         trailer_query="Doraemon Nobita's Dinosaur Telugu"),
    dict(id="doraemon-steel-troops", title="Doraemon: Nobita and the Steel Troops", kind="anime", year=2011,
         genres=["Animation", "Sci-Fi", "Adventure"], platforms=["JioHotstar*"],
         synopsis="Nobita finds giant robot parts and suddenly the gang is defending Earth from a robot army.",
         emoji="🤖", colors=["#334155", "#0ea5e9"], moods=["nostalgia", "fun", "action"], telugu=True,
         trailer_query="Doraemon Nobita and the Steel Troops Telugu"),
    dict(id="doraemon-sky-utopia", title="Doraemon: Nobita's Sky Utopia", kind="anime", year=2023,
         genres=["Animation", "Fantasy", "Family"], platforms=["JioHotstar*"],
         synopsis="The gang flies to a 'perfect' floating city in the sky, which turns out to be not so perfect.",
         emoji="☁️", colors=["#7dd3fc", "#a78bfa"], moods=["nostalgia", "chill", "comfort"], telugu=True,
         trailer_query="Doraemon Nobita's Sky Utopia Telugu"),

    # ───────────── Reality TV ─────────────
    dict(id="bbt10", title="Bigg Boss Telugu 10", kind="reality", meta="Star Maa · 9:30 PM · Host: Nagarjuna",
         genres=["Reality", "Drama", "Telugu"], platforms=["Star Maa", "JioHotstar"],
         synopsis="Nagarjuna is back for Season 10. Nominations, captaincy tasks, weekend verdicts, the full chaos.",
         emoji="👁️", colors=["#4c1d95", "#f43f5e"], moods=["drama", "social", "fun"], telugu=True,
         status="live", fav=True, trailer_query="Bigg Boss Telugu 10 latest promo"),
    dict(id="bbjodi2", title="BB Jodi Season 2", kind="reality", meta="Star Maa · Season wrapped Mar 2026",
         genres=["Reality", "Dance", "Telugu"], platforms=["Star Maa", "JioHotstar"],
         synopsis="Bigg Boss alumni pair up for a dance battle. Re-live the best performances and the grand finale.",
         emoji="💃", colors=["#be185d", "#7c3aed"], moods=["social", "fun", "nostalgia"], telugu=True,
         status="wrapped", trailer_query="BB Jodi Season 2 best performances"),

    # ───────────── Movies ─────────────
    dict(id="pushpa2", title="Pushpa 2: The Rule", kind="movie", year=2024,
         genres=["Action", "Mass", "Telugu"], platforms=["Netflix"],
         synopsis="Pushpa Raj's sandalwood empire grows, and so does the swagger. Peak whistle-in-the-theatre energy.",
         emoji="🔥", colors=["#7c2d12", "#dc2626"], moods=["hype", "action", "social"], telugu=True, fav=True),
    dict(id="kalki", title="Kalki 2898 AD", kind="movie", year=2024,
         genres=["Sci-Fi", "Mythology", "Action"], platforms=["Prime Video"],
         synopsis="A dystopian future collides with Mahabharata myth. Big-screen world-building with a wild last act.",
         emoji="🛸", colors=["#78350f", "#0e7490"], moods=["hype", "mind", "action"], telugu=True, fav=True),
    dict(id="devara", title="Devara: Part 1", kind="movie", year=2024,
         genres=["Action", "Drama", "Telugu"], platforms=["Netflix"],
         synopsis="A coastal strongman rules the sea by fear. Then his son inherits the legend.",
         emoji="🌊", colors=["#0c4a6e", "#b91c1c"], moods=["action", "hype"], telugu=True),
    dict(id="lucky-baskhar", title="Lucky Baskhar", kind="movie", year=2024,
         genres=["Thriller", "Crime", "Drama"], platforms=["Netflix"],
         synopsis="A broke bank cashier finds a loophole in 1990s Bombay. A slick money thriller that keeps you guessing.",
         emoji="💸", colors=["#14532d", "#ca8a04"], moods=["mind", "chill"], telugu=True, fav=True),
    dict(id="hanuman", title="HanuMan", kind="movie", year=2024,
         genres=["Superhero", "Fantasy", "Telugu"], platforms=["ZEE5"],
         synopsis="A village nobody gets superpowers from a sacred gem. A homegrown superhero film with heart.",
         emoji="🐒", colors=["#9a3412", "#facc15"], moods=["fun", "hype", "action"], telugu=True),
    dict(id="interstellar", title="Interstellar", kind="movie", year=2014,
         genres=["Sci-Fi", "Drama", "Space"], platforms=["Prime Video"],
         synopsis="A pilot leaves his kids to search for a new home for humanity through a wormhole. Time hurts.",
         emoji="🪐", colors=["#0f172a", "#f97316"], moods=["mind", "chill"]),
    dict(id="spiderverse", title="Spider-Man: Across the Spider-Verse", kind="movie", year=2023,
         genres=["Animation", "Superhero", "Action"], platforms=["Netflix*"],
         synopsis="Miles crashes into a multiverse of Spider-People with very different ideas about destiny.",
         emoji="🕷️", colors=["#db2777", "#2563eb"], moods=["hype", "fun", "action"]),

    # ───────────── Series ─────────────
    dict(id="stranger-things", title="Stranger Things", kind="series", year=2016,
         genres=["Sci-Fi", "Horror", "80s"], platforms=["Netflix"],
         synopsis="Kids on bikes vs. monsters from the Upside Down. Synth music, friendship and a lot of waffles.",
         emoji="🚲", colors=["#7f1d1d", "#1e1b4b"], moods=["fun", "nostalgia", "social"], fav=True),
    dict(id="family-man", title="The Family Man", kind="series", year=2019,
         genres=["Spy", "Action", "Comedy"], platforms=["Prime Video"],
         synopsis="A middle-class dad is secretly a top intelligence officer. Juggling terror plots and PTA meetings.",
         emoji="🕶️", colors=["#1f2937", "#16a34a"], moods=["action", "fun"], fav=True),
    dict(id="panchayat", title="Panchayat", kind="series", year=2020,
         genres=["Comedy", "Slice of Life", "Drama"], platforms=["Prime Video"],
         synopsis="An engineering grad ends up as secretary of a tiny village office. The most wholesome show in India.",
         emoji="🏡", colors=["#365314", "#fbbf24"], moods=["chill", "comfort", "fun"], fav=True),
    dict(id="arcane", title="Arcane", kind="series", year=2021,
         genres=["Animation", "Steampunk", "Drama"], platforms=["Netflix"],
         synopsis="Two sisters end up on opposite sides of a city war. Every frame looks like concept art.",
         emoji="⚙️", colors=["#4c1d95", "#06b6d4"], moods=["mind", "action", "hype"], fav=True),
    dict(id="squid-game", title="Squid Game", kind="series", year=2021,
         genres=["Thriller", "Survival", "Drama"], platforms=["Netflix"],
         synopsis="Broke players compete in deadly kids' games for a giant cash prize. Peak group-watch tension.",
         emoji="🦑", colors=["#be123c", "#0f766e"], moods=["drama", "social", "mind"]),
    dict(id="kota-factory", title="Kota Factory", kind="series", year=2019,
         genres=["Drama", "Student Life", "Comedy"], platforms=["Netflix"],
         synopsis="IIT aspirants survive coaching-centre pressure with Jeetu Bhaiya's advice. Way too relatable.",
         emoji="📚", colors=["#334155", "#e2e8f0"], moods=["comfort", "chill", "mind"]),
    dict(id="breaking-bad", title="Breaking Bad", kind="series", year=2008,
         genres=["Crime", "Drama", "Thriller"], platforms=["Netflix"],
         synopsis="A chemistry teacher slowly turns into a kingpin. Each season gets tighter than the one before.",
         emoji="⚗️", colors=["#14532d", "#eab308"], moods=["mind", "drama"]),

    # ───────────── Sports ─────────────
    dict(id="ipl", title="IPL Highlights", kind="sports", meta="Cricket · T20",
         genres=["Cricket", "T20", "Highlights"], platforms=["JioHotstar", "Star Sports"],
         synopsis="Last-over finishes, sixes into the stands and the best catches. Your daily cricket fix.",
         emoji="🏏", colors=["#1d4ed8", "#f59e0b"], moods=["hype", "social", "action"], fav=True,
         trailer_query="IPL highlights"),
    dict(id="team-india", title="Team India Match Highlights", kind="sports", meta="Cricket · International",
         genres=["Cricket", "India", "Highlights"], platforms=["JioHotstar", "Star Sports"],
         synopsis="Latest highlights from the Men in Blue: centuries, collapses and comebacks.",
         emoji="🇮🇳", colors=["#1e40af", "#f97316"], moods=["hype", "social"],
         trailer_query="India cricket match highlights latest"),
    dict(id="pkl", title="Pro Kabaddi League", kind="sports", meta="Kabaddi",
         genres=["Kabaddi", "Indian Sports", "Highlights"], platforms=["JioHotstar", "Star Sports"],
         synopsis="Super raids, tackles and last-second Do-or-Die drama. Underrated hype.",
         emoji="🤼", colors=["#9f1239", "#facc15"], moods=["hype", "action"],
         trailer_query="Pro Kabaddi highlights latest"),
    dict(id="epl", title="Premier League Highlights", kind="sports", meta="Football",
         genres=["Football", "EPL", "Highlights"], platforms=["JioHotstar"],
         synopsis="Matchweek goals, late winners and VAR chaos from England's top flight.",
         emoji="⚽", colors=["#3b0764", "#22c55e"], moods=["hype", "social"],
         trailer_query="Premier League highlights this week"),
    dict(id="f1", title="Formula 1 Race Highlights", kind="sports", meta="Motorsport",
         genres=["F1", "Racing", "Highlights"], platforms=["FanCode"],
         synopsis="Overtakes, strategy gambles and team-radio meltdowns from the latest Grand Prix.",
         emoji="🏎️", colors=["#991b1b", "#111827"], moods=["hype", "mind"],
         trailer_query="F1 race highlights latest"),
]

for _item in CATALOG:          # sensible defaults so the UI never KeyErrors
    _item.setdefault("telugu", False)
    _item.setdefault("fav", False)
    _item.setdefault("moods", [])

BY_ID = {item["id"]: item for item in CATALOG}

MOODS: dict[str, dict] = {
    "bored":     {"label": "😐 Bored",       "tags": {"hype", "fun"},
                  "line": "Boredom detected. Deploying countermeasures…"},
    "hyped":     {"label": "⚡ Hyped",       "tags": {"hype", "action"},
                  "line": "Energy at 200%. Here's something that can keep up."},
    "chill":     {"label": "😌 Chill",       "tags": {"chill", "comfort"},
                  "line": "Low effort, high comfort. Blanket mode on."},
    "nostalgic": {"label": "🥹 Nostalgic",   "tags": {"nostalgia", "comfort"},
                  "line": "Rewinding to the good old days. Doraemon's got you."},
    "low":       {"label": "😢 Low-key sad", "tags": {"comfort", "fun"},
                  "line": "Sending a virtual hug. These always help. 💜"},
    "squad":     {"label": "🎉 Squad mode",  "tags": {"social", "drama"},
                  "line": "Group-watch picks. Open the Lounge and drag your friends in."},
    "brainy":    {"label": "🧠 Big-brain",   "tags": {"mind"},
                  "line": "Plot twists and mind-benders, coming right up."},
}

BOOSTS = [
    "Fun fact: a group of flamingos is called a flamboyance. Be flamboyant today. 🦩",
    "Octopuses have three hearts. You only need one good episode. 🐙",
    "Honey never spoils, and neither does a Doraemon rewatch. 🍯",
    "Sea otters hold hands while they sleep so they don't drift apart. Text your bestie. 🦦",
    "Your boredom just rolled a natural 1. VibeSync rolled a 20. 🎲",
    "Loading happiness… 99%… just pick a card already. ✨",
    "Cows have best friends and get stressed when they're apart. Respect the squad. 🐄",
    "You survived 100% of your bad days so far. Undefeated. 🏆",
]

# Episode tracker seed data (your own logs get added on top, saved in data/profile.json)
TRACKER_SHOWS = {
    "bbt10": {
        "title": "Bigg Boss Telugu 10",
        "seed_updates": [
            {"ts": "2026-10-29", "tag": "Buzz",
             "text": "Rohit & Trigun are reported to be pulling the most audience votes (Deccan Chronicle)."},
        ],
        "links": {
            "Latest promos": "https://www.youtube.com/results?search_query=Bigg+Boss+Telugu+10+latest+promo",
            "Elimination news": "https://www.google.com/search?q=Bigg+Boss+Telugu+10+elimination+this+week&tbm=nws",
            "Watch on JioHotstar": "https://www.jiohotstar.com",
        },
    },
    "bbjodi2": {
        "title": "BB Jodi Season 2",
        "seed_updates": [
            {"ts": "2026-03-29", "tag": "Finale", "text": "Grand finale aired on Star Maa. Season 2 is wrapped."},
        ],
        "links": {
            "Best performances": "https://www.youtube.com/results?search_query=BB+Jodi+Season+2+best+performances",
            "Watch on JioHotstar": "https://www.jiohotstar.com",
        },
    },
}

TRACKER_TAGS = ["Highlight", "Nomination", "Elimination", "Captaincy", "Wild card", "Hot take", "Buzz", "Finale"]


def items_of(kind: str) -> list[dict]:
    return CATALOG if kind == "all" else [i for i in CATALOG if i["kind"] == kind]


def items_for_mood(mood: str) -> list[dict]:
    tags = MOODS[mood]["tags"]
    return [i for i in CATALOG if tags & set(i["moods"])]


def all_genres(items: list[dict] | None = None) -> list[str]:
    return sorted({g for i in (items or CATALOG) for g in i["genres"]})


def all_platforms(items: list[dict] | None = None) -> list[str]:
    return sorted({p.rstrip("*") for i in (items or CATALOG) for p in i["platforms"]})


def default_favorites() -> list[str]:
    return [i["id"] for i in CATALOG if i["fav"]]


def filter_items(kind="all", query="", genres=(), platforms=(), telugu_only=False) -> list[dict]:
    q = query.strip().lower()
    out = []
    for item in items_of(kind):
        if q and q not in (item["title"] + " " + item["synopsis"] + " " + " ".join(item["genres"])).lower():
            continue
        if genres and not set(genres) & set(item["genres"]):
            continue
        if platforms and not set(platforms) & {p.rstrip("*") for p in item["platforms"]}:
            continue
        if telugu_only and not item["telugu"]:
            continue
        out.append(item)
    return out
