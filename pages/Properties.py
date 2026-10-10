import json
import math
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="معرض العقارات | Aqarify",
    page_icon=":material/apartment:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════
# 1) التنسيق (نفس ألوان وهوية الصفحة الرئيسية)
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
    .stApp [data-testid="stMarkdownContainer"],
    [data-testid="stDialog"] [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    .stApp, [data-testid="stDialog"] div[role="dialog"] {
        background-color: var(--color-bg);
        color: var(--color-dark);
    }
    .stApp *:not(i):not([data-testid="stIconMaterial"]),
    [data-testid="stDialog"] *:not(i):not([data-testid="stIconMaterial"]) {
        font-family: 'Cairo', sans-serif !important;
    }

    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 1280px; }

    /* ─── الشعار (نفس شكل الصفحة الرئيسية) ─── */
    .brand-logo-link { display: inline-flex; align-items: center; gap: 14px; }
    .brand-icon-box {
        background: #F0EFEA; color: var(--color-dark);
        width: 52px; height: 52px; border-radius: 14px;
        border: 1px solid var(--color-border);
        box-shadow: 0 4px 12px rgba(20, 22, 28, 0.06);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; flex-shrink: 0;
    }
    .brand-logo-text { font-size: 34px; font-weight: 800; color: var(--color-dark); line-height: 1; margin: 0; }
    .brand-logo-dot { color: var(--color-accent); }
    .brand-logo-sub { font-size: 13px; font-weight: 400; color: var(--color-text-muted); margin-top: 4px; display: block; }

    /* ─── شريط التنقل (نفس شكل الصفحة الرئيسية، ويحافظ على الجلسة) ─── */
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
        font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important;
        font-size: 16px; content: "\\f015";
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Properties"]::before { content: "\\f64f"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Customer"]::before   { content: "\\f508"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Calculator"]::before { content: "\\f1ec"; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Admin"]::before      { content: "\\f1de"; }

    .st-key-topnav [data-testid="stPageLink-NavLink"]:hover { color: var(--color-accent) !important; background: transparent !important; }
    /* الصفحة الحالية = معرض العقارات */
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Properties"] { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Properties"]::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent);
    }

    /* ─── شريط الإحصائيات ─── */
    .stat-box {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 16px; padding: 16px 18px; display: flex; align-items: center; gap: 14px;
    }
    .stat-icon {
        width: 44px; height: 44px; border-radius: 12px; background: var(--color-dark);
        color: var(--color-accent); display: flex; align-items: center; justify-content: center;
        font-size: 18px; flex-shrink: 0;
    }
    .stat-num { font-size: 22px; font-weight: 800; line-height: 1.1; }
    .stat-label { font-size: 13px; color: var(--color-text-muted); }

    /* ─── كروت العقارات ─── */
    .prop-card-box {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 20px; overflow: hidden; margin-bottom: 10px;
        transition: all .3s ease; box-shadow: 0 4px 15px rgba(0,0,0,.03);
    }
    .prop-card-box:hover {
        transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,.08);
        border-color: var(--color-accent);
    }
    .prop-img-box { position: relative; height: 220px; width: 100%; overflow: hidden; background: var(--color-border); }
    .prop-img { width: 100%; height: 100%; background-size: cover; background-position: center; }
    .prop-badge {
        position: absolute; top: 15px; right: 15px; background: var(--color-dark);
        color: var(--color-accent); padding: 4px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 800;
    }
    .prop-status {
        position: absolute; top: 15px; left: 15px; background: var(--color-white);
        color: var(--color-dark); padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 700;
    }
    .prop-fav {
        position: absolute; bottom: 15px; left: 15px; width: 36px; height: 36px;
        border-radius: 50%; background: var(--color-dark); color: var(--color-accent);
        display: flex; align-items: center; justify-content: center;
    }
    .prop-card-content { padding: 20px; }
    .prop-card-title { font-size: 18px; font-weight: 800; margin-bottom: 6px; }
    .prop-card-location { font-size: 14px; color: var(--color-text-muted); margin-bottom: 12px; }
    .prop-card-price { font-size: 22px; font-weight: 800; color: var(--color-accent); }
    .prop-card-ppm { font-size: 13px; color: var(--color-text-muted); margin-bottom: 14px; }
    .prop-card-specs {
        display: flex; justify-content: space-between; background: #F9FAFB;
        padding: 10px 14px; border-radius: 12px; border: 1px solid var(--color-border);
        font-size: 14px; font-weight: 700; margin-bottom: 12px;
    }
    .chip {
        display: inline-block; border: 1px solid var(--color-border); border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600; margin-left: 6px; margin-top: 4px;
        color: var(--color-dark); background: var(--color-white);
    }
    .prop-id { font-size: 12px; color: var(--color-text-muted); }

    /* ─── نافذة التفاصيل ─── */
    .gal-grid { display: grid; grid-template-columns: 2fr 1fr; grid-template-rows: 1fr 1fr; gap: 8px; height: 300px; margin-bottom: 18px; }
    .gal-img { background-size: cover; background-position: center; border-radius: 14px; background-color: var(--color-border); }
    .gal-img.main { grid-row: 1 / span 2; }
    .dlg-price { font-size: 28px; font-weight: 800; color: var(--color-accent); }
    .dlg-sub { color: var(--color-text-muted); font-size: 14px; }
    .spec-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 16px 0; }
    .spec-box { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 14px; padding: 12px; text-align: center; }
    .spec-box i { color: var(--color-accent); font-size: 18px; }
    .spec-val { font-weight: 800; font-size: 17px; margin-top: 4px; }
    .spec-lbl { font-size: 12px; color: var(--color-text-muted); }
    .fin-box { background: var(--color-dark); color: var(--color-white); border-radius: 16px; padding: 16px 20px; margin: 16px 0; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .fin-box .k { font-size: 12px; opacity: .75; }
    .fin-box .v { font-size: 18px; font-weight: 800; color: var(--color-accent); }

    /* ─── الأزرار الموحدة: عدّل هذا القسم فقط عند توحيد التصميم ─── */
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
        font-weight: 700; border-radius: 12px; transition: all .2s ease;
    }
    [data-testid="stBaseButton-secondary"] {
        background: transparent; color: var(--color-dark); border: 1px solid var(--color-dark);
    }
    [data-testid="stBaseButton-secondary"]:hover {
        background: var(--color-dark); color: var(--color-white); border-color: var(--color-dark);
    }
    [data-testid="stBaseButton-primary"] {
        background: var(--color-accent); color: var(--color-dark); border: 1px solid var(--color-accent);
    }
    [data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 4px 12px rgba(201,162,75,.35); border-color: var(--color-accent);
        background: var(--color-accent); color: var(--color-dark);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2) تحميل البيانات من data/properties.json
