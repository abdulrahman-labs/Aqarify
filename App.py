import streamlit as st

st.set_page_config(
    page_title="Aqarify | بيتك القادم يبدأ من هنا",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False

import session
session.restore_login()  # يرجّع تسجيل الدخول بعد Refresh

import db
from utils import EMBLEMS, build_logo_registry, company_tag, esc, norm, safe, set_branding

# العقارات المميزة في الصفحة الرئيسية (بالترتيب ده)
FEATURED_TITLES = [
    "تاون هاوس راقٍ في أمواج",
    "شقة جاهزة للسكن في ماونتن بارك",
    "استوديو فاخر في كابيتال جاردنز",
]


@st.cache_data
def _home_data(version):
    """العقارات المميزة (محددة بالاسم) + أرقام وشركاء الصفحة."""
    items = db.list_properties_legacy()

    by_title = {norm(p["title"]).strip(): p for p in items}
    picked = [by_title[k] for k in (norm(t).strip() for t in FEATURED_TITLES) if k in by_title]

    # احتياطي: لو وحدة اتحذفت أو اتغير اسمها، نكمّل بأغلى الوحدات الجاهزة عشان الكروت تفضل 3
    if len(picked) < 3:
        pool = sorted([p for p in items if p["status"] == "جاهز للتسليم"] or items, key=lambda p: -p["price_val"])
        picked += [p for p in pool if p not in picked][:3 - len(picked)]

    named = {(p.get("company_id") or 0, p["company_name"]) for p in items if p.get("company_name")}
    counts = {}
    for p in items:
        if p.get("company_name"):
            counts[p["company_name"]] = counts.get(p["company_name"], 0) + 1
    return {
        "counts": counts, "picked": picked, "units": len(items), "cities": len({p["city"] for p in items}),
        "partners": sorted({n for _, n in named}),
        "registry": build_logo_registry(tuple(sorted(named))),   # نفس توزيع شعارات المعرض
        "logos": {p["company_name"]: p["company_logo"] for p in items if p.get("company_name") and p.get("company_logo")},
    }


EMPTY = {"counts": {}, "picked": [], "units": 0, "cities": 0, "partners": [], "registry": {}, "logos": {}}
data = _home_data(db.properties_version()) if db.DB_FILE.exists() else EMPTY
set_branding(data["registry"], data["logos"])

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    :root { --color-dark:#14161C; --color-white:#FFFFFF; --color-accent:#C9A24B; --color-bg:#FAFAF8;
            --color-border:#E4E2DA; --color-text-muted:#666666; }

    html, body, .stApp { direction: rtl; }
    .stApp { color: var(--color-dark); background-color: var(--color-bg);
        background-image: radial-gradient(circle at 8% 6%, rgba(201,162,75,.09), transparent 26%),
                          radial-gradient(circle at 95% 45%, rgba(20,22,28,.03), transparent 22%); }
    .stApp [data-testid="stMarkdownContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp *:not(i):not([data-testid="stIconMaterial"]) { font-family: 'Cairo', sans-serif !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 7rem; max-width: 1280px; }

    /* ─── الشعار والتنقل (نفس معرض العقارات بالظبط) ─── */
    .brand-logo-link { display: inline-flex; align-items: center; gap: 14px; }
    .brand-icon-box { background: var(--color-dark); color: var(--color-accent); width: 52px; height: 52px;
        border-radius: 14px; border: 1px solid var(--color-dark); box-shadow: 0 6px 16px rgba(20,22,28,.18);
        display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
    .brand-logo-text { font-size: 34px; font-weight: 800; line-height: 1; }
    .brand-logo-dot { color: var(--color-accent); }
    .brand-logo-sub { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; display: block; }

    .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: wrap;
        justify-content: flex-end; align-items: center; gap: 22px !important; padding-top: 14px; }
    .st-key-topnav [data-testid="stElementContainer"],
    .st-key-topnav [data-testid="stPageLink"] { width: auto !important; flex: 0 0 auto !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"] { position: relative; display: inline-flex !important;
        align-items: center; gap: 8px; background: transparent !important; padding: 8px 0 !important;
        border-radius: 0 !important; color: var(--color-dark) !important; text-decoration: none !important;
        transition: color .2s ease; }
    .st-key-topnav [data-testid="stPageLink-NavLink"] p { font-size: 16px !important; font-weight: 700 !important;
        color: inherit !important; margin: 0 !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]::before { font-family: "Font Awesome 6 Free" !important;
        font-weight: 900 !important; font-size: 15px; width: 18px; text-align: center; content: "\\f015"; }
    .st-key-topnav [href*="Properties"]::before { content: "\\f64f" !important; }
    .st-key-topnav [href*="Customer"]::before   { content: "\\f508" !important; }
    .st-key-topnav [href*="Calculator"]::before { content: "\\f1ec" !important; }
    .st-key-topnav [href*="Admin"]::before      { content: "\\f1de" !important; }
    .st-key-topnav [href*="Company"]::before    { content: "\\f1ad" !important; }
    .st-key-topnav [href*="Login"]::before      { content: "\\f2f6" !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]:hover { color: var(--color-accent) !important; }
    /* الصفحة الحالية = الرئيسية */
    .st-key-topnav [data-testid="stPageLink-NavLink"]:not(:is([href*="Properties"],[href*="Customer"],[href*="Calculator"],[href*="Admin"],[href*="Login"],[href*="Company"])) { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]:not(:is([href*="Properties"],[href*="Customer"],[href*="Calculator"],[href*="Admin"],[href*="Login"],[href*="Company"]))::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent); }

    /* ─── الهيرو ─── */
    .hero-title { font-size: clamp(28px, 2.8vw, 40px); font-weight: 800; line-height: 1.35; letter-spacing: -.6px; }
    .hero-title span { color: var(--color-accent); }
    .hero-sub { font-size: 16px; font-weight: 700; letter-spacing: 1px; color: var(--color-accent); margin: 8px 0 16px; }
    .hero-desc { max-width: 560px; font-size: 16px; line-height: 2; color: var(--color-text-muted); margin-bottom: 24px; }
    .hero-stats { display: flex; gap: 14px; margin-top: 22px; }
    .hero-stats > div { flex: 1; background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 16px; padding: 12px 16px; box-shadow: 0 4px 14px rgba(20,22,28,.04); }
    .hero-stats b { display: block; font-size: 24px; font-weight: 800; line-height: 1.2; }
    .hero-stats span { font-size: 13px; color: var(--color-text-muted); font-weight: 600; }
    .hero-img-box { position: relative; border-radius: 24px; overflow: hidden; border: 1px solid var(--color-border);
        box-shadow: 0 18px 44px rgba(20,22,28,.13); }
    .hero-img-box img { width: 100%; height: 440px; object-fit: cover; display: block; transition: transform .8s ease; }
    .hero-img-box:hover img { transform: scale(1.035); }
    .hero-img-box::after { content: ""; position: absolute; inset: 0; pointer-events: none;
        background: linear-gradient(180deg, transparent 55%, rgba(20,22,28,.28)); }
    .float-card { position: absolute; z-index: 2; bottom: 20px; right: 20px; display: flex; align-items: center; gap: 14px;
        background: rgba(255,255,255,.95); backdrop-filter: blur(10px); border: 1px solid rgba(201,162,75,.35);
        border-radius: 16px; padding: 12px 18px; box-shadow: 0 10px 28px rgba(0,0,0,.14); }
    .float-card i { font-size: 24px; color: var(--color-accent); }
    .float-card b { display: block; font-size: 16px; font-weight: 800; }
    .float-card span { font-size: 13px; color: var(--color-text-muted); }

    /* ─── الأزرار ─── */
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
        min-height: 50px; font-weight: 700; border-radius: 12px; transition: all .2s ease; }
    [data-testid="stBaseButton-secondary"] { background: var(--color-white); color: var(--color-dark);
        border: 1px solid rgba(20,22,28,.35); }
    [data-testid="stBaseButton-secondary"]:hover { background: var(--color-dark); color: var(--color-white);
        border-color: var(--color-dark); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(20,22,28,.18); }
    [data-testid="stBaseButton-primary"] { background: linear-gradient(135deg, #DCC17E, #C9A24B);
        color: var(--color-dark); border: 1px solid rgba(171,130,49,.4); box-shadow: 0 5px 15px rgba(201,162,75,.22); }
    [data-testid="stBaseButton-primary"]:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(201,162,75,.45);
        color: var(--color-dark); border-color: var(--color-accent); }

    /* ─── الأقسام والكروت ─── */
    .sec-title { text-align: center; font-size: 32px; font-weight: 800; margin: 84px 0 30px; }
    .sec-title::after { content: ""; display: block; width: 46px; height: 3px; border-radius: 4px;
        background: var(--color-accent); margin: 12px auto 0; }
    .sec-sub { text-align: center; color: var(--color-text-muted); font-size: 16px; margin: -18px 0 30px; }
    .card { position: relative; overflow: hidden; height: 100%; background: var(--color-white);
        border: 1px solid var(--color-border); border-radius: 20px; padding: 26px 22px;
        box-shadow: 0 5px 18px rgba(20,22,28,.035); transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease; }
    .card:hover { transform: translateY(-4px); box-shadow: 0 14px 30px rgba(20,22,28,.08); border-color: var(--color-accent); }
    .card::before { content: ""; position: absolute; top: 0; right: 24px; width: 42px; height: 3px;
        border-radius: 0 0 4px 4px; background: var(--color-accent); transition: width .3s ease; }
    .card:hover::before { width: 76px; }
    .center { text-align: center; }
    .card .t { font-size: 19px; font-weight: 800; margin-bottom: 8px; }
    .card .d { font-size: 15px; line-height: 1.9; color: var(--color-text-muted); }
    .ico { display: grid; place-items: center; width: 58px; height: 58px; margin: 0 auto 14px; border-radius: 18px;
        background: rgba(201,162,75,.13); color: var(--color-accent); font-size: 24px; }
    .num { display: grid; place-items: center; width: 48px; height: 48px; margin: 0 auto 14px; border-radius: 50%;
        background: var(--color-accent); color: var(--color-dark); font-size: 20px; font-weight: 800;
        border: 4px solid rgba(201,162,75,.18); box-sizing: content-box; }
    .stars { color: var(--color-accent); font-size: 12px; letter-spacing: 2px; margin-bottom: 10px; }
    .quote { font-size: 15px; line-height: 1.9; color: var(--color-text-muted); margin-bottom: 14px; }
    .quote::before { content: "\\201C"; display: block; font: 700 36px/0.8 Georgia, serif; color: rgba(201,162,75,.6); }

    .partners-panel { position: relative; overflow: hidden; padding: 30px 0; border: 1px solid var(--color-border);
        border-radius: 28px; background: linear-gradient(180deg, #FFFEFB, #F8F4EA); box-shadow: 0 10px 30px rgba(20,22,28,.04); }
    .partners-panel::before, .partners-panel::after { content: ""; position: absolute; width: 300px; height: 300px;
        border-radius: 50%; pointer-events: none; background: radial-gradient(circle, rgba(201,162,75,.16), transparent 70%); }
    .partners-panel::before { top: -140px; right: -90px; }
    .partners-panel::after { bottom: -150px; left: -90px; }
    .marq { direction: ltr; overflow: hidden; padding: 8px 0; -webkit-mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent);
        mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent); }
    .marq .track { display: flex; width: max-content; animation: marq var(--d, 40s) linear infinite; }
    .marq.rev .track { animation-direction: reverse; }
    .partners-panel:hover .track { animation-play-state: paused; }
    @keyframes marq { to { transform: translateX(-50%); } }
    .partner { direction: rtl; display: flex; align-items: center; gap: 12px; margin-right: 16px; padding: 8px 22px 8px 8px;
        background: rgba(255,255,255,.85); border: 1px solid rgba(201,162,75,.22); border-radius: 999px; white-space: nowrap;
        box-shadow: 0 3px 12px rgba(20,22,28,.03); transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease; }
    .partner:hover { transform: translateY(-4px); border-color: var(--color-accent); box-shadow: 0 12px 26px rgba(201,162,75,.22); }
    .partner b { display: block; font-size: 14.5px; font-weight: 700; line-height: 1.4; }
    .partner span { display: block; font-size: 12px; font-weight: 600; color: #9A7B34; }
    .p-ico { width: 46px; height: 46px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center; overflow: hidden;
        background: linear-gradient(145deg, #FFFEFA, #F4ECD6); border: 1px solid rgba(201,162,75,.28); }
    .p-ico svg { width: 26px; height: 26px; }
    .p-ico img { width: 100%; height: 100%; object-fit: contain; padding: 7px; box-sizing: border-box; background: #fff; }

    .prop { padding: 0; }
    .prop::before { display: none; }
    .prop-img { position: relative; height: 210px; background-size: cover; background-position: center;
        background-color: var(--color-border); transition: transform .6s ease; }
    .prop-wrap { overflow: hidden; }
    .prop:hover .prop-img { transform: scale(1.05); }
    .prop .tag { position: absolute; top: 14px; right: 14px; background: rgba(20,22,28,.78); color: var(--color-accent);
        padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 800; border: 1px solid rgba(201,162,75,.35); }
    .prop-body { position: relative; background: var(--color-white); padding: 18px; }
    .prop .t { font-size: 17px; margin-bottom: 6px; }
    .muted { font-size: 14px; color: var(--color-text-muted); }
    .specs { display: flex; gap: 16px; font-size: 13px; font-weight: 700; margin: 12px 0; padding: 10px 0;
        border-block: 1px dashed var(--color-border); }
    .specs i { color: var(--color-accent); margin-inline-end: 5px; }
    .price { font-size: 21px; font-weight: 800; color: var(--color-accent); }
    .company-bar { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: #FBFAF6;
        border-bottom: 1px solid var(--color-border); font-size: 13px; font-weight: 700; }
    .company-bar i { color: var(--color-accent); }

    .cta { position: relative; overflow: hidden; isolation: isolate; text-align: center; background: var(--color-dark);
        border: 1px solid rgba(201,162,75,.28); border-radius: 24px; padding: 46px 28px; margin: 84px 0 24px;
        box-shadow: 0 14px 34px rgba(20,22,28,.12); }
    .cta::before, .cta::after { content: ""; position: absolute; z-index: -1; border: 1px solid rgba(201,162,75,.22);
        border-radius: 50%; width: 260px; height: 260px; }
    .cta::before { right: -95px; top: -150px; }
    .cta::after { left: -130px; bottom: -190px; width: 320px; height: 320px; }
    .cta .t { font-size: 32px; font-weight: 800; color: var(--color-white); margin-bottom: 10px; }
    .cta .d { font-size: 17px; color: #CCCCCC; }

    .foot-t { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
    .foot-p { font-size: 15px; color: var(--color-text-muted); line-height: 1.8; margin-bottom: 6px; }
    .foot-p i { margin-inline-end: 6px; }
    .copy { text-align: center; font-size: 14px; color: var(--color-text-muted); padding: 6px 0 20px; }

    @media (max-width: 1100px) { .st-key-topnav [data-testid="stPageLink-NavLink"] p { font-size: 14px !important; } }
    @media (max-width: 768px) {
        .block-container { padding: 5rem 1rem 1rem !important; max-width: 100% !important; }
        .brand-logo-text { font-size: 26px; }
        .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] { justify-content: center !important; gap: 12px !important; }
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 10px !important; }
        .hero-img-box img { height: 290px; }
        .hero-stats b { font-size: 20px; }
        .sec-title { font-size: 26px; margin-top: 56px; }
        .cta { padding: 32px 18px; margin-top: 56px; }
    }
    @media (prefers-reduced-motion: reduce) { * { transition: none !important; } .marq .track { animation: none; flex-wrap: wrap; width: auto; justify-content: center; } }
</style>
""", unsafe_allow_html=True)

# ─── مسار الشعار ───
import base64, os
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "assets", "logo.png")
with open(LOGO_PATH, "rb") as _f:
    LOGO_B64 = base64.b64encode(_f.read()).decode()
HERO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "assets", "hero.jpg")
with open(HERO_PATH, "rb") as _f:
    HERO_B64 = base64.b64encode(_f.read()).decode()

# ─── الهيدر (نفس معرض العقارات: الشعار أقصى اليمين) ───
col_logo, col_nav = st.columns([1.1, 3])
with col_logo:
    st.markdown(f"""
    <div class="brand-logo-link">
        <img src="data:image/png;base64,{LOGO_B64}" alt="Aqarify" style="height:52px;width:auto;flex-shrink:0;">
        <div>
            <div class="brand-logo-text">Aqarify<span class="brand-logo-dot">.</span></div>
            <span class="brand-logo-sub">بيتك القادم يبدأ من هنا</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    with st.container(key="topnav"):
        st.page_link("App.py", label="الرئيسية")
        st.page_link("pages/Properties.py", label="معرض العقارات")
        st.page_link("pages/Customer Service.py", label="المستشار الذكي")
        st.page_link("pages/Calculator.py", label="حاسبة التمويل")
        if st.session_state.get("is_admin_logged_in", False):
            st.page_link("pages/Admin.py", label="لوحة الإدارة")
        if (st.session_state.get("user") or {}).get("role") == "company":
            st.page_link("pages/Company.py", label="لوحة الشركة")
        st.page_link("pages/Login.py", label="حسابي" if st.session_state.get("user") else "تسجيل الدخول")

# ─── التوجيه عبر الرابط (Routing) ───
if "page" in st.query_params:
    page = st.query_params["page"]
    del st.query_params["page"]
    if page == "props":
        st.switch_page("pages/Properties.py")
    elif page == "chat":
        st.switch_page("pages/Customer Service.py")
    elif page == "calc":
        st.switch_page("pages/Calculator.py")
    elif page == "admin" and st.session_state.get("is_admin_logged_in", False):
        st.switch_page("pages/Admin.py")

st.markdown("<hr style='margin: 10px 0 30px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f"<div class='sec-title'>{title}</div>" + (f"<div class='sec-sub'>{sub}</div>" if sub else ""),
                unsafe_allow_html=True)


# ─── الهيرو ───
col_text, col_img = st.columns([1.2, 1], gap="large", vertical_alignment="center")
with col_text:
    st.markdown(
        "<div class='hero-title'>مستقبل السكن العقاري <span>الذكي</span></div>"
        "<div class='hero-sub'>Future of Modern Living</div>"
        "<div class='hero-desc'>نقدم لك أرقى المجتمعات السكنية والوحدات الفاخرة، مع تجربة استشارة فورية معززة "
        "بالذكاء الاصطناعي لاختيار العقار المالي والسكني الأمثل لك ولأسرتك.</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    if b1.button("تحدث مع المستشار الذكي", key="hero_chat", type="primary", icon=":material/support_agent:", width="stretch"):
        st.switch_page("pages/Customer Service.py")
    if b2.button("استكشف المعرض", key="hero_explore", icon=":material/apartment:", width="stretch"):
        st.switch_page("pages/Properties.py")
    st.markdown("<div class='hero-stats'>" + "".join(
        f"<div><b>{n}</b><span>{lb}</span></div>" for n, lb in
        ((data["units"], "وحدة متاحة"), (len(data["partners"]), "شركة شريكة"), (data["cities"], "منطقة"))
    ) + "</div>", unsafe_allow_html=True)

with col_img:
    st.markdown(
        '<div class="hero-img-box"><img src="data:image/jpeg;base64,' + HERO_B64 + '" alt="Aqarify Architecture">'
        '<div class="float-card"><i class="fa-solid fa-shield-halved"></i>'
        '<div><b>شركاء موثوقون</b><span>استثمار سكني آمن ومعتمد</span></div></div></div>', unsafe_allow_html=True)

# ─── لماذا نحن ───
section("لماذا نحن؟")
features = [
    ("fa-headset", "مستشار ذكي 24/7", "إجابات فورية واستشارات دقيقة مجهزة بالذكاء الاصطناعي على مدار الساعة."),
    ("fa-file-contract", "عقود موثقة", "ضمان قانوني كامل لكافة المعاملات العقارية لضمان استثمارك بشكل آمن."),
    ("fa-gem", "تشطيبات فاخرة", "اختيارات حصرية من أفضل الوحدات ذات التشطيب المودرن والأولتر ألوكس."),
    ("fa-calculator", "تمويل مرن", "خطط سداد وأقساط مريحة تناسب مختلف الميزانيات بدفعات مقدمة بسيطة."),
]
for col, (ic, t, d) in zip(st.columns(4), features):
    col.markdown(f'<div class="card center"><div class="ico"><i class="fa-solid {ic}"></i></div>'
                 f'<div class="t">{t}</div><div class="d">{d}</div></div>', unsafe_allow_html=True)

# ─── كيف يعمل ───
section("كيف يعمل Aqarify؟")
steps = [
    ("1", "اسأل المستشار", "ناقش متطلباتك وميزانيتك مع مستشارنا الذكي لتحصل على ترشيحات فورية."),
    ("2", "اختر عقارك", "تصفح الصور الحقيقية والمواصفات الكاملة للوحدة المناسبة من المعرض."),
    ("3", "احجز موعد المعاينة", "تواصل مع فريق الدعم البشري لحجز زيارة ميدانية ومعاينة الموقع."),
]
for col, (n, t, d) in zip(st.columns(3), steps):
    col.markdown(f'<div class="card center"><div class="num">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>',
                 unsafe_allow_html=True)

# ─── عقارات مميزة ───
section("عقارات مميزة")
for col, prp in zip(st.columns(3), data["picked"]):
    comp = company_tag(prp.get("company_name"))
    p = safe(prp)
    col.markdown(
        f'<div class="card prop">{comp}<div class="prop-wrap"><div class="prop-img" style="background-image:url({p["main_image"]})">'
        f'<span class="tag">{p["type"]}</span></div></div><div class="prop-body">'
        f'<div class="t">{p["title"]}</div>'
        f'<div class="muted"><i class="fa-solid fa-location-dot"></i> {p["location"]}</div>'
        f'<div class="specs"><span><i class="fa-solid fa-bed"></i>{p["beds"]}</span>'
        f'<span><i class="fa-solid fa-bath"></i>{p["baths"]}</span>'
        f'<span><i class="fa-solid fa-ruler-combined"></i>{p["area"]} م²</span></div>'
        f'<div class="price">{p["price"]} ج.م</div></div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
if st.columns([1, 1.2, 1])[1].button("عرض كل العقارات", key="all_props_btn", icon=":material/apartment:", width="stretch"):
    st.switch_page("pages/Properties.py")

# ─── الشركات المتعاقدة (شريط متحرك بصفّين باتجاهين) ───
if data["partners"]:
    section("الشركات المتعاقدة معنا", "نخبة من المطورين العقاريين يعرضون وحداتهم مباشرة على Aqarify")
    names = data["partners"][:16]
    mid = len(names) // 2

    def p_icon(n):
        logo = data["logos"].get(n)
        if logo and str(logo).startswith(("http://", "https://", "data:image/", "/")):
            return f'<div class="p-ico"><img src="{esc(logo)}" alt=""></div>'
        fill, line = EMBLEMS[data["registry"].get(n, ("skyline", None))[0]]
        return ('<div class="p-ico"><svg viewBox="4 4 56 56" fill="none">'
                + (f'<path d="{fill}" fill="rgba(201,162,75,.2)"/>' if fill else "")
                + f'<path d="{line}" stroke="#A8832F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

    def marquee(lst, cls=""):
        lst = lst * max(1, -(-6 // len(lst)))   # نكرر لو العدد قليل عشان الحركة تفضل متصلة
        cards = "".join(
            f'<div class="partner">{p_icon(n)}<div><b>{esc(n)}</b>'
            f'<span>{data["counts"].get(n, 0)} وحدة</span></div></div>' for n in lst)
        return f'<div class="marq {cls}"><div class="track" style="--d:{max(30, len(lst) * 6)}s">{cards}{cards}</div></div>'

    st.markdown('<div class="partners-panel">' + marquee(names) + marquee(names[mid:] + names[:mid], "rev") + "</div>",
                unsafe_allow_html=True)

# ─── آراء العملاء ───
section("آراء العملاء")
STARS = '<i class="fa-solid fa-star"></i>' * 5
reviews = [
    ("أحمد الشريف", "تجربة استثنائية! المستشار الذكي ساعدني في تحديد الشقة المناسبة بميزانيتي بالضبط قبل المعاينة."),
    ("م. سارة محمود", "السرعة في التواصل والدقة في عرض المساحات الهندسية جعلت عملية الشراء سهلة وموثوقة جداً."),
    ("د. كريم عبد العزيز", "منصة ممتازة وحاسبة التمويل كانت دقيقة جداً في حساب القسط الشهري بدون مفاجآت."),
]
for col, (name, text) in zip(st.columns(3), reviews):
    col.markdown(f'<div class="card"><div class="stars">{STARS}</div>'
                 f'<div class="quote">{text}</div><div class="t" style="margin:0;font-size:17px">{name}</div></div>',
                 unsafe_allow_html=True)

# ─── دعوة للتصرف ───
st.markdown('<div class="cta"><div class="t">جاهز تلاقي بيتك؟</div>'
            '<div class="d">ابدأ الآن محادثتك مع المستشار العقاري الذكي واكتشف أفضل الفرص المتاحة.</div></div>',
            unsafe_allow_html=True)
if st.columns([1, 1.2, 1])[1].button("ابدأ المحادثة الآن", key="cta_bottom_btn", type="primary",
                                      icon=":material/rocket_launch:", width="stretch"):
    st.switch_page("pages/Customer Service.py")

# ─── الفوتر ───
st.markdown("<hr style='margin: 50px 0 28px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([1.6, 1, 1.2])
with f1:
    st.markdown(f"""
    <div class="brand-logo-link" style="margin-bottom: 10px;">
        <img src="data:image/png;base64,{LOGO_B64}" alt="Aqarify" style="height:52px;width:auto;flex-shrink:0;">
        <div>
            <div class="brand-logo-text">Aqarify<span class="brand-logo-dot">.</span></div>
            <span class="brand-logo-sub">بيتك القادم يبدأ من هنا</span>
        </div>
    </div>
    <div class="foot-p" style="margin-top:8px">المنصة العقارية الذكية الأولى للحلول السكنية والاستثمارية الموثوقة.</div>
    """, unsafe_allow_html=True)
with f2:
    st.markdown("<div class='foot-t'>روابط سريعة</div>", unsafe_allow_html=True)
    st.page_link("App.py", label="الرئيسية")
    st.page_link("pages/Properties.py", label="معرض العقارات")
    st.page_link("pages/Customer Service.py", label="المستشار الذكي")
    st.page_link("pages/Calculator.py", label="حاسبة التمويل")
with f3:
    st.markdown("<div class='foot-t'>بيانات التواصل</div>"
                "<div class='foot-p'><i class='fa-solid fa-phone'></i>+20 100 000 0000</div>"
                "<div class='foot-p'><i class='fa-solid fa-envelope'></i>support@aqarify.com</div>"
                "<div class='foot-p'><i class='fa-solid fa-location-dot'></i>القاهرة، مصر</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 14px 0;'><div class='copy'>جميع الحقوق محفوظة © 2026 منصة Aqarify العقارية.</div>",
            unsafe_allow_html=True)