import calendar
from datetime import date

import pandas as pd
import streamlit as st

import db

st.set_page_config(
    page_title="حاسبة التمويل | Aqarify",
    page_icon=":material/calculate:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_FILE = db.DB_FILE

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
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Calculator"] { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Calculator"]::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent);
    }

    /* ─── عناصر الصفحة ─── */
    .st-key-inputs_panel {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 20px; padding: 22px; margin-bottom: 16px;
    }
    .box { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 20px; padding: 22px; margin-bottom: 16px; }
    .box-title { font-size: 17px; font-weight: 800; margin-bottom: 14px; }
    .box-title i { color: var(--color-accent); margin-left: 8px; }
    .chip {
        display: inline-block; border: 1px solid var(--color-border); border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600; margin-left: 6px; margin-top: 4px; background: var(--color-white);
    }

    .sel-img { height: 190px; border-radius: 14px; background-size: cover; background-position: center; background-color: var(--color-border); margin-bottom: 14px; }
    .sel-title { font-size: 18px; font-weight: 800; }
    .sel-loc { font-size: 14px; color: var(--color-text-muted); margin: 4px 0 8px; }
    .sel-price { font-size: 22px; font-weight: 800; color: var(--color-accent); }
    .sel-specs { display: flex; justify-content: space-between; background: #F9FAFB; border: 1px solid var(--color-border); border-radius: 12px; padding: 10px 14px; font-size: 14px; font-weight: 700; margin: 12px 0 8px; }

    .plan-banner {
        background: var(--color-dark); color: var(--color-white); border-radius: 20px;
        padding: 24px 28px; margin-bottom: 16px; display: flex; justify-content: space-between;
        align-items: center; gap: 20px; flex-wrap: wrap;
    }
    .plan-label { font-size: 13px; opacity: .75; }
    .plan-big { font-size: 36px; font-weight: 800; color: var(--color-accent); line-height: 1.2; }
    .plan-sum { font-size: 14px; line-height: 1.9; max-width: 460px; opacity: .92; }

    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
    .kpi { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 16px; padding: 16px; transition: all .25s ease; }
    .kpi:hover { transform: translateY(-3px); border-color: var(--color-accent); box-shadow: 0 10px 22px rgba(0,0,0,.06); }
    .kpi i { color: var(--color-accent); font-size: 18px; }
    .kpi-val { font-size: 19px; font-weight: 800; margin-top: 8px; line-height: 1.2; }
    .kpi-lbl { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }

    .track { display: flex; align-items: center; gap: 28px; flex-wrap: wrap; }
    .donut { width: 168px; height: 168px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .donut-in { width: 126px; height: 126px; border-radius: 50%; background: var(--color-white); display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .donut-pct { font-size: 30px; font-weight: 800; line-height: 1; }
    .donut-lbl { font-size: 13px; color: var(--color-text-muted); }
    .stat-list { flex: 1; min-width: 240px; }
    .stat-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed var(--color-border); font-size: 14px; }
    .stat-row:last-child { border-bottom: none; }
    .stat-row b { font-weight: 800; }
    .stat-row .gold { color: var(--color-accent); }
    .pbar { height: 12px; background: var(--color-border); border-radius: 10px; overflow: hidden; margin: 18px 0 8px; }
    .pbar-fill { height: 100%; background: var(--color-accent); border-radius: 10px; }
    .pbar-lbl { display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; }

    .meter { height: 10px; background: var(--color-border); border-radius: 10px; overflow: hidden; margin: 10px 0; }
    .meter-fill { height: 100%; background: var(--color-dark); border-radius: 10px; }
    .note-line { font-size: 14px; line-height: 1.9; }

    .scen { width: 100%; border-collapse: collapse; font-size: 14px; }
    .scen th { text-align: right; color: var(--color-text-muted); font-weight: 600; padding: 10px 8px; border-bottom: 1px solid var(--color-border); }
    .scen td { padding: 12px 8px; border-bottom: 1px solid var(--color-border); font-weight: 700; }
    .scen tr.cur td { background: #F6EBCB; }
    .scen tr:last-child td { border-bottom: none; }

    .st-key-inputs_panel [data-testid="stNumberInput"] input { font-weight: 700; }

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


PROPS = load_props(DB_FILE.stat().st_mtime) if DB_FILE.exists() else st.session_state.get("properties_list", [])
BY_ID = {p["id"]: p for p in PROPS}
ss = st.session_state

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
        if ss.get("is_admin_logged_in", False):
            st.page_link("pages/Admin.py", label="لوحة الإدارة")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 4) منطق الحساب
# ═══════════════════════════════════════════════════════════════
# ===== LOGIC START =====
FREQS = {"شهري": 12, "ربع سنوي": 4, "نصف سنوي": 2, "سنوي": 1}
UNIT_NAME = {12: "شهرياً", 4: "كل 3 شهور", 2: "كل 6 شهور", 1: "سنوياً"}


def money(v):
    return f"{int(round(v)):,}"


def add_months(d, m):
    y = d.year + (d.month - 1 + m) // 12
    mo = (d.month - 1 + m) % 12 + 1
    return date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def pmt_value(financed, years, freq, annual_rate):
    n = years * freq
    r = annual_rate / 100 / freq
    if r == 0:
        return financed / n
    return financed * r / (1 - (1 + r) ** -n)


def build_plan(price, down_pct, years, freq, annual_rate, start):
    down = price * down_pct / 100
    financed = price - down
    n = years * freq
    r = annual_rate / 100 / freq
    pmt = pmt_value(financed, years, freq, annual_rate)
    rows, bal = [], financed
    for k in range(1, n + 1):
        interest = bal * r
        principal = pmt - interest
        bal = max(0.0, bal - principal)
        rows.append({"k": k, "due": add_months(start, k * (12 // freq)), "pmt": pmt,
                     "principal": principal, "interest": interest, "balance": bal})
    return {"down": down, "financed": financed, "n": n, "pmt": pmt, "rows": rows,
            "total_inst": pmt * n, "total_interest": pmt * n - financed}
# ===== LOGIC END =====

# ═══════════════════════════════════════════════════════════════
# 5) القادم من المعرض / المستشار
# ═══════════════════════════════════════════════════════════════
incoming = ss.pop("selected_property_for_calc", None)
if incoming:
    pid = incoming.get("id")
    if pid not in BY_ID:
        pid = next((p["id"] for p in PROPS
                    if p["title"] == incoming.get("title") and p["price"] == incoming.get("price")), None)
    if pid in BY_ID:
        ss.calc_prop = pid
        ss.calc_price = BY_ID[pid]["price_val"]
ss.setdefault("calc_prop", 0)
ss.setdefault("calc_price", 5_000_000)


def on_prop_change():
    if ss.calc_prop in BY_ID:
        ss.calc_price = BY_ID[ss.calc_prop]["price_val"]


def reset_plan():
    ss.calc_down, ss.calc_years, ss.calc_freq = 10, 8, "شهري"
    ss.calc_rate, ss.calc_maint, ss.calc_cash = 0.0, 0.0, 10


def go_advisor(p):
    ss["chat_property_context"] = p["title"]
    ss.active_prop_data = p
    st.switch_page("pages/Customer Service.py")


# ═══════════════════════════════════════════════════════════════
# 6) الواجهة
# ═══════════════════════════════════════════════════════════════
st.markdown("<h2 style='font-weight:800; font-size:32px; margin-bottom:5px;'>حاسبة التمويل العقاري</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:var(--color-text-muted); font-size:17px; margin-bottom:22px;'>اختر الوحدة، اضبط خطة السداد، وتابع كم سددت وكم تبقّى عليك بالتفصيل.</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1.8])

# ─────────────── العمود الأيمن: الوحدة والمدخلات ───────────────
with col_in:
    with st.container(key="inputs_panel"):
        st.markdown("<div class='box-title'><i class='fa-solid fa-sliders'></i> بيانات الخطة</div>", unsafe_allow_html=True)

        if PROPS:
            st.selectbox(
                "الوحدة", [0] + [p["id"] for p in PROPS], key="calc_prop", on_change=on_prop_change,
                format_func=lambda i: "إدخال سعر يدوي" if i == 0 else f"#{i} · {BY_ID[i]['title']} · {BY_ID[i]['price']} ج.م",
            )
        price = st.number_input("سعر الوحدة (ج.م)", min_value=100_000, max_value=200_000_000, step=50_000, key="calc_price")
        down_pct = st.slider("نسبة المقدم %", 5, 60, 10, key="calc_down")
        years = st.slider("مدة التقسيط (سنوات)", 1, 12, 8, key="calc_years")
        freq_label = st.selectbox("دورية السداد", list(FREQS), key="calc_freq")
        rate = st.slider("الفائدة أو زيادة التقسيط السنوية %", 0.0, 25.0, 0.0, 0.5, key="calc_rate",
                         help="اتركها 0 لو التقسيط بدون فوائد.")
        maint = st.slider("رسوم الصيانة والتسجيل %", 0.0, 15.0, 0.0, 0.5, key="calc_maint",
                          help="تُدفع غالباً عند الاستلام وتُحسب خارج التقسيط.")
        cash_disc = st.slider("خصم الدفع الكاش %", 0, 30, 10, key="calc_cash")
        start = st.date_input("تاريخ بداية التقسيط", value=date.today(), key="calc_start")
        income = st.number_input("دخلك الشهري (اختياري)", min_value=0, max_value=5_000_000, value=0, step=1000, key="calc_income")
        st.button("إعادة ضبط الخطة", icon=":material/restart_alt:", on_click=reset_plan, width="stretch")

    prop = BY_ID.get(ss.calc_prop)
    if prop:
        st.markdown(
            '<div class="box">'
            '<div class="box-title"><i class="fa-solid fa-house-circle-check"></i> الوحدة المختارة</div>'
            f'<div class="sel-img" style="background-image:url({prop["main_image"]})"></div>'
            f'<div class="sel-title">{prop["title"]}</div>'
            f'<div class="sel-loc"><i class="fa-solid fa-location-dot"></i> {prop["location"]} · وحدة #{prop["id"]}</div>'
            f'<div class="sel-price">{prop["price"]} ج.م</div>'
            '<div class="sel-specs">'
            f'<span><i class="fa-solid fa-bed"></i> {prop["beds"]} غرف</span>'
            f'<span><i class="fa-solid fa-bath"></i> {prop["baths"]} حمام</span>'
            f'<span><i class="fa-solid fa-ruler-combined"></i> {prop["area"]} م²</span></div>'
            f'<div><span class="chip">{prop["type"]}</span><span class="chip">{prop["finishing"]}</span>'
            f'<span class="chip">{prop["status"]}</span><span class="chip">استلام: {prop["delivery"]}</span></div>'
            f'<div style="font-size:13px;color:var(--color-text-muted);margin-top:10px;">سعر المتر: {money(prop["price_val"] / prop["area"])} ج.م</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if price != prop["price_val"]:
            st.caption("السعر المدخل يختلف عن سعر الوحدة في المعرض، والحساب يعتمد على السعر المدخل.")
        if st.button("اسأل المستشار عن هذه الوحدة", icon=":material/support_agent:", type="primary", width="stretch"):
            go_advisor(prop)
        if st.button("العودة إلى المعرض", icon=":material/apartment:", width="stretch"):
            st.switch_page("pages/Properties.py")
    else:
        st.markdown(
            '<div class="box"><div class="box-title"><i class="fa-solid fa-circle-info"></i> وضع الإدخال اليدوي</div>'
            '<div class="note-line">اختر وحدة من القائمة بالأعلى لعرض صورتها وتفاصيلها، أو افتح الحاسبة من زر '
            '«حاسبة التمويل» في معرض العقارات.</div></div>',
            unsafe_allow_html=True,
        )

# ─────────────── العمود الأيسر: النتائج ───────────────
freq = FREQS[freq_label]
plan = build_plan(price, down_pct, years, freq, rate, start)
rows, n, pmt, down, financed = plan["rows"], plan["n"], plan["pmt"], plan["down"], plan["financed"]
maint_fee = price * maint / 100
total_payable = down + plan["total_inst"]
total_cost = total_payable + maint_fee

with col_out:
    # ── بانر الخطة ──
    st.markdown(
        '<div class="plan-banner"><div>'
        f'<div class="plan-label">القسط {freq_label}</div>'
        f'<div class="plan-big">{money(pmt)} ج.م</div></div>'
        f'<div class="plan-sum">مقدم <b>{money(down)} ج.م</b> ({down_pct}%)، ثم <b>{n}</b> قسط {UNIT_NAME[freq]} '
        f'على مدى <b>{years}</b> سنوات، لتبلغ إجمالي المدفوعات <b>{money(total_cost)} ج.م</b>.</div></div>',
        unsafe_allow_html=True,
    )

    # ── مؤشرات ──
    kpis = [
        ("fa-hand-holding-dollar", money(down), "المقدم (ج.م)"),
        ("fa-scale-balanced", money(financed), "المبلغ المقسّط (ج.م)"),
        ("fa-percent", money(plan["total_interest"]), "إجمالي الفوائد (ج.م)"),
        ("fa-flag-checkered", rows[-1]["due"].strftime("%Y-%m-%d"), "تاريخ آخر قسط"),
    ]
    st.markdown(
        '<div class="kpi-grid">' + "".join(
            f'<div class="kpi"><i class="fa-solid {ic}"></i><div class="kpi-val">{v}</div><div class="kpi-lbl">{lb}</div></div>'
            for ic, v, lb in kpis) + '</div>',
        unsafe_allow_html=True,
    )

    # ── تتبع السداد ──
    st.markdown("<div class='box-title' style='margin-top:6px;'><i class='fa-solid fa-chart-pie'></i> تتبع السداد</div>", unsafe_allow_html=True)
    auto_n = sum(1 for r in rows if r["due"] <= date.today())
    c_auto, c_manual = st.columns([1, 1.6])
    with c_auto:
        auto = st.toggle("احسب المسدد تلقائياً من التاريخ", value=False, key="calc_auto")
    if auto:
        paid_k = auto_n
        with c_manual:
            st.caption(f"عدد الأقساط المستحقة حتى اليوم: {auto_n}")
    else:
        with c_manual:
            paid_k = st.slider("عدد الأقساط المسددة حتى الآن", 0, n, value=n // 3)

    paid_total = down + pmt * paid_k
    remaining = total_payable - paid_total
    pct = paid_total / total_payable * 100
    rem_principal = rows[paid_k - 1]["balance"] if paid_k > 0 else financed
    nxt = rows[paid_k] if paid_k < n else None
    next_txt = f"{nxt['due'].strftime('%Y-%m-%d')} · {money(nxt['pmt'])} ج.م" if nxt else "تم سداد كامل الأقساط"

    st.markdown(
        '<div class="box"><div class="track">'
        f'<div class="donut" style="background: conic-gradient(var(--color-accent) {pct:.1f}%, var(--color-border) 0);">'
        f'<div class="donut-in"><div class="donut-pct">{pct:.0f}%</div><div class="donut-lbl">مسدد</div></div></div>'
        '<div class="stat-list">'
        f'<div class="stat-row"><span>ما سددته (المقدم + {paid_k} قسط)</span><b class="gold">{money(paid_total)} ج.م</b></div>'
        f'<div class="stat-row"><span>المتبقي عليك ({n - paid_k} قسط)</span><b>{money(remaining)} ج.م</b></div>'
        f'<div class="stat-row"><span>أصل الدين المتبقي</span><b>{money(rem_principal)} ج.م</b></div>'
        f'<div class="stat-row"><span>القسط القادم</span><b>{next_txt}</b></div>'
        '</div></div>'
        f'<div class="pbar"><div class="pbar-fill" style="width:{pct:.1f}%"></div></div>'
        f'<div class="pbar-lbl"><span>مسدد {money(paid_total)}</span><span>متبقٍ {money(remaining)}</span></div></div>',
        unsafe_allow_html=True,
    )

    # ── القدرة الشرائية + الكاش ──
    c1, c2 = st.columns(2)
    with c1:
        monthly_eq = pmt * freq / 12
        if income > 0:
            ratio = monthly_eq / income * 100
            if ratio <= 30:
                verdict = "نسبة مريحة وآمنة."
            elif ratio <= 40:
                verdict = "نسبة مقبولة لكنها قريبة من الحد الأعلى."
            else:
                verdict = "نسبة مرتفعة، يُفضّل زيادة المقدم أو مدة التقسيط."
            body = (f'<div class="note-line">القسط الشهري المكافئ <b>{money(monthly_eq)} ج.م</b> يمثّل '
                    f'<b>{ratio:.0f}%</b> من دخلك.</div><div class="meter"><div class="meter-fill" style="width:{min(ratio, 100):.0f}%"></div></div>'
                    f'<div class="note-line">{verdict}</div>')
        else:
            body = ('<div class="note-line">أدخل دخلك الشهري في قسم بيانات الخطة لمعرفة نسبة القسط من دخلك '
                    f'(القسط الشهري المكافئ: <b>{money(monthly_eq)} ج.م</b>).</div>')
        st.markdown(f"<div class='box'><div class='box-title'><i class='fa-solid fa-wallet'></i> القدرة على السداد</div>{body}</div>", unsafe_allow_html=True)
    with c2:
        cash_price = price * (1 - cash_disc / 100)
        saving = total_cost - cash_price
        st.markdown(
            "<div class='box'><div class='box-title'><i class='fa-solid fa-money-bill-wave'></i> لو دفعت كاش</div>"
            f"<div class='note-line'>سعر الكاش بعد خصم {cash_disc}%: <b>{money(cash_price)} ج.م</b>.<br>"
            f"توفّر مقارنة بالتقسيط: <b style='color:var(--color-accent)'>{money(max(saving, 0))} ج.م</b>.</div></div>",
            unsafe_allow_html=True,
        )

    # ── الرسوم البيانية ──
    st.markdown("<div class='box-title'><i class='fa-solid fa-chart-line'></i> تطور الرصيد المتبقي</div>", unsafe_allow_html=True)
    df_bal = pd.DataFrame({"الرصيد المتبقي": [financed] + [r["balance"] for r in rows]})
    st.area_chart(df_bal, color="#C9A24B", height=240)

    st.markdown("<div class='box-title' style='margin-top:10px;'><i class='fa-solid fa-chart-column'></i> المدفوع سنوياً</div>", unsafe_allow_html=True)
    yearly = {}
    for r in rows:
        y = (r["k"] - 1) // freq + 1
        a = yearly.setdefault(y, [0.0, 0.0])
        a[0] += r["principal"]
        a[1] += r["interest"]
    df_year = pd.DataFrame({"أصل القسط": [v[0] for v in yearly.values()], "الفائدة": [v[1] for v in yearly.values()]},
                           index=list(yearly.keys()))
    st.bar_chart(df_year, color=["#14161C", "#C9A24B"], height=240)

    # ── مقارنة المدد ──
    st.markdown("<div class='box-title' style='margin-top:10px;'><i class='fa-solid fa-code-compare'></i> قارن بين مدد التقسيط</div>", unsafe_allow_html=True)
    trs = ""
    for y in sorted({3, 5, 8, 10, 12, years}):
        pm = pmt_value(financed, y, freq, rate)
        cur = " class='cur'" if y == years else ""
        label = f"{y} سنوات" + (" (خطتك)" if y == years else "")
        trs += f"<tr{cur}><td>{label}</td><td>{money(pm)} ج.م</td><td>{money(pm * y * freq - financed)} ج.م</td><td>{money(down + pm * y * freq)} ج.م</td></tr>"
    st.markdown(
        "<div class='box'><table class='scen'><tr><th>المدة</th><th>القسط</th><th>إجمالي الفوائد</th><th>إجمالي المدفوع</th></tr>"
        f"{trs}</table></div>",
        unsafe_allow_html=True,
    )

    # ── جدول الأقساط ──
    st.markdown("<div class='box-title'><i class='fa-solid fa-table-list'></i> جدول الأقساط التفصيلي</div>", unsafe_allow_html=True)
    df = pd.DataFrame([{
        "#": r["k"], "تاريخ الاستحقاق": r["due"].strftime("%Y-%m-%d"), "القسط": money(r["pmt"]),
        "من الأصل": money(r["principal"]), "الفائدة": money(r["interest"]), "الرصيد المتبقي": money(r["balance"]),
        "الحالة": "مسدد" if r["k"] <= paid_k else "قادم",
    } for r in rows])
    try:
        shown = df.style.apply(lambda row: ["background-color:#F6EBCB" if row["الحالة"] == "مسدد" else "" for _ in row], axis=1)
        st.dataframe(shown, width="stretch", hide_index=True, height=360)
    except Exception:
        st.dataframe(df, width="stretch", hide_index=True, height=360)
    st.download_button("تحميل الجدول (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="aqarify_installments.csv", mime="text/csv", icon=":material/download:")
    st.caption("الحسابات تقديرية لأغراض العرض، والعقد الرسمي هو المرجع النهائي لقيم الأقساط والرسوم.")