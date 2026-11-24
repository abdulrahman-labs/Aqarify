import base64
from pathlib import Path

import streamlit as st

import auth
import session

st.set_page_config(
    page_title="تسجيل الدخول | Aqarify",
    page_icon=":material/login:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────── الأصول (Assets) ─────────────
# حط الصورة الأولى (المبنى بدون الكارت) هنا:  assets/login_bg.png
# (اختياري) اللوجو لوحده بخلفية شفافة:        assets/logo.png
ASSETS = Path(__file__).resolve().parent / "assets"
if not ASSETS.exists():  # لو الملف جوه فولدر pages/
    ASSETS = Path(__file__).resolve().parent.parent / "assets"


@st.cache_resource
def _b64(name: str) -> str | None:
    p = ASSETS / name
    if not p.exists():
        return None
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


bg = _b64("login_bg.png") or _b64("login_bg.jpg")
logo = _b64("logo.png")
bg_css = (f"background: url('{bg}') center / cover no-repeat fixed !important;"
          if bg else "background: #1b1712;")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Cairo:wght@400;600;700;800&display=swap');
    :root {{
        --ink:#14161C; --muted:#6B665A; --navy:#0F1626; --navy-2:#1B2539;
        --gold:#B8893A; --gold-soft:#D9B96F; --cream:#FBF7EF; --line:#E3DAC6; --line-strong:#CDBF9E;
    }}

    html, body, .stApp {{ direction: rtl; overflow-x: hidden; }}
    .stApp {{ {bg_css} color: var(--ink); }}
    [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ overflow-x: hidden; }}
    .stApp *:not(i):not([data-testid="stIconMaterial"]) {{ font-family: 'IBM Plex Sans Arabic', 'Cairo', sans-serif !important; }}
    .stApp .brand .name {{ font-family: 'Cairo', sans-serif !important; }}   /* الـ wordmark زي ما هو */
    [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"], #MainMenu, footer {{ display: none !important; }}
    [data-testid="InputInstructions"] {{ display: none !important; }}

    /* ===== حركات هادية ===== */
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes cardIn {{ from {{ opacity: 0; top: 18px; }} to {{ opacity: 1; top: 0; }} }}
    @keyframes bgShine {{ from {{ background-position: 100% 0; }} to {{ background-position: 0% 0; }} }}
    @keyframes pop {{ from {{ opacity: 0; transform: translateY(-4px); }} to {{ opacity: 1; transform: none; }} }}

    /* لمعة خفيفة بتروح وتيجي على الصورة بس (تحت الكارت) */
    [data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}
    .stApp::before {{
        content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background: linear-gradient(105deg, transparent 0%, transparent 38%, rgba(255,226,160,.05) 44%,
                    rgba(255,232,175,.15) 50%, rgba(255,226,160,.05) 56%, transparent 62%, transparent 100%);
        background-size: 300% 100%; background-position: 100% 0;
        mix-blend-mode: screen; animation: bgShine 10s ease-in-out infinite alternate;
    }}

    /* ===== الكارت (يمين الصفحة) ===== */
    /* ملاحظة: ممنوع transform/filter/backdrop-filter على الكارت نفسه، لأنها بتكسر العناصر الـ fixed اللي جواه */
    [data-testid="stMainBlockContainer"] {{
        position: relative; z-index: 10; top: 0;
        max-width: 350px; width: 350px;
        margin: 4vh 3vw 0 auto;
        padding: 22px 26px 20px !important;
        background: linear-gradient(180deg, rgba(255,255,255,.93) 0%, rgba(251,247,239,.90) 100%);
        border: 1px solid rgba(255,255,255,.6);
        border-radius: 24px;
        box-shadow: 0 34px 70px -22px rgba(8,10,18,.55), 0 12px 26px -14px rgba(8,10,18,.35),
                    inset 0 0 0 1px rgba(184,137,58,.30), inset 0 1px 0 rgba(255,255,255,.9);
        animation: cardIn .8s cubic-bezier(.2,.8,.2,1) backwards;
        transition: top .3s ease;
    }}
    [data-testid="stMainBlockContainer"]:hover:not(:has(.back-home:hover)):not(:has(.feat-bar:hover)) {{ top: -2px; }}
    [data-testid="stMainBlockContainer"]::before {{      /* تأثير زجاجي خفيف */
        content: ""; position: absolute; inset: 0; z-index: -1; border-radius: inherit; pointer-events: none;
        -webkit-backdrop-filter: blur(14px) saturate(120%); backdrop-filter: blur(14px) saturate(120%);
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: .6rem; }}
    .stApp [data-testid="stMarkdownContainer"] {{ direction: rtl !important; text-align: right !important; }}

    /* الهرمية: لوجو > عنوان > وصف */
    .brand {{ text-align: center !important; margin-bottom: 0; }}
    .brand img, .brand svg {{ display: block; margin: 0 auto 4px; height: 58px; width: auto; max-width: 100%; }}
    .brand .name {{ font-size: 27px; font-weight: 700; letter-spacing: .5px; line-height: 1.25; }}
    .welcome {{ text-align: center !important; font-size: 19px; font-weight: 700; line-height: 1.4; margin: 8px 0 0;
                color: var(--ink); animation: fadeUp .7s .15s backwards; }}
    .welcome-sub {{ text-align: center !important; color: var(--muted); font-size: 12.5px; font-weight: 400;
                    line-height: 1.6; margin-bottom: 10px; animation: fadeUp .7s .25s backwards; }}
    [data-testid="stForm"] {{ border: none !important; padding: 0 !important; animation: fadeUp .7s .35s backwards; }}

    /* ===== الحقول ===== */
    [data-testid="stTextInput"] [data-baseweb="input"] {{
        border: 1px solid var(--line) !important; border-radius: 12px !important;
        background: rgba(255,255,255,.92) !important; min-height: 42px;
        box-shadow: inset 0 1px 2px rgba(20,22,28,.04);
        transition: border-color .2s, box-shadow .2s;
    }}
    [data-testid="stTextInput"] [data-baseweb="input"] > div,
    [data-testid="stTextInput"] [data-baseweb="base-input"] {{ background: transparent !important; border: none !important; }}
    [data-testid="stTextInput"] [data-baseweb="input"]:hover {{ border-color: var(--line-strong) !important; }}
    [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {{
        border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(184,137,58,.15);
    }}
    [data-testid="stTextInput"] input {{
        direction: rtl; unicode-bidi: plaintext; text-align: start;
        height: 40px; font-size: 14px; font-weight: 500; line-height: 1.6; color: var(--ink);
        border: none !important; background-color: transparent !important;
        background-repeat: no-repeat; background-position: right 14px center; background-size: 18px;
        padding-inline-start: 44px !important; padding-inline-end: 8px !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{ color: #9B957F; opacity: 1; font-weight: 400; }}
    [data-testid="stTextInput"] input[aria-label="البريد الإلكتروني"] {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A38A55' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='5' width='18' height='14' rx='2.5'/%3E%3Cpath d='m3.5 7.5 8.5 6 8.5-6'/%3E%3C/svg%3E");
    }}
    [data-testid="stTextInput"] input[type="password"] {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A38A55' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='5' y='11' width='14' height='9' rx='2.5'/%3E%3Cpath d='M8 11V8a4 4 0 0 1 8 0v3'/%3E%3C/svg%3E");
    }}
    [data-testid="stTextInput"] input[aria-label="الاسم"] {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A38A55' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='3.6'/%3E%3Cpath d='M4.5 20c.9-3.6 3.9-5.5 7.5-5.5s6.6 1.9 7.5 5.5'/%3E%3C/svg%3E");
    }}
    /* أيقونة إظهار/إخفاء كلمة المرور (موحدة اللون مع باقي الأيقونات) */
    [data-testid="stTextInput"] [data-baseweb="input"] button {{
        background: transparent !important; border: none !important; box-shadow: none !important;
        color: #A38A55 !important; padding: 0 14px !important; height: 100%; min-height: 40px;
        transition: color .2s;
    }}
    [data-testid="stTextInput"] [data-baseweb="input"] button:hover {{ color: var(--gold) !important; }}
    [data-testid="stTextInput"] [data-baseweb="input"] button svg {{ width: 18px; height: 18px; }}

    /* ===== نسيت كلمة المرور ===== */
    .forgot-box {{ margin: 2px 0 12px; }}
    .forgot-box summary {{ line-height: 1.7; list-style: none; cursor: pointer; color: #9A7430; font-size: 13px; font-weight: 500;
                           display: inline-block; transition: color .2s; }}
    .forgot-box summary::-webkit-details-marker {{ display: none; }}
    .forgot-box summary:hover {{ color: var(--gold); text-decoration: underline; text-underline-offset: 3px; }}
    .forgot-msg {{ margin: 8px 0 4px; padding: 10px 12px; background: #FBF3E0; border: 1px solid #E8D6A8;
                   border-radius: 10px; color: #5A4412; font-size: 13px; font-weight: 500; line-height: 1.7;
                   animation: pop .3s ease; }}

    /* ===== الأزرار ===== */
    [data-testid="stBaseButton-primaryFormSubmit"] {{
        background: linear-gradient(180deg, var(--navy-2) 0%, var(--navy) 100%) !important;
        color: #F5EEDB !important; border: 1px solid rgba(201,162,75,.35) !important;
        height: 42px; border-radius: 12px; font-size: 15px; font-weight: 600;
        box-shadow: 0 12px 22px -10px rgba(10,14,28,.65), inset 0 1px 0 rgba(255,255,255,.08);
        transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease, background .2s ease;
    }}
    [data-testid="stBaseButton-primaryFormSubmit"] p {{ color: inherit !important; font-weight: 600; }}
    /* عكس أيقونة سهم الدخول لليسار لتتوافق مع RTL */
    [data-testid="stBaseButton-primaryFormSubmit"] [data-testid="stIconMaterial"],
    [data-testid="stBaseButton-primaryFormSubmit"] svg {{
        transform: scaleX(-1);
    }}
    [data-testid="stBaseButton-primaryFormSubmit"]:hover {{
        background: linear-gradient(180deg, #223049 0%, #121B2E 100%) !important;
        border-color: rgba(217,185,111,.7) !important; color: #fff !important;
        transform: translateY(-1px);
        box-shadow: 0 16px 26px -12px rgba(10,14,28,.7), inset 0 1px 0 rgba(255,255,255,.1);
    }}
    [data-testid="stBaseButton-primaryFormSubmit"]:active {{ transform: translateY(0); }}
    [data-testid="stBaseButton-secondary"] {{
        background: rgba(255,255,255,.7); color: var(--ink); border: 1px solid rgba(184,137,58,.5);
        height: 40px; border-radius: 12px; font-size: 14px; font-weight: 600;
        transition: background .2s, border-color .2s, transform .2s;
    }}
    [data-testid="stBaseButton-secondary"]:hover {{
        background: rgba(184,137,58,.08); border-color: var(--gold); color: var(--ink); transform: translateY(-1px);
    }}
    [data-testid="stBaseButton-primaryFormSubmit"]:focus-visible, [data-testid="stBaseButton-secondary"]:focus-visible {{
        outline: 2px solid var(--gold-soft); outline-offset: 2px;
    }}
    [data-testid="stAlert"] {{ border-radius: 12px; font-size: 13.5px; line-height: 1.7; }}

    .or-sep {{ display: flex; align-items: center; justify-content: center; gap: 12px;
               color: #7B7566; font-size: 12.5px; font-weight: 500; margin: 12px 0; }}
    .or-sep::before {{ content: ""; flex: 1; height: 1px; background: linear-gradient(270deg, var(--line-strong), transparent); }}
    .or-sep::after  {{ content: ""; flex: 1; height: 1px; background: linear-gradient(90deg,  var(--line-strong), transparent); }}

    /* ===== زر العودة للرئيسية (هادي وغير منافس للكارت) ===== */
    .back-home {{
        position: fixed; top: 24px; left: 24px; z-index: 50;
        display: flex; align-items: center; gap: 8px;
        padding: 7px 15px; border-radius: 999px;
        background: rgba(12,16,28,.45); border: 1px solid rgba(255,255,255,.16);
        -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
        color: rgba(255,255,255,.9) !important; font-size: 13px; font-weight: 500; text-decoration: none;
        transition: background .2s, border-color .2s, color .2s;
    }}
    .stApp a.back-home, .stApp a.back-home:hover {{ text-decoration: none !important; }}
    .stApp a.back-home:hover {{ background: rgba(12,16,28,.72); border-color: rgba(217,185,111,.6); color: #fff !important; }}
    .back-home:focus-visible {{ outline: 2px solid var(--gold-soft); outline-offset: 2px; }}
    .back-home svg {{ width: 15px; height: 15px; fill: currentColor; opacity: .9; }}

    /* ===== الشريط السفلي (بخلفية زجاجية خفيفة) ===== */
    .feat-bar {{
        position: fixed; left: 0; bottom: 2.5vh; z-index: 40;
        width: calc(97vw - 370px); height: 78px;
        display: flex; align-items: center; direction: rtl; padding: 0 26px;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(18,15,10,.48) 0%, rgba(12,10,7,.62) 100%);
        border: 1px solid rgba(240,200,110,.22);
        box-shadow: 0 14px 32px -12px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,236,190,.14);
        -webkit-backdrop-filter: blur(10px) saturate(120%); backdrop-filter: blur(10px) saturate(120%);
        animation: fadeUp .7s .45s backwards;
    }}
    .feat {{
        position: relative; flex: 1; height: 50px; padding: 0 10px; cursor: default; border-radius: 12px;
        display: flex; align-items: center; justify-content: center; gap: 10px;
        transition: transform .3s ease;
    }}
    .feat + .feat::before {{      /* فاصل ذهبي بيخفت من الأطراف */
        content: ""; position: absolute; right: 0; top: -6px; bottom: -6px; width: 1px;
        background: linear-gradient(180deg, transparent, rgba(240,200,110,.85), transparent);
    }}
    .feat .ft {{ text-align: right; }}
    .feat .t1 {{ color: #F8DA85; font-size: 13.5px; font-weight: 700; line-height: 1.5; letter-spacing: .1px;
                 text-shadow: 0 1px 2px rgba(0,0,0,.95), 0 2px 10px rgba(0,0,0,.85), 0 0 16px rgba(232,190,98,.22);
                 transition: color .3s, text-shadow .3s; }}
    .feat .t2 {{ color: #F0E0B4; font-size: 11px; font-weight: 500; line-height: 1.5;
                 text-shadow: 0 1px 2px rgba(0,0,0,.95), 0 2px 8px rgba(0,0,0,.8); }}
    .feat .ic {{
        width: 40px; height: 40px; flex: none; border-radius: 50%; display: grid; place-items: center;
        background: radial-gradient(circle at 50% 28%, rgba(70,52,22,.92), rgba(18,13,7,.92));
        border: 1.5px solid rgba(240,200,110,.85);
        box-shadow: 0 0 14px rgba(232,190,98,.35), 0 6px 14px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,236,190,.35);
        transition: transform .45s cubic-bezier(.2,.8,.2,1), box-shadow .3s;
    }}
    .feat svg {{ width: 22px; height: 22px; stroke: #F8DA85; fill: none; stroke-width: 1.6;
                 stroke-linecap: round; stroke-linejoin: round; filter: drop-shadow(0 0 4px rgba(232,190,98,.55)); }}
    .feat:hover {{ transform: translateY(-3px); }}
    .feat:hover .t1 {{ color: #FFE9A8; text-shadow: 0 1px 2px rgba(0,0,0,.95), 0 2px 10px rgba(0,0,0,.85), 0 0 18px rgba(232,190,98,.6); }}
    .feat:hover .ic {{ transform: rotate(-8deg) scale(1.1); box-shadow: 0 0 24px rgba(232,190,98,.65), 0 6px 14px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,236,190,.4); }}

    @media (prefers-reduced-motion: reduce) {{
        .stApp::before, [data-testid="stMainBlockContainer"], .welcome, .welcome-sub,
        [data-testid="stForm"], .feat-bar {{ animation: none !important; }}
        * {{ transition-duration: .01ms !important; }}
    }}

    /* ===== تابلت أفقي / لابتوب صغير ===== */
    @media (max-width: 1100px) {{
        [data-testid="stMainBlockContainer"] {{ width: 330px; max-width: 330px; margin-right: 2.5vw; }}
        .feat-bar {{ width: calc(97vw - 350px); padding: 0 14px; }}
        .feat {{ gap: 10px; padding: 0 6px; }}
        .feat .t2 {{ display: none; }}
        .feat .t1 {{ font-size: 12.5px; }}
        .feat .ic {{ width: 36px; height: 36px; }} .feat svg {{ width: 20px; height: 20px; }}
    }}

    /* ===== تابلت عمودي + موبايل ===== */
    @media (max-width: 900px) {{
        .stApp {{ background-position: 28% 35% !important; background-attachment: scroll !important; }}
        [data-testid="stMainBlockContainer"] {{
            width: min(92vw, 440px) !important; max-width: min(92vw, 440px) !important;
            margin: 84px auto 150px !important; padding: 26px 20px 22px !important;
        }}
        .back-home {{ top: calc(14px + env(safe-area-inset-top, 0px)); left: 14px; }}
        .feat-bar {{ left: 0; right: 0; width: auto; bottom: 0; height: calc(88px + env(safe-area-inset-bottom, 0px));
                     padding: 0 6px env(safe-area-inset-bottom, 0px);
                     border-radius: 18px 18px 0 0;
                     background: linear-gradient(0deg, rgba(14,10,6,.85), rgba(14,10,6,.45)); }}
        .feat {{ flex-direction: column; gap: 4px; height: auto; padding: 0 4px; }}
        .feat .ft {{ text-align: center; }}
        .feat .t1 {{ font-size: 11.5px; line-height: 1.4; }}
        .feat .ic {{ width: 38px; height: 38px; }}
        .feat svg {{ width: 21px; height: 21px; }}
    }}
    @media (max-width: 380px) {{
        .brand .name {{ font-size: 28px; }}
        .welcome {{ font-size: 19px; }}
        .feat .t1 {{ font-size: 10.5px; }}
    }}
    @media (max-height: 560px) and (orientation: landscape) {{
        .feat-bar {{ display: none; }}
        [data-testid="stMainBlockContainer"] {{ margin-bottom: 24px !important; }}
    }}
</style>

<a class="back-home" href="/" target="_self">
    <span>العودة للرئيسية</span>
    <svg viewBox="0 0 24 24"><path d="M12 3 2 12h3v9h6v-6h2v6h6v-9h3z"/></svg>
</a>

<div class="feat-bar">
    <div class="feat"><div class="ft"><div class="t1">أكبر مجموعة من العقارات</div><div class="t2">خيارات متنوعة تناسب احتياجاتك</div></div><span class="ic"><svg viewBox="0 0 24 24"><path d="M5 21V8.5L12 4l7 4.5V21"/><path d="M3 21h18"/><path d="M9.5 21v-5.5h5V21"/><path d="M9.5 11.5h1M13.5 11.5h1"/></svg></span></div>
    <div class="feat"><div class="ft"><div class="t1">دعم فني على مدار الساعة</div><div class="t2">نحن دائماً في خدمتك</div></div><span class="ic"><svg viewBox="0 0 24 24"><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="13" width="4" height="6" rx="1.6"/><rect x="17" y="13" width="4" height="6" rx="1.6"/><path d="M20 19c0 1.6-1.6 2.4-4.5 2.4"/></svg></span></div>
    <div class="feat"><div class="ft"><div class="t1">أمان وموثوقية في كل خطوة</div><div class="t2">بياناتك في أيدٍ أمينة</div></div><span class="ic"><svg viewBox="0 0 24 24"><path d="M12 3 4.5 6v5.5c0 4.4 3.1 7.9 7.5 9.5 4.4-1.6 7.5-5.1 7.5-9.5V6z"/><path d="m8.8 12 2.4 2.4 4-4.4"/></svg></span></div>
</div>
""", unsafe_allow_html=True)

# ───────────── الكارت ─────────────
LOGO_SVG = (
    '<svg viewBox="0 0 120 80" fill="none" stroke="#B8893A" stroke-width="3.2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M22 40 60 6l38 34"/><path d="M30 40 60 14l30 26"/>'
    '<path d="M24 74V46M36 74V34M48 74V28M60 74V40"/>'
    '<path d="M70 74V44h24v30M70 74h24"/><path d="M78 56h8v8h-8z"/>'
    '</svg>'
)
brand = (f'<img src="{logo}" alt="Aqarify">' if logo else LOGO_SVG) + '<div class="name">Aqarify</div>'
st.markdown(f'<div class="brand">{brand}</div>', unsafe_allow_html=True)

user = session.current_user()
if user:
    st.success(f"أنت مسجّل دخول باسم {user['name']} "
               f"({'أدمن' if user['role'] == 'admin' else 'شركة' if user['role'] == 'company' else 'مستخدم'}).")
    c1, c2 = st.columns(2)
    if c1.button("الرئيسية", width="stretch"):
        st.switch_page("App.py")
    if c2.button("تسجيل الخروج", width="stretch"):
        session.logout_user()
        st.rerun()
    st.stop()

st.session_state.setdefault("auth_mode", "login")

if st.session_state.auth_mode == "login":
    st.markdown('<div class="welcome">مرحباً بعودتك!</div>'
                '<div class="welcome-sub">سجِّل الدخول لمتابعة رحلتك العقارية</div>',
                unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="البريد الإلكتروني",
                              label_visibility="collapsed")
        password = st.text_input("كلمة المرور", type="password", placeholder="كلمة المرور",
                                 label_visibility="collapsed")
        st.markdown('<details class="forgot-box"><summary>نسيت كلمة المرور؟</summary>'
                    '<div class="forgot-msg">تواصل مع الدعم الفني لإعادة ضبط كلمة المرور.</div></details>',
                    unsafe_allow_html=True)
        go = st.form_submit_button("تسجيل الدخول", type="primary", width="stretch", icon=":material/login:")

    if go:
        wait = auth.lock_remaining(email)
        if wait > 0:
            st.error(f"محاولات كثيرة. جرّب بعد {wait} ثانية.")
        else:
            u = auth.authenticate(email, password)
            if u:
                auth.clear_failures(email)
                session.login_user(u)
                st.switch_page("App.py")
            else:
                auth.register_failure(email)
                st.error("البريد أو كلمة المرور غير صحيحة.")

    st.markdown('<div class="or-sep">أو</div>', unsafe_allow_html=True)
    if st.button("إنشاء حساب", width="stretch", key="to_register", icon=":material/person_add:"):
        st.session_state.auth_mode = "register"
        st.rerun()

else:
    st.markdown('<div class="welcome">أهلاً بك في Aqarify</div>'
                '<div class="welcome-sub">أنشئ حسابك وابدأ رحلتك العقارية</div>',
                unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=True):
        r_name = st.text_input("الاسم", placeholder="الاسم", label_visibility="collapsed")
        r_email = st.text_input("البريد الإلكتروني", key="r_email", placeholder="البريد الإلكتروني",
                                label_visibility="collapsed")
        r_pw1 = st.text_input("كلمة المرور", type="password", key="r_pw1",
                              placeholder="كلمة المرور (8 أحرف على الأقل)", label_visibility="collapsed")
        r_pw2 = st.text_input("أعد كتابة كلمة المرور", type="password", key="r_pw2",
                              placeholder="أعد كتابة كلمة المرور", label_visibility="collapsed")
        reg = st.form_submit_button("إنشاء حساب", type="primary", width="stretch")

    if reg:
        if r_pw1 != r_pw2:
            st.error("كلمتا المرور غير متطابقتين.")
        else:
            # التسجيل العام دايماً role=user، الأدمن بيتعمل من الـ Terminal بس
            ok, msg = auth.create_user(r_name, r_email, r_pw1, role="user")
            (st.success if ok else st.error)(msg + (" سجّل دخولك من الزر بالأسفل." if ok else ""))

    st.markdown('<div class="or-sep">أو</div>', unsafe_allow_html=True)
    if st.button("عندي حساب بالفعل", width="stretch", key="to_login"):
        st.session_state.auth_mode = "login"
        st.rerun()