# ═══════════════════════════════════════════════════════════════
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "properties.json"
PAGE_SIZE = 12


@st.cache_data
def load_properties(mtime):
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


if not DATA_FILE.exists():
    st.error("ملف البيانات غير موجود. تأكد من وجود data/properties.json في مجلد المشروع.")
    st.stop()

all_props = load_properties(DATA_FILE.stat().st_mtime)
st.session_state.properties_list = all_props
st.session_state.setdefault("favorites", [])
st.session_state.setdefault("prop_page", 1)

# ═══════════════════════════════════════════════════════════════
# 3) الهيدر
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
    is_admin = st.session_state.get("is_admin_logged_in", False)
    with st.container(key="topnav"):
        st.page_link("App.py", label="الرئيسية")
        st.page_link("pages/Properties.py", label="معرض العقارات")
        st.page_link("pages/Customer Service.py", label="المستشار الذكي")
        st.page_link("pages/Calculator.py", label="حاسبة التمويل")
        if is_admin:
            st.page_link("pages/Admin.py", label="لوحة الإدارة")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 4) دوال مساعدة
# ═══════════════════════════════════════════════════════════════
def toggle_fav(pid):
    favs = st.session_state.favorites
    if pid in favs:
        favs.remove(pid)
    else:
        favs.append(pid)


def go_advisor(prop):
    st.session_state["chat_property_context"] = prop["title"]
    st.session_state.active_prop_data = prop
    st.switch_page("pages/Customer Service.py")


def go_calculator(prop):
    st.session_state["selected_property_for_calc"] = {"id": prop["id"], "title": prop["title"], "price": prop["price"]}
    st.switch_page("pages/Calculator.py")


