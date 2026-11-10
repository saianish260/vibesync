"""Page chrome + Lounge styles. Colours follow the theme picked inside Discover."""
import re

import streamlit as st

THEMES = {
    "cinema":   dict(bg="#0D0A12", s1="#17131E", s2="#221C2B", line="rgba(246,242,236,.08)", text="#F6F2EC",
                     muted="#A69EB0", accent="#FFB547", on_accent="#1A1208", hot="#FF4D5E"),
    "daylight": dict(bg="#F6F3EE", s1="#FFFFFF", s2="#EDE7DF", line="rgba(30,26,23,.1)", text="#1D1916",
                     muted="#6E655D", accent="#0F766E", on_accent="#FFFFFF", hot="#E11D48"),
    "deepsea":  dict(bg="#05161B", s1="#0B232A", s2="#123039", line="rgba(230,244,241,.08)", text="#E8F5F2",
                     muted="#8FB3AC", accent="#5EE6B8", on_accent="#03231A", hot="#FF6B6B"),
    "mono":     dict(bg="#000000", s1="#111111", s2="#1C1C1C", line="rgba(255,255,255,.1)", text="#FFFFFF",
                     muted="#9A9A9A", accent="#FFFFFF", on_accent="#000000", hot="#FF453A"),
}

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap');
:root{--bg:%(bg)s;--s1:%(s1)s;--s2:%(s2)s;--line:%(line)s;--text:%(text)s;--muted:%(muted)s;--accent:%(accent)s;--on-accent:%(on_accent)s;--hot:%(hot)s;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text);
  font-family:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased}
.stApp *{font-family:inherit}
.stApp p,.stApp label,.stApp span,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:var(--text)}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;height:0!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:.75rem 1rem 2rem!important;max-width:1080px}
.stApp::before{content:"";position:fixed;inset:0 0 auto 0;height:70vh;pointer-events:none;z-index:0;
  background:radial-gradient(80%% 60%% at 50%% 0%%,color-mix(in srgb,var(--accent) 22%%,transparent),transparent 70%%)}
[data-testid="stVerticalBlock"]{gap:.6rem}
iframe{border:0;display:block}

/* Lounge top bar */
.vs-top{display:flex;align-items:center;justify-content:space-between;gap:.8rem;margin:.2rem 0 .4rem}
.vs-mark{font-weight:900;font-size:1.45rem;letter-spacing:-.03em;font-variation-settings:"wdth" 125}
.vs-mark i{font-style:normal;color:var(--accent)}
.st-key-back_discover{display:flex;justify-content:flex-end}
.st-key-back_discover button{min-height:42px;padding:0 1.1rem!important;background:var(--s2)!important;border:0!important}
.vs-hero{position:relative;padding:1.4rem 1.3rem;border-radius:26px;overflow:hidden;margin:.4rem 0 .6rem;
  background:linear-gradient(125deg,color-mix(in srgb,var(--accent) 30%%,var(--s1)),var(--s1) 62%%);box-shadow:inset 0 0 0 1px var(--line)}
.vs-hero h1{margin:0;font-weight:850;font-variation-settings:"wdth" 125;font-size:clamp(2rem,8vw,3.4rem);line-height:.95;letter-spacing:-.035em}
.vs-hero p{margin:.6rem 0 0;color:var(--muted)!important;font-size:1rem;max-width:44ch}
.vs-hero .emo{position:absolute;right:1rem;top:.6rem;font-size:3.6rem;opacity:.9;transform:rotate(8deg)}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]){border-radius:22px!important}

/* widgets */
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{border-radius:999px;border:1px solid var(--line);background:var(--s1);color:var(--text);font-weight:700;min-height:44px;transition:transform .15s,background-color .2s,filter .2s}
.stButton>button:hover{filter:brightness(1.08);border-color:var(--line)!important;color:var(--text)!important}
.stButton>button:active,.stFormSubmitButton>button:active{transform:scale(.97)}
.stButton>button[kind="primary"],.stFormSubmitButton>button{background:var(--accent);color:var(--on-accent);border-color:transparent;box-shadow:0 8px 24px color-mix(in srgb,var(--accent) 30%%,transparent)}
.stButton>button p,.stFormSubmitButton>button p{color:inherit!important}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div,[data-baseweb="input"]{background:var(--s1)!important;color:var(--text)!important;border-color:var(--line)!important;border-radius:12px!important}
[data-testid="stChatInput"]{background:var(--s1)!important;border-color:var(--line)!important}
[data-testid="stChatInput"] textarea{color:var(--text)!important}
[data-testid="stExpander"]{background:var(--s1);border:1px solid var(--line);border-radius:16px}
[data-testid="stExpander"] summary{color:var(--text)}
[data-testid="stCode"],.stCode{border-radius:12px}

