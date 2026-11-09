"""Cyberpunk neon + glassmorphism theme, injected once per page run."""
import streamlit as st

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root{
  --bg:#07060f; --violet:#7a5cff; --violet-deep:#2a1066; --blue:#2b6bff; --cyan:#00f0ff;
  --pink:#ff2bd6; --lime:#39ff14; --text:#e8e6ff; --muted:#a3a0c8;
  --glass:rgba(255,255,255,.045); --glass-border:rgba(0,240,255,.16); --radius:18px;
}

/* ── App shell ─────────────────────────────────────────── */
html,body,.stApp{font-family:'Space Grotesk',system-ui,sans-serif;}
html,body{background:#07060f;}
.stApp{
  background:
    radial-gradient(1100px 600px at 10% -10%, rgba(122,92,255,.35), transparent 60%),
    radial-gradient(900px 600px at 110% 10%, rgba(0,240,255,.18), transparent 60%),
    radial-gradient(800px 700px at 50% 120%, rgba(255,43,214,.16), transparent 60%),
    linear-gradient(180deg,#07060f 0%,#0b0820 55%,#07060f 100%);
  background-attachment:fixed;
}
.stApp::before{ /* subtle moving grid floor */
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.18;
  background-image:linear-gradient(rgba(0,240,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(122,92,255,.12) 1px,transparent 1px);
  background-size:46px 46px;mask-image:linear-gradient(180deg,transparent,black 30%,transparent 95%);
  animation:gridMove 18s linear infinite;
}
@keyframes gridMove{to{background-position:0 46px,46px 0}}
[data-testid="stHeader"]{background:transparent;}
.block-container,[data-testid="stMainBlockContainer"]{padding-top:1.4rem;padding-bottom:4rem;max-width:1400px;}
#MainMenu,footer{visibility:hidden;}
h1,h2,h3{font-family:'Orbitron',sans-serif;letter-spacing:.04em;}
a{color:var(--cyan);}

/* ── Streamlit widgets, neon-ified ─────────────────────── */
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{
  border-radius:12px;border:1px solid rgba(0,240,255,.35);background:rgba(10,8,30,.6);
  color:var(--text);font-weight:600;transition:all .2s ease;backdrop-filter:blur(8px);
}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stLinkButton>a:hover{
  border-color:var(--cyan);color:#fff;box-shadow:0 0 18px rgba(0,240,255,.45),inset 0 0 12px rgba(0,240,255,.12);transform:translateY(-1px);
}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{
  background:rgba(12,10,32,.7)!important;border-radius:12px!important;border-color:rgba(122,92,255,.4)!important;
}
[data-testid="stExpander"]{background:var(--glass);border:1px solid var(--glass-border);border-radius:var(--radius);backdrop-filter:blur(14px);}
[data-testid="stMetric"]{background:var(--glass);border:1px solid var(--glass-border);border-radius:14px;padding:10px 14px;}
.stTabs [data-baseweb="tab-list"]{gap:6px;}
.stTabs [data-baseweb="tab"]{background:var(--glass);border-radius:12px 12px 0 0;padding:6px 16px;}
[data-testid="stSidebar"]{background:rgba(8,6,22,.92);border-right:1px solid var(--glass-border);}

/* The big glowing Surprise Me! button (Streamlit adds .st-key-<key>) */
.st-key-surprise button,.st-key-home_surprise button{
  font-family:'Orbitron',sans-serif;font-size:1.05rem;letter-spacing:.08em;padding:.8rem 1.2rem;border:none;color:#fff;
  background:linear-gradient(90deg,var(--pink),var(--violet),var(--cyan),var(--pink));background-size:300% 100%;
  animation:shimmer 4s linear infinite,pulseGlow 2.2s ease-in-out infinite;
}
.st-key-surprise button:hover,.st-key-home_surprise button:hover{transform:translateY(-2px) scale(1.02);}
@keyframes shimmer{to{background-position:300% 0}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 14px rgba(255,43,214,.5),0 0 28px rgba(0,240,255,.25)}50%{box-shadow:0 0 26px rgba(255,43,214,.85),0 0 52px rgba(0,240,255,.5)}}

/* ── Brand bar ─────────────────────────────────────────── */
.vs-brand{font-family:'Orbitron',sans-serif;font-weight:900;font-size:1.35rem;letter-spacing:.14em;
  background:linear-gradient(90deg,var(--cyan),var(--violet),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 10px rgba(0,240,255,.35));padding-top:.35rem;}

/* ── Hero ──────────────────────────────────────────────── */
.vs-hero{position:relative;text-align:center;padding:2.2rem 1rem 1.6rem;margin-bottom:1rem;border-radius:26px;
  background:linear-gradient(135deg,rgba(122,92,255,.16),rgba(0,240,255,.06) 50%,rgba(255,43,214,.12));
  border:1px solid var(--glass-border);backdrop-filter:blur(16px);overflow:hidden;animation:rise .6s ease both;}
.vs-hero::after{content:"";position:absolute;inset:-40%;background:conic-gradient(from 0deg,transparent,rgba(0,240,255,.12),transparent 30%);animation:spin 10s linear infinite;pointer-events:none;}
@keyframes spin{to{transform:rotate(360deg)}}
.vs-logo{position:relative;z-index:1;font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2.4rem,7vw,5rem);letter-spacing:.12em;
  background:linear-gradient(90deg,#fff,var(--cyan) 30%,var(--violet) 60%,var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 22px rgba(0,240,255,.45));animation:flicker 5s infinite;}
@keyframes flicker{0%,92%,100%{opacity:1}93%{opacity:.55}95%{opacity:1}96%{opacity:.7}}
.vs-greet{position:relative;z-index:1;font-size:clamp(1.05rem,2.6vw,1.45rem);font-weight:700;margin-top:.3rem;}
.vs-tagline{position:relative;z-index:1;color:var(--muted);margin-top:.2rem;}
.vs-boost{position:relative;z-index:1;display:inline-block;margin-top:1rem;padding:.55rem 1rem;border-radius:999px;font-size:.95rem;
  background:rgba(0,0,0,.35);border:1px solid rgba(255,43,214,.35);box-shadow:0 0 18px rgba(255,43,214,.18);}
.vs-moodline{font-family:'Orbitron',sans-serif;font-size:clamp(.9rem,2.2vw,1.1rem);color:var(--cyan);text-shadow:0 0 12px rgba(0,240,255,.6);
  margin:.4rem 0 .9rem;animation:rise .4s ease both;}

/* ── Section headers ───────────────────────────────────── */
.vs-section{display:flex;align-items:center;gap:.8rem;margin:2rem 0 .8rem;}
.vs-sec-icon{font-size:1.6rem;width:48px;height:48px;display:grid;place-items:center;border-radius:14px;
  background:linear-gradient(135deg,rgba(122,92,255,.35),rgba(0,240,255,.2));box-shadow:0 0 18px rgba(122,92,255,.35);}
.vs-sec-title{font-family:'Orbitron',sans-serif;font-weight:800;font-size:clamp(1.05rem,2.6vw,1.35rem);letter-spacing:.05em;}
.vs-sec-sub{color:var(--muted);font-size:.9rem;}

/* ── Card grid ─────────────────────────────────────────── */
.vs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:18px;margin-bottom:.6rem;}
.vs-card{position:relative;display:flex;flex-direction:column;border-radius:var(--radius);overflow:hidden;
  background:var(--glass);border:1px solid var(--glass-border);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  transition:transform .28s cubic-bezier(.2,.8,.2,1),box-shadow .28s,border-color .28s;animation:rise .5s ease both;}
.vs-card:hover{transform:translateY(-7px) scale(1.015);border-color:rgba(0,240,255,.6);
  box-shadow:0 14px 40px rgba(0,0,0,.45),0 0 26px rgba(0,240,255,.35),0 0 60px rgba(122,92,255,.25);}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

.vs-poster{position:relative;aspect-ratio:2/3;max-height:300px;width:100%;overflow:hidden;
  background:radial-gradient(circle at 30% 25%,rgba(255,255,255,.22),transparent 45%),linear-gradient(145deg,var(--c1),var(--c2));}
.vs-poster::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 4px);}
.vs-poster::after{content:"";position:absolute;top:0;left:-80%;width:50%;height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.28),transparent);transform:skewX(-18deg);transition:left .7s ease;}
.vs-card:hover .vs-poster::after,.vs-spotlight:hover .vs-poster::after{left:130%;}
.vs-emoji{position:absolute;top:44%;left:50%;transform:translate(-50%,-50%);font-size:4.4rem;filter:drop-shadow(0 6px 18px rgba(0,0,0,.5));transition:transform .35s;}
.vs-card:hover .vs-emoji{transform:translate(-50%,-55%) scale(1.15) rotate(-6deg);}
.vs-ptitle{position:absolute;left:0;right:0;bottom:0;padding:2.2rem .8rem .7rem;font-family:'Orbitron',sans-serif;font-weight:800;
  font-size:1rem;line-height:1.2;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.8);background:linear-gradient(180deg,transparent,rgba(5,3,15,.88));}
