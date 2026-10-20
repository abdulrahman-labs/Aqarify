import os
import re
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

import db

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Use the current Google Gen AI SDK.
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    genai = None
    types = None
    HAS_GEMINI = False

st.set_page_config(
    page_title="المستشار الذكي | Aqarify",
    page_icon=":material/support_agent:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_FILE = db.DB_FILE
WHATSAPP_NUMBER = "201000000000"   # ← غيّره برقمك الحقيقي
PHONE_TEXT = "+20 100 000 0000"
EMAIL_TEXT = "support@aqarify-eg.com"

# ═══════════════════════════════════════════════════════════════
# 1) التنسيق الموحد
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    :root {
        --color-dark: #14161C;
        --color-white: #FFFFFF;
        --color-accent: #C9A24B;
        --color-bg: #FAFAF8;
        --color-border: #E4E2DA;
        --color-text-muted: #666666;
    }

    html, body, .stApp, [data-testid="stDialog"] { direction: rtl; }
    .stApp [data-testid="stMarkdownContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: var(--color-bg); color: var(--color-dark); }
    .stApp *:not(i):not([data-testid="stIconMaterial"]) { font-family: 'Cairo', sans-serif !important; }

    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 1280px; }

    /* ─── الشعار ─── */
    .brand-logo-link { display: inline-flex; align-items: center; gap: 14px; }
    .brand-icon-box {
        background: #F0EFEA; color: var(--color-dark); width: 52px; height: 52px; border-radius: 14px;
        border: 1px solid var(--color-border); box-shadow: 0 4px 12px rgba(20,22,28,.06);
        display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;
    }
    .brand-logo-text { font-size: 34px; font-weight: 800; color: var(--color-dark); line-height: 1; margin: 0; }
    .brand-logo-dot { color: var(--color-accent); }
    .brand-logo-sub { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; display: block; }

    /* ─── شريط التنقل ─── */
    .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: wrap;
        justify-content: flex-end; align-items: center; gap: 28px !important; padding-top: 10px;
    }
    .st-key-topnav [data-testid="stElementContainer"],
    .st-key-topnav [data-testid="stPageLink"] { width: auto !important; flex: 0 0 auto !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"] {
        position: relative; display: inline-flex !important; align-items: center; gap: 8px;
        background: transparent !important; padding: 8px 0 !important; border-radius: 0 !important;
        color: var(--color-dark) !important; text-decoration: none !important; transition: color .2s ease;
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"] p {
        font-size: 17px !important; font-weight: 700 !important; color: inherit !important; margin: 0 !important;
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"]::before {
        font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important; font-size: 16px; content: "\\f015";
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Properties"]::before { content: "\\f64f"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Customer"]::before   { content: "\\f508"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Calculator"]::before { content: "\\f1ec"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Admin"]::before      { content: "\\f1de"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]:hover { color: var(--color-accent) !important; background: transparent !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Customer"] { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Customer"]::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent);
    }

    /* ─── كروت عامة ─── */
    .box {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 20px; padding: 20px; margin-bottom: 16px;
    }
    .box-title { font-size: 16px; font-weight: 800; margin-bottom: 10px; }
    .advisor-head { display: flex; align-items: center; gap: 16px; }
    .advisor-avatar {
        width: 54px; height: 54px; border-radius: 16px; background: var(--color-dark);
        color: var(--color-accent); display: flex; align-items: center; justify-content: center;
        font-size: 24px; flex-shrink: 0;
    }
    .advisor-name { font-size: 20px; font-weight: 800; line-height: 1.2; }
    .advisor-desc { font-size: 14px; color: var(--color-text-muted); margin-top: 2px; }
    .mode-chip {
        display: inline-block; border: 1px solid var(--color-border); border-radius: 20px;
        padding: 2px 12px; font-size: 12px; font-weight: 700; margin-top: 8px;
    }
    .mode-chip i { color: var(--color-accent); margin-left: 6px; }

    .chip {
        display: inline-block; border: 1px solid var(--color-border); border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600; margin-left: 6px; margin-top: 4px;
        background: var(--color-white);
    }

    /* ─── كارت العقار المختار ─── */
    .sel-img { height: 190px; border-radius: 14px; background-size: cover; background-position: center; background-color: var(--color-border); margin-bottom: 14px; }
    .sel-title { font-size: 18px; font-weight: 800; }
    .sel-loc { font-size: 14px; color: var(--color-text-muted); margin: 4px 0 8px; }
    .sel-price { font-size: 22px; font-weight: 800; color: var(--color-accent); }
    .sel-specs { display: flex; justify-content: space-between; background: #F9FAFB; border: 1px solid var(--color-border); border-radius: 12px; padding: 10px 14px; font-size: 14px; font-weight: 700; margin: 12px 0 8px; }

    /* ─── كروت الترشيحات داخل المحادثة ─── */
    .mini-card { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 16px; overflow: hidden; transition: all .25s ease; }
    .mini-card:hover { transform: translateY(-3px); border-color: var(--color-accent); box-shadow: 0 10px 22px rgba(0,0,0,.07); }
    .mini-img { height: 120px; background-size: cover; background-position: center; background-color: var(--color-border); }
    .mini-body { padding: 12px 14px; }
    .mini-title { font-size: 14px; font-weight: 800; line-height: 1.4; }
    .mini-loc { font-size: 12px; color: var(--color-text-muted); margin: 2px 0 6px; }
    .mini-price { font-size: 16px; font-weight: 800; color: var(--color-accent); }
    .mini-specs { font-size: 12px; font-weight: 700; margin-top: 4px; }

    /* ─── المحادثة ─── */
    [data-testid="stChatMessage"] {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 16px; padding: 14px 18px; margin-bottom: 10px;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #F4F2EC; }
    [data-testid="stChatMessageAvatarAssistant"] { background: var(--color-dark) !important; color: var(--color-accent) !important; }
    [data-testid="stChatMessageAvatarUser"] { background: var(--color-accent) !important; color: var(--color-dark) !important; }
    [data-testid="stChatInput"] { border-radius: 14px; border: 1px solid var(--color-border); }

    /* حاوية الرسائل (بتسكرول جواها) وعنصر السكرول المخفي */
    .st-key-chat_scroll { background: var(--color-bg); }
    .st-key-scroll_helper { height: 0 !important; margin: 0 !important; overflow: hidden !important; }

    /* ─── التبويبات ─── */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: none; }
    .stTabs [data-baseweb="tab"] {
        height: 46px; background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 12px; padding: 0 22px;
    }
    .stTabs [data-baseweb="tab"] p { font-weight: 800; }
    .stTabs [aria-selected="true"] { background: var(--color-dark) !important; border-color: var(--color-dark); }
    .stTabs [aria-selected="true"] p { color: var(--color-accent) !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ─── واتساب والتواصل ─── */
    .wa-btn {
        display: flex; align-items: center; justify-content: center; gap: 10px;
        background: var(--color-dark); color: var(--color-white) !important; font-weight: 800;
        padding: 13px 20px; border-radius: 12px; text-decoration: none !important;
        transition: all .2s ease; margin-bottom: 14px;
    }
    .wa-btn i { color: #25D366; font-size: 22px; }
    .wa-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(20,22,28,.25); }
    .info-row { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; font-size: 14px; }
    .info-row i { color: var(--color-accent); width: 18px; margin-top: 4px; }
    .info-row b { display: block; font-size: 13px; color: var(--color-text-muted); font-weight: 600; }

    /* ─── الأزرار الموحدة ─── */
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-secondaryFormSubmit"], [data-testid="stBaseButton-primaryFormSubmit"] {
        font-weight: 700; border-radius: 12px; transition: all .2s ease;
    }
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {
        background: transparent; color: var(--color-dark); border: 1px solid var(--color-dark);
    }
    [data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background: var(--color-dark); color: var(--color-white); border-color: var(--color-dark);
    }
    [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--color-accent); color: var(--color-dark); border: 1px solid var(--color-accent);
    }
    [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover {
        box-shadow: 0 4px 12px rgba(201,162,75,.35); background: var(--color-accent); color: var(--color-dark);
    }
    /* ─── تحسينات التجاوب مع الهواتف الذكية (Mobile Responsive) ─── */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        .hero-title-main { font-size: 28px !important; }
        .brand-logo-text { font-size: 26px !important; }
        .kpi-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
        .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] {
            justify-content: center !important; gap: 12px !important;
        }
        /* إجبار أعمدة Streamlit على النزول تحت بعضها على الموبايل */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2) البيانات (من قاعدة البيانات SQLite)