def floor_text(prop):
    return "أرضي" if prop.get("floor") in (None, 0) else f"الدور {prop['floor']}"


def card_html(p):
    img = p["main_image"]
    ppm = f"{p['price_val'] // p['area']:,}"
    heart = '<div class="prop-fav"><i class="fa-solid fa-heart"></i></div>' if p["id"] in st.session_state.favorites else ""
    return (
        '<div class="prop-card-box">'
        f'<div class="prop-img-box"><div class="prop-img" style="background-image:url({img})"></div>'
        f'<div class="prop-badge">{p["type"]}</div>'
        f'<div class="prop-status">{p["status"]}</div>{heart}</div>'
        '<div class="prop-card-content">'
        f'<div class="prop-card-title">{p["title"]}</div>'
        f'<div class="prop-card-location"><i class="fa-solid fa-location-dot"></i> {p["location"]}</div>'
        f'<div class="prop-card-price">{p["price"]} ج.م</div>'
        f'<div class="prop-card-ppm">{ppm} ج.م للمتر</div>'
        '<div class="prop-card-specs">'
        f'<span><i class="fa-solid fa-bed"></i> {p["beds"]} غرف</span>'
        f'<span><i class="fa-solid fa-bath"></i> {p["baths"]} حمام</span>'
        f'<span><i class="fa-solid fa-ruler-combined"></i> {p["area"]} م²</span></div>'
        f'<span class="chip">{p["finishing"]}</span><span class="chip">{floor_text(p)}</span>'
        f'<span class="chip">استلام: {p["delivery"]}</span>'
        f'<div class="prop-id" style="margin-top:10px;">رقم الوحدة #{p["id"]}</div>'
        '</div></div>'
    )


@st.dialog("تفاصيل العقار", width="large")
def show_property_modal(p):
    imgs = [p["main_image"]] + p.get("gallery", [])[:2]
    while len(imgs) < 3:
        imgs.append(imgs[0])
    down = p["price_val"] * 0.10
    monthly = (p["price_val"] - down) / (8 * 12)
    feats = "".join(f'<span class="chip">{f}</span>' for f in p.get("features", []))
    st.markdown(
        '<div class="gal-grid">'
        f'<div class="gal-img main" style="background-image:url({imgs[0]})"></div>'
        f'<div class="gal-img" style="background-image:url({imgs[1]})"></div>'
        f'<div class="gal-img" style="background-image:url({imgs[2]})"></div></div>'
        f'<div style="font-size:22px;font-weight:800;">{p["title"]}</div>'
        f'<div class="dlg-sub"><i class="fa-solid fa-location-dot"></i> {p["location"]} · وحدة #{p["id"]}</div>'
        f'<div class="dlg-price">{p["price"]} ج.م</div>'
        '<div class="spec-grid">'
        f'<div class="spec-box"><i class="fa-solid fa-bed"></i><div class="spec-val">{p["beds"]}</div><div class="spec-lbl">غرف نوم</div></div>'
        f'<div class="spec-box"><i class="fa-solid fa-bath"></i><div class="spec-val">{p["baths"]}</div><div class="spec-lbl">حمامات</div></div>'
        f'<div class="spec-box"><i class="fa-solid fa-ruler-combined"></i><div class="spec-val">{p["area"]} م²</div><div class="spec-lbl">المساحة</div></div>'
        f'<div class="spec-box"><i class="fa-solid fa-layer-group"></i><div class="spec-val">{floor_text(p)}</div><div class="spec-lbl">الموقع بالمبنى</div></div>'
        '</div>'
        f'<div style="margin-bottom:8px;"><span class="chip">{p["type"]}</span><span class="chip">{p["finishing"]}</span>'
        f'<span class="chip">{p["status"]}</span><span class="chip">استلام: {p["delivery"]}</span></div>'
        f'<p style="line-height:1.9;">{p["desc"]}</p>'
        f'<div>{feats}</div>'
        '<div class="fin-box">'
        f'<div><div class="k">مقدم تقديري (10%)</div><div class="v">{down:,.0f} ج.م</div></div>'
        f'<div><div class="k">قسط شهري تقديري (8 سنوات)</div><div class="v">{monthly:,.0f} ج.م</div></div>'
        '<div><div class="k">ملاحظة</div><div style="font-size:13px;">تقدير تقريبي بدون فوائد. استخدم الحاسبة للتفاصيل</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("استفسر عبر المستشار", key=f"m_bot_{p['id']}", icon=":material/support_agent:",
                     type="primary", width="stretch"):
            go_advisor(p)
    with b2:
        if st.button("حاسبة التمويل", key=f"m_calc_{p['id']}", icon=":material/calculate:",
                     width="stretch"):
            go_calculator(p)
    with b3:
        is_fav = p["id"] in st.session_state.favorites
        st.button("إزالة من المفضلة" if is_fav else "إضافة للمفضلة", key=f"m_fav_{p['id']}",
                  icon=":material/favorite:" if is_fav else ":material/favorite_border:",
                  on_click=toggle_fav, args=(p["id"],), width="stretch")


