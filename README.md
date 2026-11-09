# ⚡ VibeSync

Pick something to watch in seconds, then jump straight into it.

- **Discover.** Real posters, a featured carousel, a mood picker, category tabs (For you, Anime, Movies, Series, Reality TV, Sports, Saved), search and a Surprise Me roll. Tap any poster for details: IMDb rating, where it streams in India, and buttons that open that exact title in Netflix, Prime Video, JioHotstar, Crunchyroll, Sony LIV, ZEE5 or FanCode. Bigg Boss Telugu and BB Jodi have a built-in episode tracker. There are four looks to pick from (Cinema hall, Daylight, Late show, Poster black). Favourites, tracker notes and your look are saved on your device.
- **Lounge.** Shared rooms with a code or link: live chat with `:emoji:` codes and badges, floating reactions, a watch poll and a synced countdown.

Availability, deep links, posters and ratings were checked on JustWatch India (Nov 2026). Platforms change, so re-check on justwatch.com/in and edit `core/data.py`.

Built with **Python + Streamlit**. Discover is a custom Streamlit component (plain HTML/CSS/JS in `components/discover/`) that runs in the browser, so every tap is instant. It's responsive for laptop (Asus TUF F15) and phone (Realme P1 5G).

---

## 1. Run it locally (VS Code + Git)

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) (tick **"Add Python to PATH"** on Windows), [Git](https://git-scm.com/downloads) and [VS Code](https://code.visualstudio.com/) with the **Python** extension.

1. Unzip `vibesync.zip`, then in VS Code use **File → Open Folder… → `vibesync`**.
2. Open a terminal (**Terminal → New Terminal**) and run:

```bash
# create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Your browser opens **http://localhost:8501**. 🎉

> PowerShell says "running scripts is disabled"? Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.
> VS Code asks to select an interpreter? Pick the one inside `.venv`.

### Put it on Git / GitHub

```bash
git init
git add .
git commit -m "VibeSync v1"
# create an empty repo on github.com, then:
git branch -M main
git remote add origin https://github.com/<your-username>/vibesync.git
git push -u origin main
```

`.gitignore` already keeps your chat rooms and tracker logs (`data/*.json`) and the virtual env out of Git.

### Run the tests

```bash
python -m unittest discover tests
```

---

## 2. Open it on your phone / share the Lounge with friends

**Same Wi-Fi (quickest).** When you run `streamlit run app.py`, the terminal prints a **Network URL** like `http://192.168.1.7:8501`. Open that on your Realme phone or your friends' phones.

- Allow Python through the Windows firewall if it asks.
- Room invite links use whatever address you opened the app with, so open it via the Network URL before sharing.

**Over the internet (free).** Deploy on **Streamlit Community Cloud**:

1. Push the repo to GitHub (above).
2. Go to [share.streamlit.io](https://share.streamlit.io), click **Create app**, pick your repo and branch `main`, and set the file to `app.py`.
3. You get a URL like `https://vibesync-yourname.streamlit.app`. Share it, and everyone can join the same rooms.

Notes on the cloud version:

- Community Cloud apps sleep after a few days without visits; the first open wakes them up.
- Rooms and tracker logs reset when the server restarts.
- The app runs as one shared profile (favourites and tracker), because it's designed as *your* app. Friends only need a display name in the Lounge.

---

## 3. Build the Android APK 📱

Streamlit runs as a Python server, so the APK is a **native Android shell**: a full-screen WebView that opens your deployed VibeSync URL. It shows a neon offline screen and sends Trailer / "Watch on" links to the YouTube / JioHotstar apps. The ready files are in the `android/` folder.

1. **Deploy first** (section 2) so you have a public URL. For Wi-Fi-only testing you can use `http://<laptop-ip>:8501`.
2. Install [Android Studio](https://developer.android.com/studio).
3. **New Project → Empty Views Activity** (not "Empty Activity", which is Compose).
   - Name: `VibeSync`
   - Package name: `com.vibesync.app`
   - Language: **Kotlin**
   - Minimum SDK: API 24
4. Wait for the first Gradle sync, then replace these files in your new project with the ones from `android/app/src/main/`:

   | Copy from `android/…`                                | Into the Android Studio project                           |
   |------------------------------------------------------|-----------------------------------------------------------|
   | `java/com/vibesync/app/MainActivity.kt`              | `app/src/main/java/com/vibesync/app/MainActivity.kt`      |
   | `AndroidManifest.xml`                                | `app/src/main/AndroidManifest.xml`                        |
   | `res/values/strings.xml`, `res/values/themes.xml`    | `app/src/main/res/values/`                                |
   | `assets/offline.html`                                | `app/src/main/assets/` (create via **File → New → Folder → Assets Folder**) |

5. **Delete** `app/src/main/res/values-night/themes.xml` (it would override the dark neon theme). If the template made `res/layout/activity_main.xml`, you can delete it too, since it's unused.
6. In `strings.xml`, set `vibesync_url` to **your** deployed URL.
7. *(Optional)* Set the app icon: right-click `res` → **New → Image Asset** → choose `android/vibesync-icon.png`.
8. **Build → Generate App Bundles or APKs → Build APK(s)**. Click **locate** to get `app-debug.apk`.
9. Install it on your phone. Either copy the APK over and tap it (allow "Install unknown apps"), or plug in the phone with USB debugging enabled and press ▶ Run.

For a shareable release build, use **Build → Generate Signed App Bundle / APK** and create a keystore. Don't commit the keystore.

---

## 4. Make it yours

| Want to…                         | Edit                                                                                  |
|----------------------------------|---------------------------------------------------------------------------------------|
| Add / change shows, movies, anime | `core/data.py` → `CATALOG`, then place it in a Browse row in `GROUPS`               |
| Use real poster images           | add `poster="https://…jpg"` to an item; it replaces the generated neon art             |
| Add moods or boost lines         | `MOODS` and `BOOSTS` in `core/data.py`                                                |
| New chat emoji codes / badges    | `core/emoji.py`                                                                       |
| Colours, glows, animations       | `core/styles.py` (CSS variables at the top)                                           |
| Chat refresh speed, limits       | `core/config.py`                                                                      |

### Project layout

```
vibesync/
├─ app.py                 # entry point + top navigation
├─ core/
│  ├─ config.py           # tunable settings
│  ├─ data.py             # catalog, moods, tracker seeds, filters
│  ├─ styles.py           # page + Lounge CSS for each look
│  ├─ cards.py            # HTML builders for cards, chat, poll, countdown
│  ├─ emoji.py            # :shortcodes:, badges, reactions
│  ├─ store.py            # thread-safe JSON stores (rooms, profile)
│  └─ state.py            # shared singletons (st.cache_resource)
├─ views/                 # discover.py (component wrapper) · lounge.py
├─ components/discover/   # index.html: the whole Discover UI
├─ tests/                 # unit tests for store, cards, filters
├─ android/               # WebView APK shell + icon
└─ .streamlit/config.toml # dark theme
```

### Good to know

- **Reality TV "live" data.** There's no free official API for Bigg Boss Telugu, so the tracker is semi-manual. It's seeded with recent news, you log episodes and twists (saved to `data/profile.json`), and one-tap buttons jump to the latest promos and elimination news.
- **Platforms.** "Watch on" lists Indian platforms as of late 2026. These change often, and `*` means "check your region or language menu" (e.g. Telugu dubs of individual Doraemon movies).
- **Trailer buttons** open a YouTube search for that title, so they never break when videos get re-uploaded.
- Requires **Streamlit ≥ 1.40** (uses `st.pills`, `st.segmented_control` and auto-refreshing fragments for the live Lounge).
