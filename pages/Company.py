import pandas as pd
import streamlit as st

import db
import session
import unit_tools as ut
from utils import esc, safe

st.set_page_config(
    page_title="لوحة الشركة | Aqarify",
    page_icon=":material/business:",
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
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Company"] { color: var(--color-accent) !important; }
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Company"]::after {
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
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: none; }
    .stTabs [data-baseweb="tab"] { height: 46px; background: var(--color-white); border: 1px solid var(--color-border); border-radius: 12px; padding: 0 22px; }
    .stTabs [data-baseweb="tab"] p { font-weight: 800; }
    .stTabs [aria-selected="true"] { background: var(--color-dark) !important; border-color: var(--color-dark); }
    .stTabs [aria-selected="true"] p { color: var(--color-accent) !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

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
        st.page_link("pages/Company.py", label="لوحة الشركة")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3) الحماية: حساب شركة فقط
# ═══════════════════════════════════════════════════════════════
current_user = session.require_role("company")

if not db.DB_FILE.exists():
    st.error("قاعدة البيانات غير موجودة. شغّل: python migrate.py")
    st.stop()

company = db.get_company(current_user["company_id"])
if not company:
    st.error("حساب الشركة غير مرتبط بشركة موجودة. تواصل مع الإدارة.")
    st.stop()

CID = company["id"]
db.init_tickets_table()

# ═══════════════════════════════════════════════════════════════
# 4) البيانات (وحدات وتذاكر الشركة دي بس)
# ═══════════════════════════════════════════════════════════════
props = db.list_properties_legacy(CID)
tickets = [{**t, "pk": t["id"], "id": t["code"]} for t in db.list_tickets(company_id=CID)]
BY_ID = {p["id"]: p for p in props}
ALL_PROPS = db.list_properties_legacy()
TYPES = sorted({p["type"] for p in ALL_PROPS} | set(ut.BASE_TYPES))
CITIES = sorted({p["city"] for p in ALL_PROPS} or {"التجمع الخامس"})
FEATURE_OPTS = sorted({f for p in ALL_PROPS for f in p.get("features", [])})
TK_STATUSES = list(db.TICKET_STATUSES)


def flash(kind, msg):
    ss.co_flash = (kind, msg)


def show_flash():
    f = ss.pop("co_flash", None)
    if f:
        {"success": st.success, "error": st.error, "info": st.info}[f[0]](f[1])


def money(v):
    return f"{int(round(v)):,}"


# ═══════════════════════════════════════════════════════════════
# 5) رأس الصفحة
# ═══════════════════════════════════════════════════════════════
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown("<h2 style='font-weight:800; font-size:32px; margin-bottom:2px;'>لوحة الشركة</h2>"
                f"<p style='color:var(--color-text-muted); font-size:16px;'>مرحباً {esc(current_user['name'])}، "
                f"شركة <b>{esc(company['name'])}</b>: أضف وحداتك وتابع طلبات العملاء في مكان واحد.</p>",
                unsafe_allow_html=True)
with h2:
    st.button("تسجيل الخروج", icon=":material/logout:", on_click=session.logout_user, width="stretch")
show_flash()

tab_dash, tab_units, tab_tickets, tab_profile = st.tabs(["المؤشرات", "وحداتي", "طلبات العملاء", "بيانات الشركة"])