# ═══════════════════════════════════════════════════════════════
# 5) العنوان وشريط الإحصائيات
# ═══════════════════════════════════════════════════════════════
st.markdown("<h2 style='font-weight:800; font-size:32px; margin-bottom:5px;'>معرض العقارات المتاحة</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:var(--color-text-muted); font-size:17px; margin-bottom:22px;'>تصفح أحدث الوحدات السكنية والاستثمارية، وقارن بين الأسعار، واحفظ ما يعجبك في المفضلة.</p>", unsafe_allow_html=True)

avg_price = sum(p["price_val"] for p in all_props) / len(all_props)
stats = [
    ("fa-building", f"{len(all_props)}", "وحدة متاحة"),
    ("fa-location-dot", f"{len({p['city'] for p in all_props})}", "منطقة"),
    ("fa-tags", f"{avg_price / 1e6:.1f} مليون", "متوسط السعر"),
    ("fa-heart", f"{len(st.session_state.favorites)}", "في مفضلتك"),
]
for col, (icon, num, label) in zip(st.columns(4), stats):
    col.markdown(
        f'<div class="stat-box"><div class="stat-icon"><i class="fa-solid {icon}"></i></div>'
        f'<div><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div></div>',
        unsafe_allow_html=True,
    )
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 6) الفلاتر والترتيب
# ═══════════════════════════════════════════════════════════════
TYPE_OPTS = ["الكل"] + sorted({p["type"] for p in all_props})
CITY_OPTS = ["الكل"] + sorted({p["city"] for p in all_props})
BEDS_OPTS = ["الكل", "1", "2", "3", "4", "5+"]
SORT_OPTS = ["الأحدث إضافة", "السعر: من الأقل", "السعر: من الأعلى", "المساحة: الأكبر"]
MIN_M = float(math.floor(min(p["price_val"] for p in all_props) / 1e6))
MAX_M = float(math.ceil(max(p["price_val"] for p in all_props) / 1e6))

if st.session_state.get("price_bounds") != (MIN_M, MAX_M):
    st.session_state.price_bounds = (MIN_M, MAX_M)
    st.session_state.f_price = (MIN_M, MAX_M)


def reset_filters():
    st.session_state.f_search = ""
    st.session_state.f_type = "الكل"
    st.session_state.f_city = "الكل"
    st.session_state.f_price = (MIN_M, MAX_M)
    st.session_state.f_beds = "الكل"
    st.session_state.f_sort = SORT_OPTS[0]
    st.session_state.f_fav = False


r1 = st.columns([2.2, 1, 1.2])
f_search = r1[0].text_input("بحث", key="f_search", placeholder="المدينة، الكمبوند، أو رقم الوحدة مثل 15")
f_type = r1[1].selectbox("نوع العقار", TYPE_OPTS, key="f_type")
f_city = r1[2].selectbox("المنطقة", CITY_OPTS, key="f_city")

r2 = st.columns([2, 1, 1.2, 1, 1])
f_price = r2[0].slider("نطاق السعر (مليون ج.م)", MIN_M, MAX_M, (MIN_M, MAX_M), step=0.5, key="f_price")
f_beds = r2[1].selectbox("غرف النوم", BEDS_OPTS, key="f_beds")
f_sort = r2[2].selectbox("الترتيب", SORT_OPTS, key="f_sort")
f_fav = r2[3].toggle("المفضلة فقط", key="f_fav")
r2[4].markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
r2[4].button("إعادة ضبط", icon=":material/restart_alt:", on_click=reset_filters, width="stretch")

