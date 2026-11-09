"""Page chrome + Lounge styles. Colours follow the theme picked inside Discover."""
import streamlit as st

THEMES = {
    "cinema":   dict(bg="#150A0E", s1="#1F1016", s2="#2B1820", line="rgba(244,185,66,.14)", text="#F7EFE3",
                     muted="#BFA9A0", accent="#F4B942", on_accent="#2A1408", hot="#FF5A4E"),
    "daylight": dict(bg="#F7F4EF", s1="#FFFFFF", s2="#EFE9E1", line="rgba(40,30,20,.12)", text="#1E1A17",
                     muted="#6B615A", accent="#0F766E", on_accent="#FFFFFF", hot="#E11D48"),
    "deepsea":  dict(bg="#06171C", s1="#0C252C", s2="#123139", line="rgba(94,230,184,.14)", text="#E6F4F1",
                     muted="#8FB3AC", accent="#5EE6B8", on_accent="#03231A", hot="#FF6B6B"),
    "mono":     dict(bg="#000000", s1="#121212", s2="#1E1E1E", line="rgba(255,255,255,.12)", text="#FFFFFF",
                     muted="#9C9C9C", accent="#FFFFFF", on_accent="#000000", hot="#FF453A"),
}

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&display=swap');
:root{--bg:%(bg)s;--s1:%(s1)s;--s2:%(s2)s;--line:%(line)s;--text:%(text)s;--muted:%(muted)s;--accent:%(accent)s;--on-accent:%(on_accent)s;--hot:%(hot)s;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text);
  font-family:'Bricolage Grotesque',system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp *{font-family:inherit}
.stApp p,.stApp label,.stApp span,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:var(--text)}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;height:0!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:.5rem .6rem 1rem!important;max-width:1180px}
[data-testid="stVerticalBlock"]{gap:.6rem}
iframe{border:0;display:block}

/* top switcher */
.st-key-nav_widget{display:flex;justify-content:center}
.st-key-nav_widget [data-baseweb="button-group"]{background:var(--s1);border-radius:999px;padding:3px;border:1px solid var(--line)}
.st-key-nav_widget button{border:0!important;border-radius:999px!important;background:transparent!important;color:var(--muted)!important;font-weight:600;padding:.2rem 1.1rem!important;min-height:34px}
.st-key-nav_widget button[kind$="Active"],.st-key-nav_widget button[aria-checked="true"],.st-key-nav_widget button[data-testid$="Active"]{background:var(--accent)!important;color:var(--on-accent)!important}
.st-key-nav_widget button p{color:inherit!important}

/* widgets */
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{border-radius:999px;border:1px solid var(--line);background:var(--s1);color:var(--text);font-weight:600;transition:transform .15s,background-color .2s}
.stButton>button:active,.stFormSubmitButton>button:active{transform:scale(.97)}
.stButton>button[kind="primary"],.stFormSubmitButton>button{background:var(--accent);color:var(--on-accent);border-color:transparent}
.stButton>button p,.stFormSubmitButton>button p{color:inherit!important}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div,[data-baseweb="input"]{background:var(--s1)!important;color:var(--text)!important;border-color:var(--line)!important;border-radius:12px!important}
[data-testid="stChatInput"]{background:var(--s1)!important;border-color:var(--line)!important}
[data-testid="stChatInput"] textarea{color:var(--text)!important}
[data-testid="stExpander"]{background:var(--s1);border:1px solid var(--line);border-radius:16px}
[data-testid="stExpander"] summary{color:var(--text)}
[data-testid="stCode"],.stCode{border-radius:12px}

/* lounge */
.vs-section{margin:.6rem 0 .3rem}.vs-sec-title{font-weight:800;font-size:clamp(1.4rem,5vw,2rem);letter-spacing:-.02em}
.vs-sec-title .ic{margin-right:.35rem}.vs-sec-sub{display:block;color:var(--muted);font-size:.95rem;margin-top:.15rem}
.vs-roomhead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem;padding:1rem 1.1rem;border-radius:20px;background:var(--s1);border:1px solid var(--line)}
.vs-roomname{font-weight:800;font-size:1.3rem;letter-spacing:-.01em}
.vs-code{font-weight:800;letter-spacing:.25em;font-size:1.2rem;background:var(--accent);color:var(--on-accent);padding:.3rem .8rem;border-radius:12px}
.vs-chat{display:flex;flex-direction:column-reverse;gap:.55rem;height:400px;overflow-y:auto;padding:.8rem;border-radius:18px;background:var(--s1);border:1px solid var(--line);scrollbar-width:thin}
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


def palette(theme: str) -> dict:
    return THEMES.get(theme, THEMES["cinema"])


def inject(theme: str = "cinema") -> None:
    st.markdown(CSS % palette(theme), unsafe_allow_html=True)
