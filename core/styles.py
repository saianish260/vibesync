"""Midnight theme: calm dark base, violet + cyan accents, built for speed.

Performance rules this stylesheet follows (they matter on phones):
- no backdrop-filter blur and no infinite animations except the tiny LIVE dot
- one web font, loaded with display=swap
- hover effects only on devices that actually hover (desktop / laptop)
"""
import streamlit as st

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root{
  --bg:#0B0D17; --surface:#151827; --surface-2:#1D2135; --border:rgba(255,255,255,.08);
  --text:#EEF0FA; --muted:#9AA0B8; --accent:#7C5CFF; --accent-2:#22D3EE; --hot:#FF4D8D; --ok:#34D399;
  --radius:14px;
}
html,body{background:var(--bg);}
html,body,.stApp{font-family:'Space Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp{background:radial-gradient(900px 420px at 15% -8%,rgba(124,92,255,.16),transparent 60%),var(--bg);}
[data-testid="stHeader"]{background:transparent;}
.block-container,[data-testid="stMainBlockContainer"]{padding-top:1rem;padding-bottom:3rem;max-width:1280px;}
#MainMenu,footer{visibility:hidden;}
a{color:var(--accent-2);}

/* ── Streamlit widgets ─────────────────────────────────── */
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{
  border-radius:12px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-weight:600;
  transition:border-color .15s,background .15s;}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{background:var(--surface)!important;border-radius:12px!important;}
[data-testid="stExpander"]{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:8px 12px;}
[data-testid="stMetricValue"]{font-size:1.4rem;}
[data-testid="stSidebar"]{background:var(--surface);}
@media (hover:hover){
  .stButton>button:hover,.stFormSubmitButton>button:hover,.stLinkButton>a:hover{border-color:var(--accent);color:#fff;background:var(--surface-2);}
}

/* Primary call-to-action buttons (Streamlit adds .st-key-<key>) */
.st-key-surprise button,.st-key-home_surprise button{
  border:none;color:#fff;font-weight:700;letter-spacing:.04em;padding:.7rem 1rem;
  background:linear-gradient(90deg,var(--accent),#5B8CFF 55%,var(--accent-2));box-shadow:0 6px 20px rgba(124,92,255,.35);}
@media (hover:hover){.st-key-surprise button:hover,.st-key-home_surprise button:hover{filter:brightness(1.1);color:#fff;}}

/* ── Brand bar ─────────────────────────────────────────── */
.vs-brand{font-weight:700;font-size:1.3rem;letter-spacing:.12em;padding-top:.3rem;
  background:linear-gradient(90deg,var(--accent-2),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent;}

/* ── Home header (compact) ─────────────────────────────── */
.vs-hello{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem;padding:1rem 1.1rem;margin:.4rem 0 1rem;
  border-radius:18px;background:linear-gradient(120deg,rgba(124,92,255,.22),rgba(34,211,238,.08));border:1px solid var(--border);}
.vs-hello h2{margin:0;font-size:clamp(1.15rem,3.6vw,1.6rem);font-weight:700;letter-spacing:0;}
.vs-hello .sub{color:var(--muted);font-size:.9rem;margin-top:.15rem;}
.vs-boost{font-size:.85rem;padding:.45rem .8rem;border-radius:999px;background:rgba(0,0,0,.25);border:1px solid var(--border);max-width:520px;}
.vs-moodline{color:var(--accent-2);font-weight:600;margin:.2rem 0 .7rem;}

/* ── Section headers ───────────────────────────────────── */
.vs-section{display:flex;align-items:baseline;justify-content:space-between;gap:.6rem;margin:1.4rem 0 .6rem;}
.vs-sec-title{font-weight:700;font-size:clamp(1.02rem,2.6vw,1.2rem);}
.vs-sec-title .ic{margin-right:.35rem;}
.vs-sec-sub{color:var(--muted);font-size:.82rem;}

/* ── Cards ─────────────────────────────────────────────── */
.vs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px;}
.vs-rail{display:grid;grid-auto-flow:column;grid-auto-columns:200px;gap:14px;overflow-x:auto;padding:2px 2px 10px;
  scroll-snap-type:x proximity;-webkit-overflow-scrolling:touch;scrollbar-width:thin;scrollbar-color:var(--surface-2) transparent;}
.vs-rail>.vs-card{scroll-snap-align:start;}
.vs-card{display:flex;flex-direction:column;border-radius:var(--radius);overflow:hidden;background:var(--surface);border:1px solid var(--border);
  transition:transform .18s ease,border-color .18s ease;}
@media (hover:hover){.vs-card:hover{transform:translateY(-4px);border-color:rgba(124,92,255,.6);}}

.vs-poster{position:relative;aspect-ratio:1/1;width:100%;background:linear-gradient(150deg,var(--c1),var(--c2));overflow:hidden;}
.vs-poster::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,13,23,0) 55%,rgba(11,13,23,.55));}
.vs-emoji{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:3.6rem;filter:drop-shadow(0 4px 10px rgba(0,0,0,.35));}
.vs-kind,.vs-live,.vs-status,.vs-tel{position:absolute;z-index:1;font-size:.62rem;font-weight:700;letter-spacing:.08em;padding:.18rem .5rem;border-radius:999px;}
.vs-kind{top:.5rem;left:.5rem;background:rgba(11,13,23,.6);color:#dfe2f2;}
.vs-live{bottom:.5rem;left:.5rem;background:var(--hot);color:#fff;display:flex;align-items:center;gap:.3rem;}
.vs-live i{width:6px;height:6px;border-radius:50%;background:#fff;animation:blink 1.2s steps(2) infinite;}
@keyframes blink{50%{opacity:.25}}
.vs-status{bottom:.5rem;left:.5rem;background:rgba(11,13,23,.6);color:#dfe2f2;}
.vs-tel{top:2rem;left:.5rem;background:rgba(52,211,153,.18);color:#a7f3d0;border:1px solid rgba(52,211,153,.45);letter-spacing:0;}

.vs-body{display:flex;flex-direction:column;gap:.4rem;padding:.7rem .75rem .8rem;flex:1;}
.vs-title{font-weight:700;font-size:.95rem;line-height:1.25;}
.vs-meta{color:var(--muted);font-size:.76rem;margin-top:-.2rem;}
.vs-tags{display:flex;flex-wrap:nowrap;gap:.25rem;overflow:hidden;}
.vs-rail .vs-kind{display:none;}
.vs-rail .vs-tel{top:.5rem;}
.vs-tag{white-space:nowrap;font-size:.68rem;padding:.12rem .45rem;border-radius:6px;background:var(--surface-2);color:#c9cde3;}
.vs-syn{margin:0;color:#c3c7dc;font-size:.8rem;line-height:1.4;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}
.vs-plat{font-size:.74rem;color:var(--muted);margin-top:auto;}
.vs-plat b{color:var(--accent-2);font-weight:600;}
.vs-play{display:block;text-align:center;padding:.5rem .6rem;border-radius:10px;font-weight:700;font-size:.82rem;
  text-decoration:none!important;color:#fff!important;background:var(--accent);}
@media (hover:hover){.vs-play:hover{background:#6a48ff;}}
.vs-empty{padding:1.6rem;text-align:center;border-radius:var(--radius);background:var(--surface);border:1px dashed var(--border);color:var(--muted);}

/* Wide card (Live now) */
.vs-wide{display:grid;grid-template-columns:150px 1fr;border-radius:var(--radius);overflow:hidden;background:var(--surface);border:1px solid var(--border);}
.vs-wide .vs-poster{aspect-ratio:auto;height:100%;min-height:190px;}
.vs-wide .vs-syn{-webkit-line-clamp:3;}
.vs-wide .vs-play{align-self:flex-start;padding:.5rem 1rem;}

/* ── Spotlight (Surprise Me result) ────────────────────── */
.vs-spotlight{margin:.6rem 0 1.2rem;padding:.9rem;border-radius:18px;background:var(--surface);
  border:1px solid rgba(124,92,255,.55);box-shadow:0 10px 40px rgba(124,92,255,.22);animation:pop .35s ease-out both;}
.vs-spot-label{font-weight:700;letter-spacing:.14em;font-size:.72rem;color:var(--accent-2);margin-bottom:.6rem;}
.vs-spot-inner{display:grid;grid-template-columns:minmax(150px,220px) 1fr;gap:1rem;}
.vs-spot-inner .vs-poster{border-radius:12px;}
.vs-spot-inner .vs-title{font-size:1.35rem;}
.vs-spot-inner .vs-syn{font-size:.95rem;-webkit-line-clamp:6;}
.vs-spot-inner .vs-plat{margin-top:.4rem;}
.vs-spot-inner .vs-play{align-self:flex-start;padding:.6rem 1.3rem;font-size:.95rem;}
@keyframes pop{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:none}}
.vs-confetti{position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden;}
.vs-confetti i{position:absolute;top:-16px;width:8px;height:12px;border-radius:2px;opacity:0;animation:fall 1.8s ease-in forwards;}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(100vh) rotate(540deg)}}

/* ── Tracker ───────────────────────────────────────────── */
.vs-update{display:flex;gap:.55rem;align-items:flex-start;padding:.5rem .65rem;margin:.3rem 0;border-radius:10px;background:var(--surface);
  border:1px solid var(--border);border-left:3px solid var(--accent);font-size:.88rem;}
.vs-update .d{color:var(--muted);font-size:.72rem;white-space:nowrap;padding-top:.1rem;}
.vs-utag{font-size:.66rem;font-weight:700;padding:.1rem .45rem;border-radius:6px;background:rgba(255,77,141,.15);color:#ffb3cd;white-space:nowrap;}

/* ── Lounge ────────────────────────────────────────────── */
.vs-roomhead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem;padding:.9rem 1.1rem;border-radius:16px;margin-bottom:.9rem;
  background:linear-gradient(120deg,rgba(124,92,255,.22),rgba(34,211,238,.06));border:1px solid var(--border);}
.vs-roomname{font-weight:700;font-size:1.15rem;}
.vs-code{font-weight:700;letter-spacing:.28em;font-size:1.15rem;color:var(--accent-2);padding:.25rem .7rem;border:1px dashed rgba(34,211,238,.5);border-radius:10px;}
.vs-chat{display:flex;flex-direction:column-reverse;gap:.5rem;height:400px;overflow-y:auto;padding:.75rem;border-radius:var(--radius);
  background:var(--surface);border:1px solid var(--border);scrollbar-width:thin;scrollbar-color:var(--surface-2) transparent;}
.vs-msg{display:flex;gap:.5rem;align-items:flex-end;max-width:88%;}
.vs-msg.mine{align-self:flex-end;flex-direction:row-reverse;}
.vs-av{flex:0 0 30px;height:30px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:.85rem;color:#0B0D17;background:var(--av);}
.vs-bubble{padding:.45rem .7rem;border-radius:14px 14px 14px 4px;background:var(--surface-2);}
.vs-msg.mine .vs-bubble{border-radius:14px 14px 4px 14px;background:rgba(124,92,255,.35);}
.vs-mhead{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;font-size:.75rem;margin-bottom:.1rem;}
.vs-time{color:var(--muted);font-size:.68rem;}
.vs-mtext{font-size:.93rem;line-height:1.4;word-break:break-word;}
.vs-chip{font-size:.62rem;font-weight:700;padding:.08rem .4rem;border-radius:6px;}
.vs-chip.hot{color:#ffc6a8;background:rgba(255,120,60,.18);}
.vs-chip.spoiler{color:#fde68a;background:rgba(253,230,138,.14);}
.vs-chip.hype{color:#a5f3fc;background:rgba(34,211,238,.15);}
.vs-chip.elim{color:#ffb3cd;background:rgba(255,77,141,.16);}
.vs-spoiler{filter:blur(5px);cursor:pointer;transition:filter .2s;outline:none;}
.vs-spoiler:hover,.vs-spoiler:focus,.vs-spoiler:active{filter:none;}
.vs-sys{align-self:center;font-size:.75rem;color:var(--muted);padding:.15rem .65rem;border-radius:999px;background:rgba(255,255,255,.04);text-align:center;}
.vs-r{font-size:1.15rem;}
.vs-floaters{position:relative;height:0;}
.vs-floaters span{position:absolute;bottom:0;font-size:1.8rem;opacity:0;animation:floatUp 2.6s ease-out forwards;pointer-events:none;}
@keyframes floatUp{0%{opacity:0;transform:translateY(0)}15%{opacity:1;transform:translateY(-24px)}100%{opacity:0;transform:translateY(-260px)}}
.vs-members{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;}
.vs-online{width:100%;font-size:.78rem;color:var(--ok);margin-bottom:.15rem;}
.vs-member{display:inline-flex;align-items:center;gap:.3rem;font-size:.78rem;padding:.18rem .55rem;border-radius:999px;background:var(--surface-2);opacity:.55;}
.vs-member i{width:7px;height:7px;border-radius:50%;background:#555;}
.vs-member.on{opacity:1;}
.vs-member.on i{background:var(--ok);}
.vs-poll{display:flex;flex-direction:column;gap:.4rem;}
.vs-pollq{font-weight:700;margin-bottom:.15rem;}
.vs-pollrow{position:relative;display:flex;justify-content:space-between;align-items:center;padding:.5rem .7rem;border-radius:10px;overflow:hidden;background:var(--surface-2);font-size:.88rem;}
.vs-pollrow.lead{outline:1px solid var(--accent-2);}
.vs-pollfill{position:absolute;inset:0 auto 0 0;background:rgba(124,92,255,.38);transition:width .4s ease;}
.vs-polllabel,.vs-pollpct{position:relative;z-index:1;}
.vs-pollpct{color:var(--muted);font-size:.78rem;white-space:nowrap;margin-left:.5rem;}

/* ── Phones (Realme P1 5G etc.) ────────────────────────── */
@media (max-width:640px){
  .block-container,[data-testid="stMainBlockContainer"]{padding-left:.75rem;padding-right:.75rem;padding-top:.6rem;}
  .vs-rail{grid-auto-columns:150px;gap:10px;}
  .vs-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
  .vs-emoji{font-size:2.8rem;}
  .vs-body{padding:.55rem .55rem .65rem;gap:.3rem;}
  .vs-title{font-size:.84rem;}
  .vs-card .vs-syn{display:none;}
  .vs-tag:nth-child(n+3){display:none;}
  .vs-play{font-size:.76rem;padding:.42rem .4rem;}
  .vs-wide{grid-template-columns:110px 1fr;}
  .vs-wide .vs-poster{min-height:170px;}
  .vs-spot-inner{grid-template-columns:120px 1fr;gap:.75rem;}
  .vs-spot-inner .vs-title{font-size:1.05rem;}
  .vs-spot-inner .vs-syn{font-size:.82rem;-webkit-line-clamp:4;}
  .vs-hello{padding:.85rem .9rem;}
  .vs-boost{font-size:.8rem;}
  .vs-chat{height:340px;}
  .vs-msg{max-width:96%;}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