.vs-kind,.vs-live,.vs-status,.vs-tel{position:absolute;z-index:2;font-size:.66rem;font-weight:700;letter-spacing:.12em;padding:.22rem .55rem;border-radius:999px;backdrop-filter:blur(6px);}
.vs-kind{top:.6rem;left:.6rem;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.25);}
.vs-live{top:.6rem;right:.6rem;background:rgba(255,30,80,.85);display:flex;align-items:center;gap:.35rem;box-shadow:0 0 14px rgba(255,30,80,.7);}
.vs-live i{width:7px;height:7px;border-radius:50%;background:#fff;animation:blink 1s infinite;}
@keyframes blink{50%{opacity:.2}}
.vs-status{top:.6rem;right:.6rem;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.3);}
.vs-tel{top:2.2rem;left:.6rem;background:rgba(57,255,20,.18);border:1px solid rgba(57,255,20,.6);color:#c8ffbd;letter-spacing:.02em;}

.vs-body{display:flex;flex-direction:column;gap:.45rem;padding:.85rem .9rem 1rem;flex:1;}
.vs-title{font-weight:700;font-size:1rem;line-height:1.25;}
.vs-meta{color:var(--muted);font-size:.8rem;margin-top:-.25rem;}
.vs-tags{display:flex;flex-wrap:wrap;gap:.3rem;}
.vs-tag{font-size:.7rem;padding:.15rem .5rem;border-radius:999px;background:rgba(122,92,255,.18);border:1px solid rgba(122,92,255,.45);color:#d8d0ff;}
.vs-syn{margin:0;color:#cfcbef;font-size:.84rem;line-height:1.45;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;}
.vs-plat{font-size:.78rem;color:var(--muted);margin-top:auto;}
.vs-plat b{color:var(--cyan);font-weight:600;margin-right:.2rem;}
.vs-play{display:inline-flex;justify-content:center;align-items:center;gap:.3rem;padding:.55rem .8rem;border-radius:12px;font-weight:700;font-size:.85rem;
  text-decoration:none!important;color:#05040c!important;background:linear-gradient(90deg,var(--cyan),#7cf9ff);
  box-shadow:0 0 14px rgba(0,240,255,.45);transition:all .2s;}
.vs-play:hover{background:linear-gradient(90deg,var(--pink),var(--violet));color:#fff!important;box-shadow:0 0 22px rgba(255,43,214,.7);}
.vs-empty{padding:2rem;text-align:center;border-radius:var(--radius);background:var(--glass);border:1px dashed var(--glass-border);color:var(--muted);}

/* ── Spotlight (Surprise Me result) ────────────────────── */
.vs-spotlight{position:relative;margin:.6rem 0 1.4rem;padding:1rem;border-radius:24px;animation:pop .5s cubic-bezier(.2,1.4,.4,1) both;
  background:linear-gradient(var(--bg),var(--bg)) padding-box,linear-gradient(120deg,var(--pink),var(--violet),var(--cyan)) border-box;
  border:2px solid transparent;box-shadow:0 0 40px rgba(255,43,214,.35),0 0 80px rgba(0,240,255,.18);}
.vs-spot-label{font-family:'Orbitron',sans-serif;font-weight:800;letter-spacing:.2em;font-size:.8rem;color:var(--pink);text-shadow:0 0 10px var(--pink);margin-bottom:.7rem;}
.vs-spot-inner{display:grid;grid-template-columns:minmax(160px,240px) 1fr;gap:1.2rem;align-items:stretch;}
.vs-spot-inner .vs-poster{border-radius:16px;max-height:360px;}
.vs-spot-inner .vs-title{font-size:1.5rem;font-family:'Orbitron',sans-serif;}
.vs-spot-inner .vs-syn{font-size:1rem;}
.vs-spot-inner .vs-play{align-self:flex-start;padding:.7rem 1.4rem;font-size:1rem;}
.vs-spot-inner .vs-body{justify-content:center;}
.vs-spot-inner .vs-plat{margin-top:.6rem;}
@keyframes pop{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}
.vs-confetti{position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden;}
.vs-confetti i{position:absolute;top:-20px;width:9px;height:14px;border-radius:2px;opacity:0;animation:fall 2.2s ease-in forwards;}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(105vh) rotate(720deg)}}

/* ── Tracker ───────────────────────────────────────────── */
.vs-update{display:flex;gap:.6rem;align-items:flex-start;padding:.55rem .7rem;margin:.35rem 0;border-radius:12px;background:rgba(0,0,0,.25);border-left:3px solid var(--cyan);font-size:.9rem;}
.vs-update .d{color:var(--muted);font-size:.75rem;white-space:nowrap;padding-top:.1rem;}
.vs-utag{font-size:.68rem;font-weight:700;padding:.12rem .45rem;border-radius:999px;background:rgba(255,43,214,.2);border:1px solid rgba(255,43,214,.5);white-space:nowrap;}

/* ── Lounge ────────────────────────────────────────────── */
.vs-roomhead{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem;padding:1rem 1.2rem;border-radius:20px;margin-bottom:1rem;
  background:linear-gradient(120deg,rgba(122,92,255,.22),rgba(0,240,255,.08));border:1px solid var(--glass-border);}
.vs-roomname{font-family:'Orbitron',sans-serif;font-weight:800;font-size:1.25rem;}
.vs-code{font-family:'Orbitron',sans-serif;font-weight:900;letter-spacing:.3em;font-size:1.3rem;color:var(--cyan);text-shadow:0 0 14px var(--cyan);
  padding:.3rem .8rem;border:1px dashed rgba(0,240,255,.5);border-radius:12px;}
.vs-panel{padding:1rem;border-radius:var(--radius);background:var(--glass);border:1px solid var(--glass-border);backdrop-filter:blur(14px);}
.vs-chat{display:flex;flex-direction:column-reverse;gap:.55rem;height:420px;overflow-y:auto;padding:.8rem;border-radius:var(--radius);
  background:rgba(4,3,14,.55);border:1px solid var(--glass-border);scrollbar-width:thin;scrollbar-color:var(--violet) transparent;}
.vs-msg{display:flex;gap:.55rem;align-items:flex-end;max-width:88%;animation:rise .25s ease both;}
.vs-msg.mine{align-self:flex-end;flex-direction:row-reverse;}
.vs-av{flex:0 0 32px;height:32px;border-radius:50%;display:grid;place-items:center;font-weight:800;color:#05040c;background:var(--av);box-shadow:0 0 12px var(--av);}
.vs-bubble{padding:.5rem .75rem;border-radius:16px 16px 16px 4px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);}
.vs-msg.mine .vs-bubble{border-radius:16px 16px 4px 16px;background:linear-gradient(135deg,rgba(122,92,255,.35),rgba(0,240,255,.18));border-color:rgba(0,240,255,.3);}
.vs-mhead{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;font-size:.78rem;margin-bottom:.15rem;}
.vs-time{color:var(--muted);font-size:.7rem;}
.vs-mtext{font-size:.95rem;line-height:1.4;word-break:break-word;}
.vs-chip{font-size:.65rem;font-weight:700;padding:.1rem .45rem;border-radius:999px;border:1px solid;}
.vs-chip.hot{color:#ffb4a8;border-color:#ff6b35;background:rgba(255,107,53,.18);}
.vs-chip.spoiler{color:#ffe28a;border-color:#ffd60a;background:rgba(255,214,10,.14);}
.vs-chip.hype{color:#a8fbff;border-color:var(--cyan);background:rgba(0,240,255,.14);}
.vs-chip.elim{color:#ffb0e9;border-color:var(--pink);background:rgba(255,43,214,.16);}
.vs-spoiler{filter:blur(6px);cursor:pointer;transition:filter .25s;outline:none;}
.vs-spoiler:hover,.vs-spoiler:focus,.vs-spoiler:active{filter:none;}
.vs-sys{align-self:center;font-size:.78rem;color:var(--muted);padding:.2rem .7rem;border-radius:999px;background:rgba(255,255,255,.04);text-align:center;}
.vs-r{font-size:1.2rem;}
.vs-floaters{position:relative;height:0;}
.vs-floaters span{position:absolute;bottom:0;font-size:2rem;opacity:0;animation:floatUp 3s ease-out forwards;pointer-events:none;}
@keyframes floatUp{0%{opacity:0;transform:translateY(0) scale(.6)}15%{opacity:1;transform:translateY(-30px) scale(1.2)}100%{opacity:0;transform:translateY(-300px) scale(1)}}
.vs-members{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;}
.vs-online{width:100%;font-size:.8rem;color:var(--lime);text-shadow:0 0 8px rgba(57,255,20,.6);margin-bottom:.2rem;}
.vs-member{display:inline-flex;align-items:center;gap:.35rem;font-size:.8rem;padding:.2rem .6rem;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);opacity:.55;}
.vs-member i{width:8px;height:8px;border-radius:50%;background:#555;}
.vs-member.on{opacity:1;border-color:var(--av);}
.vs-member.on i{background:var(--lime);box-shadow:0 0 8px var(--lime);}
.vs-poll{display:flex;flex-direction:column;gap:.45rem;}
.vs-pollq{font-weight:700;margin-bottom:.2rem;}
.vs-pollrow{position:relative;display:flex;justify-content:space-between;align-items:center;padding:.55rem .75rem;border-radius:12px;overflow:hidden;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);font-size:.9rem;}
.vs-pollrow.lead{border-color:var(--cyan);box-shadow:0 0 14px rgba(0,240,255,.3);}
.vs-pollfill{position:absolute;inset:0 auto 0 0;background:linear-gradient(90deg,rgba(122,92,255,.45),rgba(0,240,255,.3));transition:width .6s cubic-bezier(.2,.8,.2,1);}
.vs-polllabel,.vs-pollpct{position:relative;z-index:1;}
.vs-pollpct{color:var(--muted);font-size:.8rem;white-space:nowrap;margin-left:.5rem;}

/* ── Responsive: Realme P1 5G & other phones ───────────── */
@media (max-width:640px){
  .block-container,[data-testid="stMainBlockContainer"]{padding-left:.75rem;padding-right:.75rem;padding-top:.8rem;}
  .vs-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
  .vs-emoji{font-size:3rem;}
  .vs-ptitle{font-size:.82rem;padding:1.6rem .55rem .5rem;}
  .vs-body{padding:.6rem .6rem .75rem;gap:.35rem;}
  .vs-title{font-size:.88rem;}
  .vs-card .vs-syn{font-size:.76rem;-webkit-line-clamp:2!important;}
  .vs-tag:nth-child(3){display:none;}
  .vs-play{font-size:.78rem;padding:.5rem .5rem;}
  .vs-card:hover{transform:none;}
  .vs-spot-inner{grid-template-columns:1fr;}
  .vs-spot-inner .vs-poster{max-height:260px;}
  .vs-hero{padding:1.5rem .8rem 1.2rem;border-radius:20px;}
  .vs-chat{height:360px;}
  .vs-msg{max-width:96%;}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