# ─── تطبيق الفلاتر ───
q = f_search.strip().lower().lstrip("#")
results = []
for p in all_props:
    if f_type != "الكل" and p["type"] != f_type:
        continue
    if f_city != "الكل" and p["city"] != f_city:
        continue
    if not (f_price[0] * 1e6 <= p["price_val"] <= f_price[1] * 1e6):
        continue
    if f_beds == "5+" and p["beds"] < 5:
        continue
    if f_beds not in ("الكل", "5+") and p["beds"] != int(f_beds):
        continue
    if f_fav and p["id"] not in st.session_state.favorites:
        continue
    if q and q not in f"{p['title']} {p['location']} {p['type']}".lower() and q != str(p["id"]):
        continue
    results.append(p)

if f_sort == "السعر: من الأقل":
    results.sort(key=lambda p: p["price_val"])
elif f_sort == "السعر: من الأعلى":
    results.sort(key=lambda p: p["price_val"], reverse=True)
elif f_sort == "المساحة: الأكبر":
    results.sort(key=lambda p: p["area"], reverse=True)
else:
    results.sort(key=lambda p: p["id"], reverse=True)

# ─── الرجوع للصفحة 1 عند تغيير أي فلتر ───
sig = (f_search, f_type, f_city, f_price, f_beds, f_sort, f_fav)
if st.session_state.get("filter_sig") != sig:
    st.session_state.filter_sig = sig
    st.session_state.prop_page = 1

total_pages = max(1, math.ceil(len(results) / PAGE_SIZE))
st.session_state.prop_page = min(max(1, st.session_state.prop_page), total_pages)
page_no = st.session_state.prop_page
start = (page_no - 1) * PAGE_SIZE
visible = results[start:start + PAGE_SIZE]

st.markdown(
    f"<div style='margin:14px 0 20px; font-weight:700; color:var(--color-text-muted);'>"
    f"عرض {len(visible)} من أصل {len(results)} عقار مطابق</div>",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════
# 7) عرض الكروت
# ═══════════════════════════════════════════════════════════════
if not results:
    st.markdown(
        '<div class="stat-box" style="justify-content:center; padding:40px; flex-direction:column; text-align:center;">'
        '<div class="stat-icon"><i class="fa-solid fa-magnifying-glass"></i></div>'
        '<div class="stat-num" style="font-size:20px;">لا توجد عقارات مطابقة</div>'
        '<div class="stat-label">جرّب توسيع نطاق السعر أو تغيير الفلاتر.</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

for i in range(0, len(visible), 2):
    row = st.columns(2)
    for col, prop in zip(row, visible[i:i + 2]):
        with col:
            st.markdown(card_html(prop), unsafe_allow_html=True)
            b1, b2, b3 = st.columns([1.2, 1.2, 1])
            with b1:
                if st.button("التفاصيل", key=f"det_{prop['id']}", icon=":material/visibility:",
                             width="stretch"):
                    show_property_modal(prop)
            with b2:
                if st.button("المستشار", key=f"bot_{prop['id']}", icon=":material/support_agent:",
                             type="primary", width="stretch"):
                    go_advisor(prop)
            with b3:
                is_fav = prop["id"] in st.session_state.favorites
                st.button("محفوظ" if is_fav else "حفظ", key=f"fav_{prop['id']}",
                          icon=":material/favorite:" if is_fav else ":material/favorite_border:",
                          on_click=toggle_fav, args=(prop["id"],), width="stretch")
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 8) ترقيم الصفحات (في RTL: السابق يمين، التالي يسار)
# ═══════════════════════════════════════════════════════════════
def go_prev():
    st.session_state.prop_page -= 1


def go_next():
    st.session_state.prop_page += 1


if total_pages > 1:
    st.markdown("<hr style='border-color: var(--color-border);'>", unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns([1, 2, 1])
    with pc1:
        if page_no > 1:
            st.button("السابق", icon=":material/chevron_right:", on_click=go_prev, width="stretch")
    with pc2:
        st.markdown(
            f"<div style='text-align:center; font-weight:700; padding-top:8px;'>صفحة {page_no} من {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with pc3:
        if page_no < total_pages:
            st.button("التالي", icon=":material/chevron_left:", on_click=go_next, width="stretch")