# ═══════════════════════════════════════════════════════════════
def _to_legacy(p):
    """يحوّل صف الـ DB لنفس الشكل القديم (price نص منسّق، price_val رقم، desc)."""
    p = dict(p)
    p["price_val"] = int(p["price"])
    p["price"] = f"{p['price_val']:,}"
    p["desc"] = p.pop("description", "") or ""
    if isinstance(p.get("area"), float) and p["area"].is_integer():
        p["area"] = int(p["area"])
    return p


@st.cache_data
def load_props(mtime):
    items = [_to_legacy(p) for p in db.search_properties(sort="newest")]
    return sorted(items, key=lambda p: p["id"])


if DB_FILE.exists():
    PROPS = load_props(DB_FILE.stat().st_mtime)
else:
    PROPS = st.session_state.get("properties_list", [])
st.session_state.properties_list = PROPS

# ═══════════════════════════════════════════════════════════════
# 3) الهيدر الموحد
# ═══════════════════════════════════════════════════════════════
col_logo, col_nav = st.columns([1.5, 2.6])
with col_logo:
    st.markdown("""
    <div class="brand-logo-link">
        <div class="brand-icon-box"><i class="fa-solid fa-building-columns"></i></div>
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

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

if not PROPS:
    st.error("قاعدة البيانات غير موجودة. شغّل: python migrate.py")
    st.stop()


@st.cache_resource
def _init_chat_db():
    """ينشئ جداول المحادثات والتذاكر مرة واحدة (IF NOT EXISTS فمفيش خطر)."""
    db.init_chat_tables()
    db.init_tickets_table()
    return True


_init_chat_db()

# ═══════════════════════════════════════════════════════════════
# 4) منطق المستشار (بحث + ردود محلية مطورة + Gemini)
# ═══════════════════════════════════════════════════════════════
# ===== LOGIC START =====
BY_ID = {p["id"]: p for p in PROPS}
CITIES = sorted({p["city"] for p in PROPS if "city" in p})

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm(t):
    t = t.translate(AR_DIGITS).lower()
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")):
        t = t.replace(a, b)
    return re.sub(r"[\u064B-\u0652]", "", t)


def floor_text(p):
    return "أرضي" if p.get("floor") in (None, 0) else f"الدور {p['floor']}"


def money(v):
    return f"{int(v):,}"


def p_line(p):
    return f"**#{p['id']} {p['title']}** — {money(p['price_val'])} ج.م · {p['area']} م² · {p['beds']} غرف · {p['location']}"


CITY_ALIASES = [("مصر الجديده", "مصر الجديدة"), ("تجمع", "التجمع الخامس"), ("زايد", "الشيخ زايد"),
                ("عاصمه", "العاصمة الإدارية"), ("معادي", "المعادي"), ("ساحل", "الساحل الشمالي"),
                ("شروق", "الشروق"), ("نصر", "مدينة نصر"), ("اكتوبر", "6 أكتوبر")]
TYPE_ALIASES = [("تاون", "تاون هاوس"), ("بنت", "بنتهاوس"), ("دوبلكس", "دوبلكس"), ("ستوديو", "استوديو"),
                ("شاليه", "شاليه"), ("فيلا", "فيلا"), ("فلل", "فيلا"), ("شق", "شقة")]


def parse_query(text):
    t = norm(text)
    f = {}
    for key, city in CITY_ALIASES:
        if key in t:
            f["city"] = city
            break
    for key, typ in TYPE_ALIASES:
        if key in t:
            f["type"] = typ
            break
    m = re.search(r"(\d+)\s*(?:غرف|غرفه|اوض|اوضه|نوم)", t)
    if m:
        f["beds"] = int(m.group(1))
    else:
        for w, n in (("غرفتين", 2), ("اوضتين", 2), ("تلات", 3), ("ثلاث", 3), ("اربع", 4), ("خمس", 5)):
            if w in t and ("غرف" in t or "اوض" in t or "غرفتين" in t or "اوضتين" in t):
                f["beds"] = n
                break
    m = re.search(r"(\d+(?:\.\d+)?)\s*مليون", t)
    if m:
        v = float(m.group(1))
        if re.search(r"مليون\s*و\s*(?:نص|نصف)", t):
            v += 0.5
        f["max_price"] = v * 1e6
    elif "مليونين" in t:
        f["max_price"] = 2e6
    if "جاهز" in t or "فوري" in t:
        f["ready"] = True
    elif "تحت الانشاء" in t:
        f["ready"] = False
    if any(w in t for w in ("ارخص", "اقل سعر", "اوفر")):
        f["sort"] = "price_asc"
    elif any(w in t for w in ("اغلي", "افخم", "اعلي سعر")):
        f["sort"] = "price_desc"
    elif "اكبر" in t:
        f["sort"] = "area_desc"
    elif "استثمار" in t:
        f["sort"] = "ppm"
    return f


def has_filters(f):
    return bool(f and (f.get("city") or f.get("type") or f.get("beds") or f.get("max_price") or f.get("sort")))


def run_search(f):
    res = []
    for p in PROPS:
        if f.get("city") and f["city"] not in p["location"]:
            continue
        if f.get("type") and p["type"] != f["type"]:
            continue
        if f.get("beds") and p["beds"] != f["beds"]:
            continue
        if f.get("max_price") and p["price_val"] > f["max_price"]:
            continue
        if f.get("ready") is True and "جاهز" not in norm(p.get("status", "جاهز")):
            continue
        if f.get("ready") is False and "جاهز" in norm(p.get("status", "جاهز")):
            continue
        res.append(p)
    s = f.get("sort")
    if s == "price_desc":
        res.sort(key=lambda p: -p["price_val"])
    elif s == "area_desc":
        res.sort(key=lambda p: -p["area"])
    elif s == "ppm":
        res.sort(key=lambda p: p["price_val"] / p["area"])
    elif s == "price_asc" or not f.get("max_price"):
        res.sort(key=lambda p: p["price_val"])
    else:
        res.sort(key=lambda p: -p["price_val"])
    return res


def search_with_relax(f):
    res = run_search(f)
    if res:
        return res, ""
    if f.get("max_price"):
        g = dict(f, max_price=f["max_price"] * 1.25)
        res = run_search(g)
        if res:
            return res, "لا توجد وحدات مطابقة تماماً، وهذه أقرب الخيارات وتتجاوز الميزانية بنسبة بسيطة (حتى 25%)"
    if f.get("beds"):
        g = {k: v for k, v in f.items() if k != "beds"}
        res = run_search(g)
        if res:
            return res, "لا توجد وحدات بنفس عدد الغرف، وهذه أقرب البدائل"
    if f.get("city"):
        g = {k: v for k, v in f.items() if k != "city"}
        res = run_search(g)
        if res:
            return res, "لا توجد وحدات مطابقة في هذه المنطقة، وهذه بدائل في مناطق أخرى"
    return [], ""


def similar_to(p, n=3):
    cands = [q for q in PROPS if q["id"] != p["id"] and q["type"] == p["type"]
             and 0.75 * p["price_val"] <= q["price_val"] <= 1.25 * p["price_val"]]
    cands.sort(key=lambda q: abs(q["price_val"] - p["price_val"]))
    return cands[:n]


def finance_text(p):
    price = p["price_val"]
    down = price * 0.10
    monthly = (price - down) / 96
    return (f"سعر **#{p['id']}** هو **{money(price)} ج.م**.\n\n"
            f"- مقدم تقديري (10%): **{money(down)} ج.م**\n"
            f"- قسط شهري تقديري على 8 سنوات: **{money(monthly)} ج.م**\n\n"
            "الأرقام تقريبية وبدون فوائد، وللتفاصيل الدقيقة استخدم صفحة حاسبة التمويل.")


def about_property(p, t):
    if any(w in t for w in ("مشابه", "شبه", "بدائل", "بديل", "غيرها", "اقتراح", "ارشح", "رشح")):
        sims = similar_to(p)
        if sims:
            return ("هذه وحدات قريبة منها في النوع والسعر:\n\n" + "\n".join("- " + p_line(q) for q in sims)
                    + "\n\nتحب أقارن لك بينها وبين وحدتك المختارة؟", [q["id"] for q in sims])
        return "لا توجد وحدات مشابهة قريبة في السعر حالياً، لو حابب وسّع الميزانية وأرشح لك بدائل.", []
    if any(w in t for w in ("تقسيط", "تمويل", "قسط", "مقدم", "سداد", "دفع", "اقساط")):
        return finance_text(p) + "\n\nتحب أرشح لك وحدات بقسط أقل؟", []
    if any(w in t for w in ("سعر", "بكام", "ثمن", "تكلف", "قيمه", "كام")):
        ppm = p["price_val"] // p["area"]
        return (f"سعر **#{p['id']} {p['title']}** هو **{money(p['price_val'])} ج.م**، "
                f"أي حوالي **{money(ppm)} ج.م للمتر**.\n\nتحب أحسب لك المقدم والقسط الشهري؟"), []
    if any(w in t for w in ("معاينه", "حجز", "زياره", "ازور", "اشوف", "موعد")):
        return (f"ممتاز، المعاينة أهم خطوة. اضغط تبويب **الدعم البشري وحجز تذكرة** وسجّل رقمك، "
                f"أو راسلنا مباشرة على واتساب، وسنرتب لك زيارة **#{p['id']}** في {p['location']}."), []
    finishing = p.get("finishing", "أولترا سوبر لوكس")
    status = p.get("status", "جاهز للتسليم")
    delivery = p.get("delivery", "فوري")
    if "تشطيب" in t:
        return f"تشطيب الوحدة **{finishing}**، وحالتها **{status}** (الاستلام: {delivery}).", []
    if any(w in t for w in ("استلام", "جاهز", "تسليم")):
        return f"حالة الوحدة: **{status}**، وموعد الاستلام: **{delivery}**.", []
    if any(w in t for w in ("ميزه", "ميزات", "خدمات", "مرافق", "كمبوند")):
        feats = "، ".join(p.get("features", ["موقع متميز", "أمن وحراسة", "مساحات خضراء"]))
        return f"تتوفر في الوحدة والمشروع الخدمات التالية: {feats}.", []
    return (f"تفاصيل **#{p['id']} {p['title']}**:\n\n"
            f"- **الموقع:** {p['location']}\n- **المساحة:** {p['area']} م²\n"
            f"- **الغرف:** {p['beds']} غرف نوم و{p['baths']} حمام\n- **الموقع بالمبنى:** {floor_text(p)}\n"
            f"- **التشطيب:** {finishing}\n- **الحالة:** {status} (استلام: {delivery})\n"
            f"- **السعر:** {money(p['price_val'])} ج.م\n\nتحب أعرف لك خطة السداد أو أرشح وحدات مشابهة؟"), []


def search_text(recs, note):
    top = recs[:3]
    head = (note + ".\n\n" if note else "") + f"وجدت **{len(recs)}** وحدة مناسبة، وهذه أبرز الترشيحات:"
    body = "\n".join("- " + p_line(p) for p in top)
    return (head + "\n\n" + body + "\n\nاضغط «اسأل عنها» تحت أي وحدة لعرض تفاصيلها، "
            "أو غيّر الميزانية أو المنطقة وأعيد البحث لك.")


def local_reply(text, active):
    t = norm(text)

    # 1. الردود الودية وشخصية المستشار
    if any(w in t for w in ("اخبارك", "ازيك", "كيفك", "عامل ايه", "اخبارك ايه")):
        return ("أهلاً بك! أنا بخير وفي أتم الاستعداد لمساعدتك في العثور على بيت أحلامك أو استثماراتك العقارية اليوم. كيف يمكنني خدمتك؟"), []

    if any(w in t for w in ("من انت", "مين انت", "عرفني بنفسك", "وظيفتك")):
        return ("أنا مستشارك العقاري الذكي لمنصة Aqarify. أمتلك قاعدة بيانات كاملة بكافة الوحدات والمشاريع المتاحة، وأساعدك في اختيار عقارك المناسب، حساب التمويل، وحجز المعاينات بكل سهولة."), []

    if any(w in t for w in ("شكرا", "تسلم", "ممتاز", "جميل", "يعطيك العافيه", "كفو")):
        return "العفو، أنا في خدمتك دائماً! لو احتجت أي ترشيحات أو تفاصيل إضافية عن الأسعار والمساحات، لا تتردد في سؤالي.", []

    if any(w in t for w in ("مرحبا", "اهلا", "السلام", "هاي", "صباح", "مساء")):
        prices = [p["price_val"] for p in PROPS]
        return (f"أهلاً وسهلاً بك في منصة Aqarify! يسعدني مساعدتك. "
                f"لدينا **{len(PROPS)}** وحدة عقارية حقيقية تبدأ أسعارها من **{money(min(prices))} ج.م**.\n\n"
                "اخبرني بالمنطقة، عدد الغرف، أو الميزانية المناسبة لك وسأقدم لك أفضل الترشيحات فوراً!"), []

    # 2. الاستعلام بالوحدة المحددة حالياً
    if active:
        return about_property(active, t)

    # 3. تحليل وشروط الاستعلام والبحث
    f = parse_query(text)
    if has_filters(f):
        recs, note = search_with_relax(f)
        if recs:
            return search_text(recs, note), [p["id"] for p in recs[:3]]
        return ("لم أجد وحدات مطابقة تماماً لهذه المواصفات. يمكنك تجربة ميزانية أعلى قليلاً، أو اختيار منطقة مجاورة وسأرشح لك أفضل الخيارات المتاحة."), []

    # 4. استفسارات المعاينة والتواصل والتقسيط
    if any(w in t for w in ("تقسيط", "تمويل", "قسط", "مقدم", "سداد", "نظام")):
        return ("أنظمة السداد المتاحة تعتمد عادةً على مقدم يبدأ من **10%** وقسط يصل حتى **8 سنوات** بدون فوائد.\n\n"
                "حدد لي الشقة أو المنطقة التي تفضلها وسأحسب لك قيمة المقدم والقسط بدقة."), []

    if any(w in t for w in ("معاينه", "حجز", "زياره", "تواصل", "رقم", "واتس")):
        return ("يمكنك حجز معاينة على الطبيعة بسهولة من خلال الانتقال إلى تبويب **الدعم البشري وحجز تذكرة** وتعبئة رقم هاتفك، أو التواصل معنا مباشرة عبر الواتساب وسيرتب لك ممثل المبيعات الموعد المناسب."), []

    # 5. البحث الشامل للوحدات المتميزة تلقائياً عند الأسئلة العامة
    prices = [p["price_val"] for p in PROPS]
    top_recs = sorted(PROPS, key=lambda x: x["price_val"])[:3]
    return (f"أهلاً بك! يمكنني تقديم استشارات مميزة واختيار الوحدة الأنسب لك من بين **{len(PROPS)}** وحدة متاحة بأسعار تبدأ من **{money(min(prices))} ج.م**.\n\n"
            f"إليك نموذجاً من أحدث الوحدات المتاحة:\n" + "\n".join("- " + p_line(p) for p in top_recs) +
            "\n\nيمكنك تحديد طلبك بذكر المنطقة (مثل: التجمع، الشيخ زايد، العاصمة) والميزانية وسأرشح لك العقار المثالي."), [p["id"] for p in top_recs]


# ─── اختيار الوحدات المرسلة لـ Gemini (أفضل 5 فقط بدل الكتالوج كله) ───
SHORTLIST_SIZE = 5


def shortlist(text, active, history, n=SHORTLIST_SIZE):
    """بحث محلي يرجّع أقرب n وحدات لسؤال العميل. Gemini ما بيشوفش غيرها."""
    picked = []

    def add(p):
        if len(picked) >= n:
            return
        if active and p["id"] == active["id"]:
            return
        if all(p["id"] != x["id"] for x in picked):
            picked.append(p)

    t = norm(text)

    # 1) وحدات ذكرها العميل صراحة (#12 أو "وحدة رقم 12")
    for m in re.findall(r"(?:#|رقم|وحده)\s*(\d{1,3})", t):
        if int(m) in BY_ID:
            add(BY_ID[int(m)])

    # 2) الوحدات اللي رشحناها في آخر رد (عشان أسئلة زي "قارن بينهم")
    for m in reversed(history):
        if m.get("ids"):
            for i in m["ids"]:
                if i in BY_ID:
                    add(BY_ID[i])
            break

    # 3) بحث بالفلاتر المفهومة من السؤال
    f = parse_query(text)
    if has_filters(f):
        recs, _ = search_with_relax(f)
        for p in recs:
            add(p)

    # 4) لو مفيش أي حاجة، نبعت عينة صغيرة (الأرخص)
    if not picked:
        for p in sorted(PROPS, key=lambda x: x["price_val"]):
            add(p)

    return picked[:n]


def catalog_text(units):
    lines = []
    for p in units:
        lines.append(f"#{p['id']} | {p['type']} | {p['location']} | {p['price_val']:,} ج.م | "
                     f"{p['area']} م² | {p['beds']} غرف | {p.get('status', '')}")
    return "\n".join(lines)


SYSTEM_PROMPT = """أنت المستشار العقاري الذكي لمنصة Aqarify في مصر.
- تتحدث بالعربية بأسلوب مهني ودود، سلس، ومحترف جداً.
- مصدرك الوحيد للمعلومات هو الوحدات المرفقة مع السؤال (وهي أنسب نتائج البحث وليست كل الوحدات)، ولا تذكر معلومات غير صحيحة.
- عند الترشيح اذكر أرقام الوحدات بصيغة #رقم (بحد أقصى 3 وحدات) مع السعر والمساحة والمنطقة.
- لا تخترع أي وحدة أو سعر أو مساحة أو ميزة غير موجودة في الوحدات المرفقة.
- إذا لم تتوفر معلومة في البيانات، قل بوضوح إنها غير متاحة، واطلب من العميل تحديد المنطقة أو الميزانية أو عدد الغرف لتحسين البحث.
- للأسعار والتقسيط: المقدم التقديري 10% والباقي على 8 سنوات بدون فوائد، مع توضيح أن الأرقام تقديرية.
- للمعاينة أو التواصل وجّه العميل إلى تبويب «الدعم البشري وحجز تذكرة» أو الواتساب.
- جاوب على تحية العميل واستفساراته العامة بود ولطف ومهنية راقية."""


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        elif "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
            return st.secrets["gemini"]["api_key"]
    except Exception:
        pass
    return ""


# ─── كاش الردود: نفس السؤال المتكرر يتجاوب من غير ما نكلم الـ API ───
CACHE_MAX = 300


@st.cache_resource
def _reply_cache():
    return {}


def ask_gemini(text, active, history):
    key = get_api_key()

    if not HAS_GEMINI:
        st.session_state["llm_error"] = (
            "مكتبة Google Gen AI غير مثبتة. شغّل الأمر: "
            "python -m pip install -U google-genai"
        )
        return None

    if not key:
        st.session_state["llm_error"] = (
            "مفتاح Gemini غير موجود. أضف GEMINI_API_KEY إلى ملف .env "
            "أو إلى Streamlit Secrets."
        )
        return None

    # نكاشي بس الأسئلة المستقلة (ليها فلاتر واضحة أو متعلقة بوحدة مختارة)
    cache = _reply_cache()
    cacheable = bool(active) or has_filters(parse_query(text))
    ckey = (norm(text).strip(), active["id"] if active else None)
    if cacheable and ckey in cache:
        st.session_state.pop("llm_error", None)
        return cache[ckey]

    try:
        client = genai.Client(api_key=key)

        ctx = ""
        if active:
            ctx = (
                f"\nالوحدة التي يسأل عنها العميل الآن:\n"
                f"#{active['id']} | {active['title']} | {active['location']} | "
                f"{active['price_val']:,} ج.م | {active['area']} م² | "
                f"{active['beds']} غرف | {active.get('desc', '')}\n"
            )

        units = shortlist(text, active, history)

        hist = "\n".join(
            ("العميل: " if m["role"] == "user" else "المستشار: ") + m["content"][:400]
            for m in history[-4:]
        )

        prompt = (
            "أنسب الوحدات المتاحة في Aqarify لطلب العميل (نتيجة بحث، وليست كل الوحدات):\n"
            f"{catalog_text(units)}\n"
            f"{ctx}\n"
            f"سجل المحادثة السابقة:\n{hist}\n\n"
            f"سؤال العميل الحالي:\n{text}\n\n"
            "أجب عن السؤال مباشرة بالعربية. استخدم الوحدات المذكورة أعلاه فقط "
            "في معلومات العقارات والأسعار والمواصفات. لا تخترع وحدات أو "
            "أسعارًا أو مواصفات غير موجودة. عند الترشيح اذكر أرقام الوحدات "
            "بصيغة #رقم وبحد أقصى ثلاث وحدات. إذا لم تجد معلومة في البيانات، "
            "وضّح أنها غير متاحة."
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        reply = getattr(response, "text", None)
        if not reply or not reply.strip():
            st.session_state["llm_error"] = (
                "اتصل Gemini لكن لم يُرجع نصًا. جرّب إرسال السؤال مرة أخرى."
            )
            return None

        reply = reply.strip()
        st.session_state.pop("llm_error", None)

        if cacheable:
            if len(cache) >= CACHE_MAX:
                cache.clear()
            cache[ckey] = reply
        return reply

    except Exception as e:
        error_text = f"{type(e).__name__}: {e}"
        st.session_state["llm_error"] = error_text[:500]
        print(f"[Aqarify Gemini Error] {error_text}")
        return None


def extract_ids(reply, active):
    ids = []
    for m in re.findall(r"#(\d{1,3})", reply):
        i = int(m)
        if i in BY_ID and i not in ids and not (active and i == active["id"]):
            ids.append(i)
    return ids[:3]
# ===== LOGIC END =====


def respond(text):
    active = BY_ID.get(st.session_state.get("active_prop_id"))
    history = st.session_state.messages[:-1]
    reply = ask_gemini(text, active, history)

    if reply:
        ids = extract_ids(reply, active)

        # If the user asks for recommendations but Gemini omitted IDs,
        # derive the displayed recommendation cards from the real catalog.
        f = parse_query(text)
        asks_for_recommendations = any(
            word in norm(text)
            for word in ("رشح", "ترشيح", "اقتراح", "افضل", "ارخص", "وحدات", "شقه", "فيلا", "شاليه", "استثمار")
        )
        if not ids and has_filters(f):
            recs, _ = search_with_relax(f)
            ids = [p["id"] for p in recs[:3] if not (active and p["id"] == active["id"])]
        elif not ids and asks_for_recommendations and not active:
            recs = sorted(PROPS, key=lambda p: p["price_val"])[:3]
            ids = [p["id"] for p in recs]

        return reply.strip(), ids

    # Local replies remain the fallback when Gemini cannot answer.
    return local_reply(text, active)


# ═══════════════════════════════════════════════════════════════
# 5) حالة الجلسة وسجل المحادثات
# ═══════════════════════════════════════════════════════════════
GREETING = (f"أهلاً بك في Aqarify. أنا مستشارك العقاري الذكي، وعندي بيانات كل الوحدات المتاحة ({len(PROPS)} وحدة) "
            "بمساحاتها وأسعارها وتفاصيلها. اطلب مني ترشيحات حسب ميزانيتك ومنطقتك، أو اسألني عن أي وحدة.")
st.session_state.setdefault("messages", [{"role": "assistant", "content": GREETING, "ids": []}])
st.session_state.setdefault("active_prop_id", None)
st.session_state.setdefault("conv_id", None)   # رقم المحادثة المحفوظة (None = محادثة جديدة)

ctx_title = st.session_state.get("chat_property_context")
if ctx_title:
    data = st.session_state.get("active_prop_data") or {}
    pid = data.get("id")
    if pid not in BY_ID:
        pid = next((p["id"] for p in PROPS if p["title"] == ctx_title), None)
    if pid in BY_ID:
        st.session_state.active_prop_id = pid
        p = BY_ID[pid]
        st.session_state.messages.append({
            "role": "assistant", "ids": [],
            "content": (f"اخترت **#{p['id']} {p['title']}** ({p['location']}). "
                        "تفاصيلها ظاهرة على الجانب، اسألني عن السعر وخطة السداد أو المميزات أو أي وحدات مشابهة."),
        })
    st.session_state.chat_property_context = None


def current_user():
    return st.session_state.get("user")


def _save_active(pid):
    """يحفظ الوحدة المختارة جوه المحادثة المحفوظة (لو فيه)."""
    user, cid = current_user(), st.session_state.get("conv_id")
    if user and cid:
        try:
            db.set_conversation_property(cid, user["id"], pid)
        except Exception:
            pass


def set_prompt(text):
    st.session_state.pending_prompt = text


def select_property(pid):
    st.session_state.active_prop_id = pid
    st.session_state.pending_prompt = f"عايز أعرف تفاصيل الوحدة رقم {pid}"
    _save_active(pid)


def clear_active():
    st.session_state.active_prop_id = None
    _save_active(None)


def new_chat():
    st.session_state.messages = [{"role": "assistant", "content": GREETING, "ids": []}]
    st.session_state.active_prop_id = None
    st.session_state.conv_id = None


def open_conversation(cid):
    user = current_user()
    if not user:
        return
    conv = db.get_conversation(cid, user["id"])
    if not conv:
        return
    stored = db.get_messages(cid, user["id"])
    st.session_state.messages = [{"role": "assistant", "content": GREETING, "ids": []}] + stored
    st.session_state.conv_id = cid
    ap = conv.get("active_prop_id")
    st.session_state.active_prop_id = ap if ap in BY_ID else None


def delete_conv(cid):
    user = current_user()
    if not user:
        return
    db.delete_conversation(cid, user["id"])
    if st.session_state.get("conv_id") == cid:
        new_chat()


def persist_turn(user, prompt, reply, ids):
    """يحفظ سؤال العميل ورد المستشار في المحادثة (وينشئها لو أول رسالة)."""
    try:
        cid = st.session_state.get("conv_id")
        if not cid:
            cid = db.create_conversation(user["id"], prompt, st.session_state.get("active_prop_id"))
            st.session_state.conv_id = cid
        db.add_message(cid, user["id"], "user", prompt)
        db.add_message(cid, user["id"], "assistant", reply, ids)
    except Exception as e:
        print(f"[Aqarify chat save error] {type(e).__name__}: {e}")
        st.warning("تعذر حفظ هذه المحادثة في سجلك، لكن المحادثة الحالية مستمرة.")


def auto_scroll():
    """ينزّل حاوية المحادثة لآخر رسالة تلقائياً بعد كل رد أو فتح محادثة."""
    nonce = f"{st.session_state.get('conv_id')}-{len(st.session_state.messages)}"
    js = """
    <script>
    (function () {
      var win = window.parent, doc = win.document;
      function scrollable(root) {
        var all = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
        for (var i = 0; i < all.length; i++) {
          var oy = win.getComputedStyle(all[i]).overflowY;
          if ((oy === 'auto' || oy === 'scroll') && all[i].scrollHeight > all[i].clientHeight + 1) return all[i];
        }
        return null;
      }
      function go() {
        var root = doc.querySelector('.st-key-chat_scroll');
        if (!root) return;
        var el = scrollable(root);
        if (el) el.scrollTop = el.scrollHeight;
      }
      [0, 150, 400, 900].forEach(function (t) { setTimeout(go, t); });
    })();
    </script>
    <!-- NONCE -->
    """.replace("NONCE", nonce)
    with st.container(key="scroll_helper"):
        components.html(js, height=0)


def go_calculator(p):
    st.session_state["selected_property_for_calc"] = {"title": p["title"], "price": p["price"]}
    st.switch_page("pages/Calculator.py")


def save_ticket(ticket):
    """يحفظ التذكرة في قاعدة البيانات ويرجّع كودها (TK-xxxx)، ومربوطة بالمستخدم لو مسجّل دخول."""
    user = current_user()
    prop = BY_ID.get(ticket.get("property_id"))
    return db.create_ticket(
        user["id"] if user else None,
        ticket["name"], ticket["phone"], ticket["topic"], ticket.get("notes", ""),
        ticket.get("property_id"), prop["title"] if prop else None,
    )


def mini_card(p):
    return (
        '<div class="mini-card">'
        f'<div class="mini-img" style="background-image:url({p["main_image"]})"></div>'
        '<div class="mini-body">'
        f'<div class="mini-title">{p["title"]}</div>'
        f'<div class="mini-loc"><i class="fa-solid fa-location-dot"></i> {p["location"]}</div>'
        f'<div class="mini-price">{money(p["price_val"])} ج.م</div>'
        f'<div class="mini-specs">{p["beds"]} غرف · {p["baths"]} حمام · {p["area"]} م²</div>'
        '</div></div>'
    )


def contact_box():
    wa = f"https://wa.me/{WHATSAPP_NUMBER}?text=" + quote("مرحباً فريق Aqarify، أود الاستفسار عن الوحدات المتاحة.")
    st.markdown(
        f'<div class="box"><a href="{wa}" target="_blank" class="wa-btn">'
        '<i class="fa-brands fa-whatsapp"></i> محادثة مباشرة عبر واتساب</a>'
        f'<div class="info-row"><i class="fa-solid fa-phone"></i><div><b>المبيعات والاستعلامات</b>{PHONE_TEXT}</div></div>'
        f'<div class="info-row"><i class="fa-solid fa-envelope"></i><div><b>البريد الإلكتروني</b>{EMAIL_TEXT}</div></div>'
        '<div class="info-row" style="margin-bottom:0"><i class="fa-solid fa-clock"></i>'
        '<div><b>مواعيد العمل</b>الأحد إلى الخميس، 9 ص - 6 م</div></div></div>',
        unsafe_allow_html=True,
    )


def history_box():
    """صندوق المحادثات القديمة: للمسجّل قائمة محادثاته، وللزائر دعوة لتسجيل الدخول."""
    user = current_user()
    if not user:
        st.markdown(
            '<div class="box"><div class="box-title"><i class="fa-solid fa-clock-rotate-left" style="color:var(--color-accent)"></i> محادثاتي</div>'
            '<div style="font-size:14px;color:var(--color-text-muted);margin-bottom:10px;">'
            'سجّل دخولك لحفظ محادثاتك مع المستشار والرجوع لها في أي وقت.</div></div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/Login.py", label="تسجيل الدخول", icon=":material/login:")
        return

    st.markdown('<div class="box-title"><i class="fa-solid fa-clock-rotate-left" style="color:var(--color-accent)"></i> محادثاتي</div>',
                unsafe_allow_html=True)
    st.button("محادثة جديدة", key="hist_new", icon=":material/add:", type="primary",
              on_click=new_chat, width="stretch")
    try:
        convs = db.list_conversations(user["id"])
    except Exception:
        convs = []
        st.caption("تعذر تحميل المحادثات.")
    if not convs:
        st.caption("لسه ما عندكش محادثات محفوظة. ابدأ بسؤال وهتتحفظ تلقائياً.")
    else:
        with st.container(height=260, key="hist_list"):
            for c in convs:
                a, b = st.columns([5, 1])
                is_cur = c["id"] == st.session_state.get("conv_id")
                a.button(c["title"], key=f"conv_{c['id']}", on_click=open_conversation, args=(c["id"],),
                         type="primary" if is_cur else "secondary", width="stretch")
                b.button("", key=f"cdel_{c['id']}", icon=":material/delete:", help="حذف المحادثة",
                         on_click=delete_conv, args=(c["id"],), width="stretch")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 6) الواجهة
# ═══════════════════════════════════════════════════════════════
tab_ai, tab_human = st.tabs(["المستشار العقاري الذكي", "الدعم البشري وحجز تذكرة"])

# ─────────────── التبويب الأول: المستشار ───────────────
with tab_ai:
    col_chat, col_side = st.columns([2.2, 1])
    active = BY_ID.get(st.session_state.active_prop_id)

    with col_chat:
        llm_on = HAS_GEMINI and bool(get_api_key())
        llm_error = st.session_state.get("llm_error")

        if llm_on and not llm_error:
            mode = '<i class="fa-solid fa-circle"></i> يعمل بنموذج Gemini 3.5 Flash'
        elif llm_error:
            mode = '<i class="fa-solid fa-circle"></i> تعذر الاتصال بـ Gemini، المحرك المحلي يعمل'
        elif not HAS_GEMINI:
            mode = '<i class="fa-solid fa-circle"></i> مكتبة Gemini غير مثبتة، المحرك المحلي يعمل'
        else:
            mode = '<i class="fa-solid fa-circle"></i> مفتاح Gemini غير موجود، المحرك المحلي يعمل'

        st.markdown(
            '<div class="box"><div class="advisor-head"><div class="advisor-avatar"><i class="fa-solid fa-user-tie"></i></div>'
            '<div><div class="advisor-name">المستشار العقاري الذكي</div>'
            f'<div class="advisor-desc">يعرف بيانات {len(PROPS)} وحدة بالكامل، ويرشح لك الأنسب لميزانيتك على مدار الساعة.</div>'
            f'<span class="mode-chip">{mode}</span></div></div></div>',
            unsafe_allow_html=True,
        )

        if llm_error:
            with st.expander("تفاصيل مشكلة الاتصال بـ Gemini"):
                st.code(llm_error, language="text")
        elif not HAS_GEMINI:
            with st.expander("كيفية تفعيل Gemini"):
                st.code("python -m pip install -U google-genai", language="bash")
        elif not get_api_key():
            with st.expander("كيفية إعداد مفتاح Gemini"):
                st.write("أضف GEMINI_API_KEY إلى ملف .env أو إلى Streamlit Secrets.")

        # حاوية الرسائل بارتفاع ثابت: بتسكرول جواها، وبتنزل لآخر رسالة تلقائياً
        msgs = st.container(height=520, key="chat_scroll")

        if active:
            chips = [("السعر وخطة السداد", "كام السعر وخطة السداد؟"), ("المميزات والتشطيب", "إيه المميزات والتشطيب؟"),
                     ("وحدات مشابهة", "رشح لي وحدات مشابهة"), ("حجز معاينة", "عايز أحجز معاينة")]
        else:
            chips = [("أرخص الوحدات", "ما هي أرخص الوحدات المتاحة؟"),
                     ("شقة 3 غرف في التجمع", "شقة 3 غرف في التجمع بحد أقصى 6 مليون"),
                     ("جاهزة للتسليم", "عايز وحدات جاهزة للتسليم"), ("أفضل استثمار", "ما أفضل وحدة للاستثمار؟"),
                     ("شاليهات الساحل", "شاليه في الساحل الشمالي")]
        for i, (col, (label, q)) in enumerate(zip(st.columns(len(chips)), chips)):
            col.button(label, key=f"chip_{i}", on_click=set_prompt, args=(q,), width="stretch")

        typed = st.chat_input("اكتب استفسارك العقاري هنا...")
        prompt = st.session_state.pop("pending_prompt", None) or typed
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt, "ids": []})
            with st.spinner("المستشار يحلل طلبك…"):
                reply, ids = respond(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply, "ids": ids})
            if current_user():
                persist_turn(current_user(), prompt, reply, ids)
            active = BY_ID.get(st.session_state.active_prop_id)

        with msgs:
            for idx, m in enumerate(st.session_state.messages):
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
                    recs = [BY_ID[i] for i in m.get("ids", []) if i in BY_ID]
                    if recs:
                        for col, p in zip(st.columns(3), recs):
                            with col:
                                st.markdown(mini_card(p), unsafe_allow_html=True)
                                st.button("اسأل عنها", key=f"rec_{idx}_{p['id']}", icon=":material/chat:",
                                          on_click=select_property, args=(p["id"],), width="stretch")

        auto_scroll()

        st.button("محادثة جديدة", icon=":material/refresh:", on_click=new_chat)

    with col_side:
        history_box()

        if active:
            finishing = active.get("finishing", "أولترا لوكس")
            status = active.get("status", "جاهز")
            chips_html = (f'<span class="chip">{active["type"]}</span><span class="chip">{finishing}</span>'
                          f'<span class="chip">{status}</span><span class="chip">{floor_text(active)}</span>')
            st.markdown(
                '<div class="box">'
                '<div class="box-title"><i class="fa-solid fa-circle-info" style="color:var(--color-accent)"></i> الوحدة المختارة</div>'
                f'<div class="sel-img" style="background-image:url({active["main_image"]})"></div>'
                f'<div class="sel-title">{active["title"]}</div>'
                f'<div class="sel-loc"><i class="fa-solid fa-location-dot"></i> {active["location"]} · وحدة #{active["id"]}</div>'
                f'<div class="sel-price">{active["price"]} ج.م</div>'
                '<div class="sel-specs">'
                f'<span><i class="fa-solid fa-bed"></i> {active["beds"]} غرف</span>'
                f'<span><i class="fa-solid fa-bath"></i> {active["baths"]} حمام</span>'
                f'<span><i class="fa-solid fa-ruler-combined"></i> {active["area"]} م²</span></div>'
                f'<div>{chips_html}</div></div>',
                unsafe_allow_html=True,
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("حاسبة التمويل", icon=":material/calculate:", type="primary", width="stretch"):
                    go_calculator(active)
            with b2:
                st.button("إلغاء الاختيار", icon=":material/close:", on_click=clear_active, width="stretch")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="box"><div class="box-title"><i class="fa-solid fa-lightbulb" style="color:var(--color-accent)"></i> جرّب أن تسأل</div>'
                '<div class="info-row"><i class="fa-solid fa-angle-left"></i><div>شقة 3 غرف في التجمع بحد أقصى 6 مليون</div></div>'
                '<div class="info-row"><i class="fa-solid fa-angle-left"></i><div>فيلا في الشيخ زايد بميزانية 15 مليون</div></div>'
                '<div class="info-row"><i class="fa-solid fa-angle-left"></i><div>أرخص وحدة جاهزة للتسليم</div></div>'
                '<div class="info-row" style="margin-bottom:0"><i class="fa-solid fa-angle-left"></i><div>ما أفضل وحدة للاستثمار؟</div></div></div>',
                unsafe_allow_html=True,
            )
        contact_box()

# ─────────────── التبويب الثاني: الدعم البشري ───────────────
with tab_human:
    col_form, col_info = st.columns([1.2, 1])

    with col_form:
        st.markdown(
            '<div class="box"><div class="advisor-head"><div class="advisor-avatar"><i class="fa-solid fa-headset"></i></div>'
            '<div><div class="advisor-name">حجز تذكرة استشارة</div>'
            '<div class="advisor-desc">سجّل بياناتك وسيتواصل معك أحد مستشارينا خلال ساعات العمل.</div></div></div></div>',
            unsafe_allow_html=True,
        )
        active_for_ticket = BY_ID.get(st.session_state.active_prop_id)
        with st.form("ticket_form", clear_on_submit=True):
            name = st.text_input("الاسم بالكامل", value=(current_user() or {}).get("name", ""))
            phone = st.text_input("رقم الهاتف أو الواتساب", placeholder="01012345678")
            topic = st.selectbox("نوع الطلب", ["طلب معاينة على الطبيعة", "استفسار عن خطط التقسيط والتمويل",
                                              "طلب المخططات الهندسية", "استشارة استثمارية عامة"])
            default_note = f"بخصوص الوحدة #{active_for_ticket['id']} - {active_for_ticket['title']}" if active_for_ticket else ""
            notes = st.text_area("تفاصيل الطلب أو أوقات التواصل المناسبة", value=default_note)
            submitted = st.form_submit_button("إرسال التذكرة", icon=":material/send:", type="primary", width="stretch")

        if submitted:
            clean_phone = re.sub(r"[\s\-+]", "", norm(phone))
            if not name.strip():
                st.error("اكتب اسمك لنتمكن من التواصل معك.")
            elif not re.fullmatch(r"(?:20)?0?1[0125]\d{8}", clean_phone):
                st.error("رقم الهاتف غير صحيح. اكتب رقم موبايل مصري مثل 01012345678.")
            else:
                tid = save_ticket({
                    "name": name.strip(), "phone": clean_phone, "topic": topic, "notes": notes.strip(),
                    "property_id": active_for_ticket["id"] if active_for_ticket else None,
                })
                st.success(f"تم تسجيل تذكرتك برقم {tid}. سيتواصل معك أحد المستشارين قريباً.")

    with col_info:
        contact_box()
        st.markdown("<div class='box-title'>أسئلة شائعة</div>", unsafe_allow_html=True)
        faqs = [
            ("كيف أحجز معاينة؟", "سجّل تذكرة من النموذج أو راسلنا على واتساب، وسنحدد معك موعداً مناسباً."),
            ("ما هي خطط السداد؟", "مقدم تقديري 10% وباقي المبلغ على أقساط تصل إلى 8 سنوات، وتختلف حسب الوحدة."),
            ("هل أستطيع الاستفسار عن أكثر من وحدة؟", "نعم، اسأل المستشار الذكي عن أي وحدة برقمها أو اطلب ترشيحات حسب ميزانيتك."),
            ("كيف أصل إلى الدعم؟", "عبر الواتساب أو الهاتف خلال ساعات العمل، أو بتسجيل تذكرة في أي وقت."),
        ]
        for q, a in faqs:
            with st.expander(q):
                st.write(a)