import json
import re
from collections import Counter

import pandas as pd
import streamlit as st

import auth
import db
import session
from utils import esc, safe

st.set_page_config(
    page_title="لوحة الإدارة | Aqarify",
    page_icon=":material/tune:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

session.restore_login()  # يرجّع تسجيل الدخول بعد Refresh

ss = st.session_state

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

    html, body, .stApp { direction: rtl; }
    .stApp [data-testid="stMarkdownContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: var(--color-bg); color: var(--color-dark); }
    .stApp *:not(i):not([data-testid="stIconMaterial"]) { font-family: 'Cairo', sans-serif !important; }

    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 7rem; max-width: 1280px; }

    /* ─── الشعار ─── */
    .brand-logo-link { display: inline-flex; align-items: center; gap: 14px; }
    .brand-icon-box {
        background: var(--color-dark); color: var(--color-accent); width: 52px; height: 52px; border-radius: 14px;
        border: 1px solid var(--color-dark); box-shadow: 0 6px 16px rgba(20,22,28,.18);
        display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;
    }
    .brand-logo-text { font-size: 34px; font-weight: 800; color: var(--color-dark); line-height: 1; margin: 0; }
    .brand-logo-dot { color: var(--color-accent); }
    .brand-logo-sub { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; display: block; }

    /* ─── شريط التنقل ─── */
    .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: wrap;
        justify-content: flex-end; align-items: center; gap: 22px !important; padding-top: 14px;
    }
    .st-key-topnav [data-testid="stElementContainer"],
    .st-key-topnav [data-testid="stPageLink"] { width: auto !important; flex: 0 0 auto !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"] {
        position: relative; display: inline-flex !important; align-items: center; gap: 8px;
        background: transparent !important; padding: 8px 0 !important; border-radius: 0 !important;
        color: var(--color-dark) !important; text-decoration: none !important; transition: color .2s ease;
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"] p {
        font-size: 16px !important; font-weight: 700 !important; color: inherit !important; margin: 0 !important;
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"]::before {
        font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important; font-size: 15px; width: 18px; text-align: center; content: "\\f015";
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Properties"]::before { content: "\\f64f"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Customer"]::before   { content: "\\f508"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Calculator"]::before { content: "\\f1ec"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Admin"]::before      { content: "\\f1de"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Company"]::before    { content: "\\f1ad"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]:hover { color: var(--color-accent) !important; background: transparent !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Admin"] { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Admin"]::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent);
    }

    /* ─── عناصر الإدارة ─── */
    .box { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 20px; padding: 22px; margin-bottom: 16px; }
    .box-title { font-size: 17px; font-weight: 800; margin-bottom: 14px; }
    .box-title i { color: var(--color-accent); margin-left: 8px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }
    .kpi { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 16px; padding: 18px; transition: all .25s ease; }
    .kpi:hover { transform: translateY(-3px); border-color: var(--color-accent); box-shadow: 0 10px 22px rgba(0,0,0,.06); }
    .kpi-icon { width: 40px; height: 40px; border-radius: 12px; background: var(--color-dark); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-size: 17px; }
    .kpi-val { font-size: 24px; font-weight: 800; margin-top: 10px; line-height: 1.1; }
    .kpi-lbl { font-size: 13px; color: var(--color-text-muted); margin-top: 2px; }
    .tk-row { display: flex; justify-content: space-between; gap: 12px; padding: 12px 0; border-bottom: 1px dashed var(--color-border); font-size: 14px; }
    .tk-row:last-child { border-bottom: none; }
    .tk-row small { color: var(--color-text-muted); display: block; }
    .badge { display: inline-block; border-radius: 20px; padding: 2px 12px; font-size: 12px; font-weight: 700; border: 1px solid var(--color-border); background: var(--color-white); white-space: nowrap; }
    .badge.new { background: var(--color-dark); color: var(--color-accent); border-color: var(--color-dark); }
    .badge.prog { background: #F6EBCB; border-color: #F6EBCB; }

    /* ─── التبويبات ─── */
    .stTabs [role="tablist"] {
        display: inline-flex; width: fit-content; max-width: 100%; gap: 4px; padding: 4px; margin-bottom: 12px;
        background: rgba(255,255,255,.78); border: 1px solid var(--color-border) !important; border-radius: 14px;
        box-shadow: 0 6px 20px rgba(20,22,28,.05);
    }
    .stTabs [role="tablist"] > div:empty, .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }
    .stTabs [role="tab"] {
        height: 38px; padding: 0 18px; border: none !important; border-radius: 10px;
        background: transparent !important; color: var(--color-dark); transition: all .22s ease;
    }
    .stTabs [role="tab"] p { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 14px; font-weight: 700; color: inherit; }
    .stTabs [role="tab"]:hover { background: rgba(201,162,75,.14) !important; }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #23262F, #14161C) !important;
        box-shadow: 0 5px 12px rgba(20,22,28,.22), inset 0 0 0 1px rgba(201,162,75,.5);
    }
    .stTabs [role="tab"][aria-selected="true"] p, .stTabs [role="tab"][aria-selected="true"] [data-testid="stIconMaterial"] { color: var(--color-accent) !important; }

    /* ─── الأزرار الموحدة: عدّل هذا القسم فقط عند توحيد التصميم ─── */
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-secondaryFormSubmit"], [data-testid="stBaseButton-primaryFormSubmit"],
    [data-testid="stDownloadButton"] button {
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

    @media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
    /* ─── تحسينات التجاوب مع الهواتف الذكية (Mobile Responsive) ─── */
    @media (max-width: 768px) {
        .stTabs [role="tablist"] { width: 100%; }
        .stTabs [role="tab"] { flex: 1; justify-content: center; padding: 0 8px; }
        .block-container {
            padding-top: 5rem !important;
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
# 2) الهيدر الموحد
# ═══════════════════════════════════════════════════════════════
import base64, os
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
with open(LOGO_PATH, "rb") as _f:
    LOGO_B64 = base64.b64encode(_f.read()).decode()

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
        if ss.get("is_admin_logged_in", False):
            st.page_link("pages/Admin.py", label="لوحة الإدارة")
        if (st.session_state.get("user") or {}).get("role") == "company":
            st.page_link("pages/Company.py", label="لوحة الشركة")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3) الحماية: لازم مستخدم مسجّل دخول بصلاحية admin
# ═══════════════════════════════════════════════════════════════
current_user = session.require_role("admin")

if not db.DB_FILE.exists():
    st.error("قاعدة البيانات غير موجودة. شغّل: python migrate.py")
    st.stop()

db.init_tickets_table()

# ═══════════════════════════════════════════════════════════════
# 4) منطق البيانات
# ═══════════════════════════════════════════════════════════════
# ===== LOGIC START =====
STATUSES = ["جاهز للتسليم", "تحت الإنشاء"]
FINISHES = ["ألترا سوبر لوكس", "سوبر لوكس", "تشطيب كامل", "نصف تشطيب"]
TK_STATUSES = ["جديدة", "قيد المتابعة", "مكتملة"]
DEFAULT_IMG = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"


def build_unit(uid, f):
    price = int(f["price"])
    city = f["city_new"].strip() or f["city"]
    compound = f["compound"].strip()
    feats = list(f["features"]) + [x.strip() for x in re.split(r"[،,]", f["feat_extra"]) if x.strip()]
    title = f["title"].strip() or f"{f['type']} للبيع في {compound}"
    area, beds, baths = int(f["area"]), int(f["beds"]), int(f["baths"])
    desc = f["desc"].strip() or (f"{f['type']} بمساحة {area} م² و{beds} غرفة نوم و{baths} حمام داخل {compound} في {city}.")
    gallery = [g.strip() for g in (f["g1"], f["g2"]) if g.strip()]
    return {
        "id": uid, "company_id": f.get("company_id"), "title": title, "type": f["type"], "city": city, "compound": compound,
        "location": f"{city} - {compound}", "price_val": price, "price": f"{price:,}",
        "beds": beds, "baths": baths, "area": area,
        "floor": None if int(f["floor"]) == 0 else int(f["floor"]),
        "finishing": f["finishing"], "status": f["status"], "delivery": f["delivery"].strip() or "فوري",
        "features": feats, "main_image": f["main_image"].strip() or DEFAULT_IMG,
        "gallery": gallery or [DEFAULT_IMG, DEFAULT_IMG], "desc": desc,
    }


def validate(f):
    if not f.get("company_id"):
        return "اختر الشركة المالكة (أضف شركة من تبويب الشركات لو القائمة فاضية)."
    if not f["compound"].strip():
        return "اكتب اسم الكمبوند أو المشروع."
    if int(f["price"]) <= 0 or int(f["area"]) <= 0:
        return "السعر والمساحة يجب أن يكونا أكبر من صفر."
    return None
# ===== LOGIC END =====

props = db.list_properties_legacy()
tickets = [{**t, "pk": t["id"], "id": t["code"]} for t in db.list_tickets()]
BY_ID = {p["id"]: p for p in props}
COMPANIES = db.list_companies()
COMP_BY_ID = {c["id"]: c for c in COMPANIES}

TYPES = sorted({p["type"] for p in props} | {"شقة", "فيلا", "دوبلكس", "تاون هاوس", "بنتهاوس", "شاليه", "استوديو"})
CITIES = sorted({p["city"] for p in props} or {"التجمع الخامس"})
FEATURE_OPTS = sorted({f for p in props for f in p.get("features", [])})


def flash(kind, msg):
    ss.admin_flash = (kind, msg)


def show_flash():
    f = ss.pop("admin_flash", None)
    if f:
        {"success": st.success, "error": st.error, "info": st.info}[f[0]](f[1])


def money(v):
    return f"{int(round(v)):,}"


# ═══════════════════════════════════════════════════════════════
# 5) رأس الصفحة
# ═══════════════════════════════════════════════════════════════
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown("<h2 style='font-weight:800; font-size:32px; margin-bottom:2px;'>لوحة الإدارة</h2>"
                f"<p style='color:var(--color-text-muted); font-size:16px;'>مرحباً {esc(current_user['name'])}، "
                "إدارة الوحدات ومتابعة التذاكر ومؤشرات الأداء في مكان واحد.</p>",
                unsafe_allow_html=True)
with h2:
    st.button("تسجيل الخروج", icon=":material/logout:", on_click=session.logout_user, width="stretch")
show_flash()

tab_dash, tab_units, tab_companies, tab_tickets = st.tabs(["المؤشرات", "إدارة الوحدات", "الشركات", "التذاكر"])

# ═══════════════════════════════════════════════════════════════
# 6) المؤشرات
# ═══════════════════════════════════════════════════════════════
with tab_dash:
    total_val = sum(p["price_val"] for p in props)
    avg = total_val / len(props) if props else 0
    ready = sum(1 for p in props if p["status"] == "جاهز للتسليم")
    new_tk = sum(1 for t in tickets if t["status"] == "جديدة")
    kpis = [
        ("fa-building", f"{len(props)}", "إجمالي الوحدات"),
        ("fa-sack-dollar", f"{total_val / 1e9:.2f} مليار", "قيمة المحفظة (ج.م)"),
        ("fa-tags", f"{avg / 1e6:.1f} مليون", "متوسط سعر الوحدة"),
        ("fa-key", f"{ready}", "جاهزة للتسليم"),
        ("fa-ticket", f"{len(tickets)}", "إجمالي التذاكر"),
        ("fa-bell", f"{new_tk}", "تذاكر جديدة"),
        ("fa-location-dot", f"{len({p['city'] for p in props})}", "عدد المناطق"),
        ("fa-ruler-combined", f"{sum(p['area'] for p in props) / max(len(props), 1):.0f} م²", "متوسط المساحة"),
    ]
    st.markdown('<div class="kpi-grid">' + "".join(
        f'<div class="kpi"><div class="kpi-icon"><i class="fa-solid {ic}"></i></div><div class="kpi-val">{v}</div><div class="kpi-lbl">{lb}</div></div>'
        for ic, v, lb in kpis) + '</div>', unsafe_allow_html=True)

    if props:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='box-title'><i class='fa-solid fa-location-dot'></i> الوحدات حسب المنطقة</div>", unsafe_allow_html=True)
            st.bar_chart(pd.Series(Counter(p["city"] for p in props), name="الوحدات"), color="#C9A24B", height=260)
        with c2:
            st.markdown("<div class='box-title'><i class='fa-solid fa-house'></i> الوحدات حسب النوع</div>", unsafe_allow_html=True)
            st.bar_chart(pd.Series(Counter(p["type"] for p in props), name="الوحدات"), color="#14161C", height=260)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("<div class='box-title'><i class='fa-solid fa-chart-simple'></i> متوسط السعر بالمليون حسب المنطقة</div>", unsafe_allow_html=True)
            df_city = pd.DataFrame(props).groupby("city")["price_val"].mean() / 1e6
            st.bar_chart(df_city.rename("متوسط السعر (مليون)"), color="#C9A24B", height=260)
        with c4:
            st.markdown("<div class='box-title'><i class='fa-solid fa-ticket'></i> التذاكر حسب نوع الطلب</div>", unsafe_allow_html=True)
            if tickets:
                st.bar_chart(pd.Series(Counter(t["topic"] for t in tickets), name="التذاكر"), color="#14161C", height=260)
            else:
                st.info("لا توجد تذاكر بعد.")

    rows = ""
    for t in map(safe, tickets[-5:][::-1]):
        cls = "new" if t["status"] == "جديدة" else ("prog" if t["status"] == "قيد المتابعة" else "")
        rows += (f'<div class="tk-row"><div><b>{t["name"]}</b> · {t["phone"]}<small>{t["topic"]} · {t.get("created_at", "")}</small></div>'
                 f'<span class="badge {cls}">{t["status"]}</span></div>')
    st.markdown("<div class='box'><div class='box-title'><i class='fa-solid fa-clock-rotate-left'></i> آخر التذاكر</div>"
                + (rows or "<div style='color:var(--color-text-muted)'>لا توجد تذاكر بعد.</div>") + "</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 7) إدارة الوحدات (على قاعدة البيانات)
# ═══════════════════════════════════════════════════════════════
def unit_form(form_key, u=None):
    d = u or {}
    with st.form(form_key, clear_on_submit=u is None):
        a, b = st.columns(2)
        with a:
            utype = st.selectbox("نوع الوحدة", TYPES, index=TYPES.index(d["type"]) if d.get("type") in TYPES else 0)
            comp_ids = [c["id"] for c in COMPANIES]
            company_id = st.selectbox(
                "الشركة المالكة", comp_ids, format_func=lambda i: COMP_BY_ID[i]["name"],
                index=comp_ids.index(d["company_id"]) if d.get("company_id") in comp_ids else 0) if comp_ids else None
            city = st.selectbox("المنطقة", CITIES, index=CITIES.index(d["city"]) if d.get("city") in CITIES else 0)
            city_new = st.text_input("منطقة جديدة (اختياري، تتجاوز الاختيار أعلاه)")
            compound = st.text_input("الكمبوند أو المشروع", value=d.get("compound", ""))
            title = st.text_input("عنوان الإعلان (اختياري، يُولَّد تلقائياً)", value=d.get("title", ""))
            price = st.number_input("السعر (ج.م)", 100_000, 200_000_000, int(d.get("price_val", 3_000_000)), 50_000)
            area = st.number_input("المساحة (م²)", 20, 5000, int(d.get("area", 150)), 5)
        with b:
            beds = st.number_input("غرف النوم", 1, 15, int(d.get("beds", 3)))
            baths = st.number_input("الحمامات", 1, 15, int(d.get("baths", 2)))
            floor = st.number_input("الدور (0 = أرضي)", 0, 60, int(d.get("floor") or 0))
            finishing = st.selectbox("التشطيب", FINISHES, index=FINISHES.index(d["finishing"]) if d.get("finishing") in FINISHES else 0)
            status = st.selectbox("الحالة", STATUSES, index=STATUSES.index(d["status"]) if d.get("status") in STATUSES else 0)
            delivery = st.text_input("موعد الاستلام", value=d.get("delivery", "فوري"))
            features = st.multiselect("المميزات", FEATURE_OPTS, default=[x for x in d.get("features", []) if x in FEATURE_OPTS])
            feat_extra = st.text_input("مميزات إضافية (افصل بفاصلة)")
        main_image = st.text_input("رابط الصورة الرئيسية", value=d.get("main_image", ""))
        g = d.get("gallery", ["", ""]) + ["", ""]
        g1 = st.text_input("رابط صورة داخلية 1", value=g[0])
        g2 = st.text_input("رابط صورة داخلية 2", value=g[1])
        desc = st.text_area("الوصف (اختياري، يُولَّد تلقائياً)", value=d.get("desc", ""))
        sub = st.form_submit_button("حفظ التعديلات" if u else "إضافة الوحدة", icon=":material/save:",
                                    type="primary", width="stretch")
    if sub:
        return {"company_id": company_id, "type": utype, "city": city, "city_new": city_new, "compound": compound, "title": title,
                "price": price, "area": area, "beds": beds, "baths": baths, "floor": floor,
                "finishing": finishing, "status": status, "delivery": delivery, "features": features,
                "feat_extra": feat_extra, "main_image": main_image, "g1": g1, "g2": g2, "desc": desc}
    return None


with tab_units:
    sub_list, sub_add, sub_edit = st.tabs(["عرض الوحدات", "إضافة وحدة", "تعديل أو حذف"])

    with sub_list:
        f1, f2, f3 = st.columns([2, 1, 1])
        q = f1.text_input("بحث (رقم الوحدة، الكمبوند، المنطقة)", key="adm_q")
        tf = f2.selectbox("النوع", ["الكل"] + TYPES, key="adm_t")
        sf = f3.selectbox("الحالة", ["الكل"] + STATUSES, key="adm_s")
        view = [p for p in props
                if (tf == "الكل" or p["type"] == tf) and (sf == "الكل" or p["status"] == sf)
                and (not q or q.strip().lstrip("#") == str(p["id"]) or q in p["title"] or q in p["location"])]
        df = pd.DataFrame([{
            "#": p["id"], "الشركة": p.get("company_name") or "—", "العنوان": p["title"], "النوع": p["type"], "الموقع": p["location"],
            "السعر": money(p["price_val"]), "المساحة": p["area"], "الغرف": p["beds"],
            "الحالة": p["status"], "الاستلام": p["delivery"],
        } for p in view])
        st.caption(f"{len(view)} وحدة من أصل {len(props)}")
        st.dataframe(df, width="stretch", hide_index=True, height=380)
        st.download_button("تنزيل نسخة احتياطية (JSON)", json.dumps(props, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name="properties_backup.json", mime="application/json", icon=":material/download:")

    with sub_add:
        st.caption(f"رقم الوحدة الجديدة سيكون #{db.next_property_id()}")
        data = unit_form("add_form")
        if data:
            err = validate(data)
            if err:
                st.error(err)
            else:
                new_id = db.add_property(build_unit(None, data))
                flash("success", f"تمت إضافة الوحدة #{new_id}، وستظهر في المعرض والمستشار فوراً.")
                st.rerun()

    with sub_edit:
        if not props:
            st.info("لا توجد وحدات لتعديلها.")
        else:
            uid = st.selectbox("اختر الوحدة", [p["id"] for p in props], key="adm_edit_id",
                               format_func=lambda i: f"#{i} · {BY_ID[i]['title']} · {BY_ID[i]['location']}")
            cur = BY_ID[uid]
            st.markdown(f'<div style="height:130px;width:220px;border-radius:14px;margin-bottom:12px;background-size:cover;'
                        f'background-position:center;background-color:var(--color-border);background-image:url({esc(cur["main_image"])})"></div>',
                        unsafe_allow_html=True)
            data = unit_form(f"edit_form_{uid}", cur)
            if data:
                err = validate(data)
                if err:
                    st.error(err)
                else:
                    if db.update_property(uid, build_unit(uid, data)):
                        flash("success", f"تم تحديث الوحدة #{uid}.")
                    else:
                        flash("error", f"الوحدة #{uid} غير موجودة.")
                    st.rerun()

            st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-trash'></i> حذف الوحدة</div>", unsafe_allow_html=True)
            sure = st.checkbox(f"أؤكد رغبتي في حذف الوحدة #{uid} نهائياً", key=f"del_ok_{uid}")
            if st.button("حذف الوحدة", icon=":material/delete:", disabled=not sure, key=f"del_btn_{uid}"):
                backup = db.backup_db()
                if db.delete_property(uid):
                    flash("success", f"تم حذف الوحدة #{uid}. نسخة احتياطية: {backup.name if backup else '—'} (داخل فولدر backups).")
                else:
                    flash("error", f"الوحدة #{uid} غير موجودة.")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# 8) التذاكر
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# 7-ب) الشركات (marketplace): كل شركة لها حساب وبتضيف وحداتها
# ═══════════════════════════════════════════════════════════════
with tab_companies:
    sub_clist, sub_cadd = st.tabs(["الشركات الحالية", "إضافة شركة"])

    with sub_clist:
        if not COMPANIES:
            st.info("لا توجد شركات بعد. أضف أول شركة من تبويب «إضافة شركة».")
        else:
            st.dataframe(pd.DataFrame([{
                "#": c["id"], "الشركة": c["name"], "الوحدات": c["units"], "الحسابات": c["accounts"],
            } for c in COMPANIES]), width="stretch", hide_index=True, height=260)

            cid = st.selectbox("اختر شركة", [c["id"] for c in COMPANIES], key="adm_comp_sel",
                               format_func=lambda i: COMP_BY_ID[i]["name"])
            cc = COMP_BY_ID[cid]
            with st.form(f"comp_edit_{cid}"):
                e_name = st.text_input("اسم الشركة", value=cc["name"])
                e_logo = st.text_input("رابط الشعار (اختياري)", value=cc["logo_url"])
                e_desc = st.text_area("نبذة عن الشركة (اختياري)", value=cc["description"])
                save_c = st.form_submit_button("حفظ بيانات الشركة", icon=":material/save:",
                                               type="primary", width="stretch")
            if save_c:
                if not e_name.strip():
                    st.error("اسم الشركة مطلوب.")
                elif db.update_company(cid, e_name, e_logo, e_desc):
                    flash("success", f"تم تحديث الشركة #{cid}.")
                    st.rerun()
                else:
                    st.error("هذا الاسم مستخدم لشركة أخرى.")

            st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-user-tie'></i> حسابات الشركة</div>",
                        unsafe_allow_html=True)
            accts = db.list_company_accounts(cid)
            if accts:
                st.dataframe(pd.DataFrame([{"الاسم": x["name"], "البريد": x["email"]} for x in accts]),
                             width="stretch", hide_index=True)
            else:
                st.caption("لا يوجد حساب لهذه الشركة بعد، فلن تستطيع إضافة وحدات.")
            with st.form(f"comp_acct_{cid}", clear_on_submit=True):
                a_name = st.text_input("اسم المسؤول")
                a_email = st.text_input("البريد الإلكتروني")
                a_pw = st.text_input("كلمة المرور (8 أحرف على الأقل)", type="password")
                add_a = st.form_submit_button("إنشاء حساب للشركة", icon=":material/person_add:", width="stretch")
            if add_a:
                ok, msg = auth.create_user(a_name, a_email, a_pw, role="user", company_id=cid)
                if ok:
                    flash("success", f"تم إنشاء حساب للشركة: {a_email.strip().lower()}")
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-trash'></i> حذف الشركة</div>",
                        unsafe_allow_html=True)
            sure_c = st.checkbox("أؤكد رغبتي في حذف هذه الشركة نهائياً", key=f"comp_del_ok_{cid}")
            if st.button("حذف الشركة", icon=":material/delete:", disabled=not sure_c, key=f"comp_del_{cid}"):
                ok, msg = db.delete_company(cid)
                flash("success" if ok else "error", f"تم حذف الشركة #{cid}." if ok else msg)
                st.rerun()

    with sub_cadd:
        with st.form("comp_add_form", clear_on_submit=True):
            n_name = st.text_input("اسم الشركة")
            n_logo = st.text_input("رابط الشعار (اختياري)")
            n_desc = st.text_area("نبذة عن الشركة (اختياري)")
            st.markdown("<div class='box-title' style='margin-top:8px;'>حساب الشركة (اختياري الآن، ويمكن إضافته لاحقاً)</div>",
                        unsafe_allow_html=True)
            n_acc_name = st.text_input("اسم المسؤول", key="n_acc_name")
            n_acc_email = st.text_input("البريد الإلكتروني", key="n_acc_email")
            n_acc_pw = st.text_input("كلمة المرور (8 أحرف على الأقل)", type="password", key="n_acc_pw")
            add_c = st.form_submit_button("إضافة الشركة", icon=":material/add_business:",
                                          type="primary", width="stretch")
        if add_c:
            want_acct = bool(n_acc_email.strip() or n_acc_pw or n_acc_name.strip())
            new_cid = db.create_company(n_name, n_logo, n_desc)
            if new_cid is None:
                st.error("اسم الشركة فاضي أو مستخدم قبل كده.")
            elif want_acct:
                ok, msg = auth.create_user(n_acc_name, n_acc_email, n_acc_pw, role="user", company_id=new_cid)
                if ok:
                    flash("success", "تمت إضافة الشركة وإنشاء حسابها.")
                    st.rerun()
                else:
                    db.delete_company(new_cid)
                    st.error(msg)
            else:
                flash("success", "تمت إضافة الشركة.")
                st.rerun()

with tab_tickets:
    if not tickets:
        st.info("لا توجد تذاكر حتى الآن. ستظهر هنا التذاكر التي يسجلها العملاء من صفحة المستشار.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("جديدة", sum(1 for t in tickets if t["status"] == "جديدة"))
        m2.metric("قيد المتابعة", sum(1 for t in tickets if t["status"] == "قيد المتابعة"))
        m3.metric("مكتملة", sum(1 for t in tickets if t["status"] == "مكتملة"))

        flt = st.selectbox("تصفية حسب الحالة", ["الكل"] + TK_STATUSES, key="tk_filter")
        shown = [t for t in tickets if flt == "الكل" or t["status"] == flt][::-1]

        def prop_label(t):
            pid = t.get("property_id")
            if not pid:
                return "—"
            title = t.get("property_title") or (BY_ID[pid]["title"] if pid in BY_ID else "")
            return f"#{pid} {title}".strip()

        dft = pd.DataFrame([{
            "رقم التذكرة": t["id"], "الشركة": COMP_BY_ID.get(t.get("company_id"), {}).get("name", "—"), "الاسم": t["name"], "الهاتف": t["phone"], "نوع الطلب": t["topic"],
            "الوحدة": prop_label(t), "الحالة": t["status"],
            "التاريخ": t.get("created_at", ""), "ملاحظات": t.get("notes", ""),
        } for t in shown])
        st.dataframe(dft, width="stretch", hide_index=True, height=340)
        st.download_button("تنزيل التذاكر (CSV)", dft.to_csv(index=False).encode("utf-8-sig"),
                           file_name="aqarify_tickets.csv", mime="text/csv", icon=":material/download:")

        st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-pen-to-square'></i> تحديث تذكرة</div>", unsafe_allow_html=True)
        tid = st.selectbox("اختر التذكرة", [t["id"] for t in tickets][::-1], key="tk_sel")
        cur_t = next(t for t in tickets if t["id"] == tid)
        ct = safe(cur_t)
        st.markdown(f'<div class="box"><b>{ct["name"]}</b> · {ct["phone"]}<br>'
                    f'<span style="color:var(--color-text-muted)">{ct["topic"]} · {esc(prop_label(cur_t))}</span><br>'
                    f'{ct.get("notes", "") or "بدون ملاحظات"}</div>', unsafe_allow_html=True)
        new_status = st.selectbox("الحالة الجديدة", TK_STATUSES, index=TK_STATUSES.index(cur_t["status"]), key=f"tk_status_{tid}")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("حفظ الحالة", icon=":material/check:", type="primary", width="stretch", key=f"tk_save_{tid}"):
                db.update_ticket_status(cur_t["pk"], new_status)
                flash("success", f"تم تحديث التذكرة {tid}.")
                st.rerun()
        with b2:
            if st.button("حذف التذكرة", icon=":material/delete:", width="stretch", key=f"tk_del_{tid}"):
                db.delete_ticket(cur_t["pk"])
                flash("success", f"تم حذف التذكرة {tid}.")
                st.rerun()