/* lounge */
.vs-section{margin:.6rem 0 .3rem}.vs-sec-title{font-weight:850;font-variation-settings:"wdth" 118;font-size:clamp(1.4rem,5vw,2rem);letter-spacing:-.025em}
.vs-sec-title .ic{margin-right:.35rem}.vs-sec-sub{display:block;color:var(--muted);font-size:.95rem;margin-top:.15rem}
.vs-roomhead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem;padding:1.1rem 1.2rem;border-radius:24px;background:linear-gradient(125deg,color-mix(in srgb,var(--accent) 26%%,var(--s1)),var(--s1) 65%%);box-shadow:inset 0 0 0 1px var(--line)}
.vs-roomname{font-weight:850;font-variation-settings:"wdth" 120;font-size:1.5rem;letter-spacing:-.02em}
.vs-code{font-weight:800;letter-spacing:.25em;font-size:1.2rem;background:var(--accent);color:var(--on-accent);padding:.3rem .8rem;border-radius:12px}
.vs-chat{display:flex;flex-direction:column-reverse;gap:.55rem;height:400px;overflow-y:auto;padding:.9rem;border-radius:22px;background:var(--s1);box-shadow:inset 0 0 0 1px var(--line);scrollbar-width:thin}
.vs-msg{display:flex;gap:.5rem;align-items:flex-end;max-width:88%%;animation:msgIn .3s cubic-bezier(.2,.8,.2,1)}
@keyframes msgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.vs-msg.mine{align-self:flex-end;flex-direction:row-reverse}
.vs-av{flex:0 0 30px;height:30px;border-radius:50%%;display:grid;place-items:center;font-weight:800;font-size:.85rem;color:#111;background:var(--av)}
.vs-bubble{padding:.5rem .75rem;border-radius:16px 16px 16px 5px;background:var(--s2)}
.vs-msg.mine .vs-bubble{border-radius:16px 16px 5px 16px;background:var(--accent);color:var(--on-accent)}
.vs-msg.mine .vs-bubble *{color:var(--on-accent)!important}
.vs-mhead{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;font-size:.75rem;margin-bottom:.1rem}
.vs-time{opacity:.65;font-size:.68rem}
.vs-mtext{font-size:.95rem;line-height:1.4;word-break:break-word}
.vs-chip{font-size:.62rem;font-weight:700;padding:.08rem .45rem;border-radius:99px;background:rgba(128,128,128,.25)}
.vs-spoiler{filter:blur(5px);cursor:pointer;transition:filter .2s;outline:none}
.vs-spoiler:hover,.vs-spoiler:focus,.vs-spoiler:active{filter:none}
.vs-sys{align-self:center;font-size:.76rem;color:var(--muted);padding:.15rem .7rem;border-radius:999px;background:var(--s2);text-align:center}
.vs-r{font-size:1.15rem}
.vs-floaters{position:relative;height:0}
.vs-floaters span{position:absolute;bottom:0;font-size:1.9rem;opacity:0;animation:floatUp 2.6s ease-out forwards;pointer-events:none}
@keyframes floatUp{0%%{opacity:0;transform:translateY(0)}15%%{opacity:1;transform:translateY(-24px)}100%%{opacity:0;transform:translateY(-260px)}}
.vs-members{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
.vs-online{width:100%%;font-size:.8rem;color:var(--muted);margin-bottom:.15rem}
.vs-member{display:inline-flex;align-items:center;gap:.3rem;font-size:.8rem;padding:.2rem .6rem;border-radius:999px;background:var(--s2);opacity:.55}
.vs-member i{width:7px;height:7px;border-radius:50%%;background:#777}
.vs-member.on{opacity:1}.vs-member.on i{background:#34D399}
.vs-poll{display:flex;flex-direction:column;gap:.4rem;margin-top:.6rem}
.vs-pollq{font-weight:700;margin-bottom:.15rem}
.vs-pollrow{position:relative;display:flex;justify-content:space-between;align-items:center;padding:.55rem .75rem;border-radius:12px;overflow:hidden;background:var(--s2);font-size:.9rem}
.vs-pollrow.lead{outline:2px solid var(--accent)}
.vs-pollfill{position:absolute;inset:0 auto 0 0;background:var(--accent);opacity:.28;transition:width .5s cubic-bezier(.2,.8,.2,1)}
.vs-polllabel,.vs-pollpct{position:relative;z-index:1}
.vs-pollpct{color:var(--muted);font-size:.78rem;white-space:nowrap;margin-left:.5rem}
.vs-tags{display:flex;flex-wrap:wrap;gap:.3rem}.vs-tag{font-size:.78rem;padding:.15rem .5rem;border-radius:8px;background:var(--s2)}
@media (max-width:640px){.vs-chat{height:340px}.vs-msg{max-width:96%%}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""


_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def custom_palette(raw) -> dict | None:
    """A title theme's palette sent by the Discover screen; only plain #rrggbb colours are accepted."""
    if not isinstance(raw, dict):
        return None
    keys = ("bg", "s1", "s2", "text", "muted", "accent", "on_accent", "hot")
    if not all(isinstance(raw.get(k), str) and _HEX.match(raw[k]) for k in keys):
        return None
    pal = {k: raw[k] for k in keys}
    r, g, b = (int(pal["text"][i:i + 2], 16) for i in (1, 3, 5))
    pal["line"] = f"rgba({r},{g},{b},.09)"
    return pal


def palette(theme: str, custom: dict | None = None) -> dict:
    return custom or THEMES.get(theme, THEMES["cinema"])


# Discover is one full-screen component with its own top bar and tab bar, so drop the page padding there.
DISCOVER_CSS = """
<style>
.block-container,[data-testid="stMainBlockContainer"]{padding:0!important;max-width:none!important}
[data-testid="stMain"],section.main,.stMain{overflow:hidden!important}
[data-testid="stVerticalBlock"]{gap:0!important}
.stApp::before{display:none}
[data-testid="stElementContainer"]:has(> .stMarkdown style){display:none}
</style>
"""


def inject(theme: str = "cinema", page: str = "discover", custom: dict | None = None) -> None:
    st.markdown(CSS % palette(theme, custom) + (DISCOVER_CSS if page == "discover" else ""), unsafe_allow_html=True)