# ═══════════════════════════════════════════════════════════════
# 6) المؤشرات
# ═══════════════════════════════════════════════════════════════
with tab_dash:
    total_val = sum(p["price_val"] for p in props)
    avg = total_val / len(props) if props else 0
    ready = sum(1 for p in props if p["status"] == "جاهز للتسليم")
    new_tk = sum(1 for t in tickets if t["status"] == "جديدة")
    kpis = [
        ("fa-building", f"{len(props)}", "وحداتي"),
        ("fa-sack-dollar", f"{total_val / 1e6:.1f} مليون", "قيمة وحداتي (ج.م)"),
        ("fa-tags", f"{avg / 1e6:.1f} مليون", "متوسط سعر الوحدة"),
        ("fa-key", f"{ready}", "جاهزة للتسليم"),
        ("fa-ticket", f"{len(tickets)}", "إجمالي الطلبات"),
        ("fa-bell", f"{new_tk}", "طلبات جديدة"),
    ]
    st.markdown('<div class="kpi-grid">' + "".join(
        f'<div class="kpi"><div class="kpi-icon"><i class="fa-solid {ic}"></i></div><div class="kpi-val">{v}</div><div class="kpi-lbl">{lb}</div></div>'
        for ic, v, lb in kpis) + '</div>', unsafe_allow_html=True)

    if props:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='box-title'><i class='fa-solid fa-house'></i> وحداتي حسب النوع</div>", unsafe_allow_html=True)
            st.bar_chart(pd.Series([p["type"] for p in props]).value_counts().rename("الوحدات"), color="#14161C", height=240)
        with c2:
            st.markdown("<div class='box-title'><i class='fa-solid fa-location-dot'></i> وحداتي حسب المنطقة</div>", unsafe_allow_html=True)
            st.bar_chart(pd.Series([p["city"] for p in props]).value_counts().rename("الوحدات"), color="#C9A24B", height=240)
    else:
        st.info("لم تضف وحدات بعد. ابدأ من تبويب «وحداتي».")

    rows = ""
    for t in map(safe, tickets[-5:][::-1]):
        cls = "new" if t["status"] == "جديدة" else ("prog" if t["status"] == "قيد المتابعة" else "")
        rows += (f'<div class="tk-row"><div><b>{t["name"]}</b> · {t["phone"]}<small>{t["topic"]} · {t.get("created_at", "")}</small></div>'
                 f'<span class="badge {cls}">{t["status"]}</span></div>')
    st.markdown("<div class='box'><div class='box-title'><i class='fa-solid fa-clock-rotate-left'></i> آخر الطلبات</div>"
                + (rows or "<div style='color:var(--color-text-muted)'>لا توجد طلبات بعد.</div>") + "</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 7) وحداتي (إضافة / تعديل / حذف، على وحدات الشركة بس)
# ═══════════════════════════════════════════════════════════════
with tab_units:
    sub_list, sub_add, sub_edit = st.tabs(["عرض الوحدات", "إضافة وحدة", "تعديل أو حذف"])

    with sub_list:
        if not props:
            st.info("لم تضف وحدات بعد. ابدأ من تبويب «إضافة وحدة».")
        else:
            df = pd.DataFrame([{
                "#": p["id"], "العنوان": p["title"], "النوع": p["type"], "الموقع": p["location"],
                "السعر": money(p["price_val"]), "المساحة": p["area"], "الغرف": p["beds"],
                "الحالة": p["status"], "الاستلام": p["delivery"],
            } for p in props])
            st.caption(f"{len(props)} وحدة")
            st.dataframe(df, width="stretch", hide_index=True, height=380)

    with sub_add:
        data = ut.unit_form("co_add_form", None, TYPES, CITIES, FEATURE_OPTS)
        if data:
            err = ut.validate(data)
            if err:
                st.error(err)
            else:
                unit = ut.build_unit(data)
                unit["company_id"] = CID
                new_id = db.add_property(unit)
                flash("success", f"تمت إضافة الوحدة #{new_id} باسم شركتك، وستظهر في المعرض والمستشار فوراً.")
                st.rerun()

    with sub_edit:
        if not props:
            st.info("لا توجد وحدات لتعديلها.")
        else:
            uid = st.selectbox("اختر الوحدة", [p["id"] for p in props], key="co_edit_id",
                               format_func=lambda i: f"#{i} · {BY_ID[i]['title']} · {BY_ID[i]['location']}")
            cur = BY_ID[uid]
            st.markdown(f'<div style="height:130px;width:220px;border-radius:14px;margin-bottom:12px;background-size:cover;'
                        f'background-position:center;background-color:var(--color-border);background-image:url({esc(cur["main_image"])})"></div>',
                        unsafe_allow_html=True)
            data = ut.unit_form(f"co_edit_form_{uid}", cur, TYPES, CITIES, FEATURE_OPTS)
            if data:
                err = ut.validate(data)
                if err:
                    st.error(err)
                else:
                    unit = ut.build_unit(data)
                    unit["company_id"] = CID
                    if db.update_property(uid, unit, company_id=CID):
                        flash("success", f"تم تحديث الوحدة #{uid}.")
                    else:
                        flash("error", f"الوحدة #{uid} غير موجودة أو لا تتبع شركتك.")
                    st.rerun()

            st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-trash'></i> حذف الوحدة</div>", unsafe_allow_html=True)
            sure = st.checkbox(f"أؤكد رغبتي في حذف الوحدة #{uid} نهائياً", key=f"co_del_ok_{uid}")
            if st.button("حذف الوحدة", icon=":material/delete:", disabled=not sure, key=f"co_del_btn_{uid}"):
                backup = db.backup_db()
                if db.delete_property(uid, company_id=CID):
                    flash("success", f"تم حذف الوحدة #{uid}. نسخة احتياطية: {backup.name if backup else '—'}.")
                else:
                    flash("error", f"الوحدة #{uid} غير موجودة أو لا تتبع شركتك.")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# 8) طلبات العملاء (التذاكر الخاصة بوحدات الشركة)
# ═══════════════════════════════════════════════════════════════
with tab_tickets:
    if not tickets:
        st.info("لا توجد طلبات حتى الآن. ستظهر هنا طلبات العملاء الخاصة بوحداتك.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("جديدة", sum(1 for t in tickets if t["status"] == "جديدة"))
        m2.metric("قيد المتابعة", sum(1 for t in tickets if t["status"] == "قيد المتابعة"))
        m3.metric("مكتملة", sum(1 for t in tickets if t["status"] == "مكتملة"))

        flt = st.selectbox("تصفية حسب الحالة", ["الكل"] + TK_STATUSES, key="co_tk_filter")
        shown = [t for t in tickets if flt == "الكل" or t["status"] == flt][::-1]

        def prop_label(t):
            pid = t.get("property_id")
            if not pid:
                return "—"
            title = t.get("property_title") or (BY_ID[pid]["title"] if pid in BY_ID else "")
            return f"#{pid} {title}".strip()

        dft = pd.DataFrame([{
            "رقم الطلب": t["id"], "الاسم": t["name"], "الهاتف": t["phone"], "نوع الطلب": t["topic"],
            "الوحدة": prop_label(t), "الحالة": t["status"],
            "التاريخ": t.get("created_at", ""), "ملاحظات": t.get("notes", ""),
        } for t in shown])
        st.dataframe(dft, width="stretch", hide_index=True, height=340)
        st.download_button("تنزيل الطلبات (CSV)", dft.to_csv(index=False).encode("utf-8-sig"),
                           file_name="company_tickets.csv", mime="text/csv", icon=":material/download:")

        st.markdown("<div class='box-title' style='margin-top:18px;'><i class='fa-solid fa-pen-to-square'></i> تحديث حالة طلب</div>", unsafe_allow_html=True)
        tid = st.selectbox("اختر الطلب", [t["id"] for t in tickets][::-1], key="co_tk_sel")
        cur_t = next(t for t in tickets if t["id"] == tid)
        ct = safe(cur_t)
        st.markdown(f'<div class="box"><b>{ct["name"]}</b> · {ct["phone"]}<br>'
                    f'<span style="color:var(--color-text-muted)">{ct["topic"]} · {esc(prop_label(cur_t))}</span><br>'
                    f'{ct.get("notes", "") or "بدون ملاحظات"}</div>', unsafe_allow_html=True)
        new_status = st.selectbox("الحالة الجديدة", TK_STATUSES, index=TK_STATUSES.index(cur_t["status"]), key=f"co_tk_status_{tid}")
        if st.button("حفظ الحالة", icon=":material/check:", type="primary", width="stretch", key=f"co_tk_save_{tid}"):
            if db.update_ticket_status(cur_t["pk"], new_status, company_id=CID):
                flash("success", f"تم تحديث الطلب {tid}.")
            else:
                flash("error", "تعذر تحديث الطلب.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# 9) بيانات الشركة (الاسم بيعدّله الأدمن بس)
# ═══════════════════════════════════════════════════════════════
with tab_profile:
    with st.form("co_profile_form"):
        st.text_input("اسم الشركة (للتعديل تواصل مع الإدارة)", value=company["name"], disabled=True)
        p_logo = st.text_input("رابط الشعار (اختياري)", value=company["logo_url"])
        p_desc = st.text_area("نبذة عن الشركة (اختياري)", value=company["description"])
        p_save = st.form_submit_button("حفظ بيانات الشركة", icon=":material/save:", type="primary", width="stretch")
    if p_save:
        if db.update_company(CID, company["name"], p_logo, p_desc):
            flash("success", "تم تحديث بيانات الشركة.")
        else:
            flash("error", "تعذر تحديث بيانات الشركة.")
        st.rerun()