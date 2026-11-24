import math

import streamlit as st

import compare_view
import db
import session
from utils import build_logo_registry, company_chip, company_logo_html, safe, set_branding

st.set_page_config(
    page_title="معرض العقارات | Aqarify",
    page_icon=":material/apartment:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

session.restore_login()  # يرجّع تسجيل الدخول بعد Refresh

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
    .block-container { padding-top: 7rem; max-width: 1280px; }

    /* ─── الشعار (نفس شكل الصفحة الرئيسية) ─── */
    .brand-logo-link { display: inline-flex; align-items: center; gap: 14px; }
    .brand-icon-box {
        background: var(--color-dark); color: var(--color-accent);
        width: 52px; height: 52px; border-radius: 14px;
        border: 1px solid var(--color-dark);
        box-shadow: 0 6px 16px rgba(20, 22, 28, 0.18);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; flex-shrink: 0;
    }
    .brand-logo-text { font-size: 34px; font-weight: 800; color: var(--color-dark); line-height: 1; margin: 0; }
    .brand-logo-dot { color: var(--color-accent); }
    .brand-logo-sub { font-size: 13px; font-weight: 400; color: var(--color-text-muted); margin-top: 4px; display: block; }

    /* ─── شريط التنقل (نفس شكل الصفحة الرئيسية، ويحافظ على الجلسة) ─── */
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
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Company"]::before    { content: "\\f1ad"; }

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

    /* ─── كروت العقارات (صورة كاملة + لوحة معلومات داكنة) ─── */
    [class*="st-key-pcard_"] {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 24px; overflow: hidden; padding: 0 !important; gap: 0 !important;
        margin-bottom: 18px; box-shadow: 0 6px 20px rgba(20,22,28,.05);
        transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
    }
    [class*="st-key-pcard_"]:hover {
        transform: translateY(-4px); box-shadow: 0 16px 36px rgba(20,22,28,.12);
        border-color: var(--color-accent);
    }
    [class*="st-key-pcard_"] > [data-testid="stVerticalBlock"] { gap: 0 !important; }
    [class*="st-key-pcard_"] [data-testid="stElementContainer"] { width: 100%; }
    [class*="st-key-pcard_"] [data-testid="stMarkdown"],
    [class*="st-key-pcard_"] [data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; }
    [class*="st-key-pbtn_"] { padding: 14px 14px 16px !important; border-top: 1px solid var(--color-border); }
    [class*="st-key-pbtn_"] [data-testid="stHorizontalBlock"] { gap: 8px !important; }
    [class*="st-key-pbtn_"] button { min-height: 40px; padding: 0.3rem 0.5rem; font-size: 13px; }

    .prop-img-box { position: relative; width: 100%; height: 380px; overflow: hidden; background: var(--color-border); }
    .prop-img {
        position: absolute; inset: 0; background-size: cover; background-position: center;
        transition: transform .6s ease;
    }
    [class*="st-key-pcard_"]:hover .prop-img { transform: scale(1.05); }
    .prop-img-box::after {
        content: ""; position: absolute; inset: 0; pointer-events: none;
        background: linear-gradient(180deg, rgba(20,22,28,.30) 0%, rgba(20,22,28,0) 30%, rgba(20,22,28,0) 55%, rgba(20,22,28,.35) 100%);
    }
    .prop-badge {
        position: absolute; top: 16px; right: 16px; z-index: 2;
        background: rgba(20,22,28,.78); backdrop-filter: blur(6px);
        color: var(--color-accent); padding: 5px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 800; border: 1px solid rgba(201,162,75,.35);
    }
    .prop-top-left { position: absolute; top: 16px; left: 16px; z-index: 2; display: flex; align-items: center; gap: 8px; }
    .prop-status {
        display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 800; backdrop-filter: blur(6px);
        background: rgba(255,255,255,.92); color: var(--color-dark);
    }
    .prop-status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: #9AA0A6; }
    .prop-status.st-ready { background: rgba(224,247,234,.95); color: #17653B; }
    .prop-status.st-ready::before { background: #1FA45B; }
    .prop-status.st-build { background: rgba(253,244,217,.96); color: #7A5A0E; }
    .prop-status.st-build::before { background: #D9A21B; }
    .prop-fav {
        width: 32px; height: 32px; border-radius: 50%; font-size: 14px;
        background: rgba(20,22,28,.78); backdrop-filter: blur(6px); color: var(--color-accent);
        display: flex; align-items: center; justify-content: center;
    }

    .prop-panel {
        position: absolute; z-index: 2; right: 14px; left: 14px; bottom: 14px;
        background: rgba(28,29,33,.92); backdrop-filter: blur(10px); color: var(--color-white);
        border-radius: 18px; padding: 12px 16px; line-height: 1.3; border: 1px solid rgba(255,255,255,.06);
    }
    .prop-panel-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
    .prop-card-price { font-size: 22px; font-weight: 800; color: var(--color-white); line-height: 1.2; }
    .prop-card-price small { font-size: 14px; font-weight: 700; color: var(--color-accent); margin-inline-start: 6px; }
    .prop-card-ppm { font-size: 12px; color: rgba(255,255,255,.62); margin-top: 2px; }
    .prop-idpill {
        font-size: 12px; font-weight: 700; color: rgba(255,255,255,.78); white-space: nowrap;
        border: 1px solid rgba(255,255,255,.2); border-radius: 20px; padding: 3px 10px;
    }
    .prop-card-title {
        font-size: 15px; font-weight: 700; margin-top: 6px; line-height: 1.4; color: var(--color-white);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .prop-panel-bottom {
        display: flex; align-items: center; justify-content: space-between; gap: 14px;
        margin-top: 8px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,.12);
    }
    .prop-card-location {
        font-size: 13px; color: rgba(255,255,255,.8); flex: 1; min-width: 0;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .prop-card-location i { color: var(--color-accent); margin-inline-end: 6px; }
    .prop-card-specs { display: flex; align-items: stretch; flex-shrink: 0; }
    .prop-spec { text-align: center; padding: 0 12px; border-inline-start: 1px solid rgba(255,255,255,.2); line-height: 1.3; }
    .prop-spec:first-child { border-inline-start: none; padding-inline-start: 0; }
    .prop-spec:last-child { padding-inline-end: 0; }
    .prop-spec b { display: block; font-size: 15px; font-weight: 800; line-height: 1.25; }
    .prop-spec b i { color: var(--color-accent); font-size: 11px; margin-inline-end: 6px; }
    .prop-spec span { font-size: 11px; color: rgba(255,255,255,.62); line-height: 1.2; }

    .prop-card-content { padding: 14px 18px 14px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 14px; }
    .prop-company { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .prop-company-ico {
        width: 50px; height: 50px; border-radius: 14px; flex-shrink: 0; position: relative; overflow: hidden;
        display: flex; align-items: center; justify-content: center;
        color: #E6C878; font-size: 19px; font-weight: 800; line-height: 1;
        box-shadow: inset 0 0 0 1px rgba(201,162,75,.5);
    }
    .prop-company-ico.has-logo { background: var(--color-white) !important; box-shadow: 0 0 0 1px var(--color-border); }
    .prop-company-ico img { width: 100%; height: 100%; object-fit: contain; padding: 5px; box-sizing: border-box; }
    .prop-company-ico.gen-logo { box-shadow: none; }
    .prop-company-ico.gen-logo img { padding: 0; }
    .company-chip {
        display: inline-flex; align-items: center; gap: 10px; margin-bottom: 12px; line-height: 1.3;
        background: var(--color-white); border: 1px solid var(--color-border); border-radius: 14px;
        padding-block: 5px; padding-inline: 6px 14px; font-size: 14px; font-weight: 800; color: var(--color-dark);
    }
    .company-chip .prop-company-ico { width: 34px; height: 34px; border-radius: 10px; }
    .prop-company-ico.soft { border-radius: 50%; background: linear-gradient(145deg, #FFFEFA, #F4ECD6); box-shadow: 0 0 0 1px rgba(201,162,75,.28); }
    .prop-company-ico.soft svg { width: 56%; height: 56%; }
    .company-chip .prop-company-ico.soft { border-radius: 50%; }
    .prop-company-txt { display: flex; flex-direction: column; line-height: 1.35; min-width: 0; }
    .prop-company-txt span { font-size: 11px; font-weight: 600; color: var(--color-text-muted); }
    .prop-company-txt b { font-size: 14px; font-weight: 800; color: var(--color-dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .prop-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
        display: inline-flex; align-items: center; border: 1px solid var(--color-border); border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 600; margin-left: 6px; margin-top: 4px;
        color: var(--color-dark); background: #FBFAF6;
    }
    .prop-card-content .chip { margin: 0; line-height: 1.5; }

    /* ─── نافذة التفاصيل ─── */
    .gal-grid { display: grid; grid-template-columns: 2fr 1fr; grid-template-rows: 1fr 1fr; gap: 10px; height: 380px; margin-bottom: 20px; }
    .gal-img { background-size: cover; background-position: center; border-radius: 18px; background-color: var(--color-border); }
    .gal-img.main { grid-row: 1 / span 2; }
    .dlg-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
    .dlg-title { font-size: 24px; font-weight: 800; line-height: 1.3; }
    .dlg-price { font-size: 30px; font-weight: 800; color: var(--color-accent); white-space: nowrap; }
    .dlg-sub { color: var(--color-text-muted); font-size: 14px; margin-top: 4px; }
    .dlg-h { font-size: 17px; font-weight: 800; margin: 22px 0 10px; display: flex; align-items: center; gap: 8px; }
    .dlg-h::before { content: ""; width: 4px; height: 18px; border-radius: 2px; background: var(--color-accent); }
    .spec-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 18px 0; }
    .spec-box { background: var(--color-white); border: 1px solid var(--color-border); border-radius: 16px; padding: 14px 10px; text-align: center; }
    .spec-ico { width: 40px; height: 40px; border-radius: 12px; background: #F4F1E6; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; }
    .spec-box i { color: var(--color-accent); font-size: 17px; }
    .spec-val { font-weight: 800; font-size: 16px; }
    .spec-lbl { font-size: 12px; color: var(--color-text-muted); }
    .amen-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
    .amen {
        background: var(--color-white); border: 1px solid var(--color-border); border-radius: 14px;
        padding: 14px 8px; text-align: center; font-size: 13px; font-weight: 700;
    }
    .amen i { display: block; color: var(--color-accent); font-size: 20px; margin-bottom: 6px; }
    .fin-box {
        background: var(--color-dark); color: var(--color-white); border-radius: 20px; padding: 22px 24px; margin: 20px 0;
        display: grid; grid-template-columns: 1.3fr 1fr 1.2fr; gap: 18px 24px; align-items: end;
    }
    .fin-box .k { font-size: 12px; opacity: .7; margin-bottom: 4px; font-weight: 600; }
    .fin-box .v { font-size: 19px; font-weight: 800; color: var(--color-white); }
    .fin-box .v-xl { font-size: 26px; font-weight: 800; color: var(--color-white); line-height: 1.2; }
    .fin-box .v-hl { font-size: 24px; font-weight: 800; color: var(--color-accent); line-height: 1.2; }
    .fin-box .fin-note { grid-column: 1 / -1; font-size: 13px; line-height: 1.8; opacity: .8; padding-top: 14px; border-top: 1px solid rgba(255,255,255,.12); }
    .fin-box .fin-note i { color: var(--color-accent); margin-inline-end: 6px; }
    .dlg-desc { line-height: 2; font-size: 15px; color: #3A3D45; max-width: 75ch; margin: 0; }

    /* ─── اسم الشركة المالكة ─── */
    .company-bar {
        display: flex; align-items: center; gap: 8px; padding: 10px 16px;
        background: #FBFAF6; border-bottom: 1px solid var(--color-border);
        font-size: 13px; font-weight: 700; color: var(--color-dark);
    }
    .company-pill {
        display: inline-flex; align-items: center; gap: 8px; margin-bottom: 10px; padding: 4px 12px;
        border: 1px solid var(--color-border); border-radius: 20px; background: var(--color-white);
        font-size: 13px; font-weight: 700; color: var(--color-dark);
    }
    .company-bar i, .company-pill i { color: var(--color-accent); }

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

    /* ─── عنوان الصفحة (عنوان يمين + وصف يسار) ─── */
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap; margin-bottom: 24px; }
    .page-title { font-weight: 800; font-size: 34px; line-height: 1.2; margin: 0; }
    .page-desc { max-width: 430px; color: var(--color-text-muted); font-size: 15px; line-height: 1.8; margin: 0; }
    .stat-box { box-shadow: 0 4px 14px rgba(20,22,28,.04); }

    /* ─── بطاقة الفلاتر ─── */
    .st-key-filters_card {
        background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 20px; padding: 18px 20px !important; box-shadow: 0 4px 14px rgba(20,22,28,.04);
    }
    [data-baseweb="input"], [data-baseweb="select"] > div {
        border-radius: 12px !important; background: #FBFAF6 !important; border: 1px solid var(--color-border) !important;
    }

    /* ─── شريط المقارنة العائم ─── */
    .st-key-cmp_tray {
        position: fixed !important; bottom: 18px; left: 50%; transform: translateX(-50%);
        width: min(860px, calc(100vw - 28px)); z-index: 999;
        background: var(--color-dark); border: 1px solid rgba(201,162,75,.45); border-radius: 22px;
        padding: 10px 16px !important; box-shadow: 0 18px 40px rgba(20,22,28,.35);
    }
    .st-key-cmp_tray [data-testid="stHorizontalBlock"] { align-items: center; flex-direction: row !important; flex-wrap: nowrap !important; gap: 10px !important; }
    .st-key-cmp_tray [data-testid="stColumn"] { min-width: 0 !important; }
    .st-key-cmp_tray [data-testid="stBaseButton-secondary"] { color: var(--color-white); border-color: rgba(255,255,255,.35); }
    .st-key-cmp_tray [data-testid="stBaseButton-secondary"]:hover { background: var(--color-white); color: var(--color-dark); }
    .st-key-cmp_tray [data-testid="stBaseButton-primary"]:disabled { opacity: .45; }
    .cmp-tray-info { display: flex; align-items: center; gap: 14px; color: var(--color-white); }
    .cmp-thumbs { display: flex; gap: 8px; }
    .cmp-thumb {
        width: 46px; height: 46px; border-radius: 12px; background-size: cover; background-position: center;
        border: 2px solid var(--color-accent); flex-shrink: 0;
    }
    .cmp-thumb.empty {
        border: 2px dashed rgba(255,255,255,.3); display: flex; align-items: center; justify-content: center;
        color: rgba(255,255,255,.4); font-size: 14px; background: transparent;
    }
    .cmp-tray-title { font-weight: 800; font-size: 15px; }
    .cmp-tray-sub { font-size: 12px; color: rgba(255,255,255,.65); }

    /* ─── نافذة المقارنة ─── */
    .cmp-hint { color: var(--color-text-muted); font-size: 14px; margin-bottom: 12px; }
    .cmp-hint i { color: var(--color-accent); }
    /* ─── لمسات إضافية: التنقل، الإحصائيات، الفلاتر، أزرار الكارت، التركيز ─── */
    .st-key-topnav, .st-key-topnav > [data-testid="stVerticalBlock"] { padding-top: 14px; }
    .st-key-topnav [data-testid="stPageLink-NavLink"]::before { width: 18px; text-align: center; font-size: 15px; }
    .st-key-topnav [data-testid="stPageLink-NavLink"] p { font-size: 16px !important; }

    .stat-box { padding: 18px 20px; gap: 16px; transition: border-color .2s ease, box-shadow .2s ease; }
    .stat-box:hover { border-color: rgba(201,162,75,.55); box-shadow: 0 8px 20px rgba(20,22,28,.06); }
    .stat-icon { width: 46px; height: 46px; border-radius: 14px; font-size: 18px; }
    .stat-num { font-size: 24px; }
    .stat-label { font-size: 13px; font-weight: 600; }

    .filters-head { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 16px; margin-bottom: 2px; }
    .filters-head i { color: var(--color-accent); font-size: 15px; }
    .filter-sep { height: 1px; background: var(--color-border); margin: 2px 0; }
    .st-key-filters_card [data-testid="stWidgetLabel"] p { font-size: 13px !important; font-weight: 700 !important; color: var(--color-text-muted) !important; }
    [data-testid="stSlider"] [role="slider"] { background-color: var(--color-accent) !important; box-shadow: 0 0 0 4px rgba(201,162,75,.2) !important; }
    [data-testid="stSliderThumbValue"] { color: #8A6410 !important; font-weight: 800; }
    [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
        border-color: var(--color-accent) !important; box-shadow: 0 0 0 3px rgba(201,162,75,.18) !important;
    }
    button:focus-visible { outline: 2px solid rgba(201,162,75,.7) !important; outline-offset: 2px; }

    /* أزرار الكارت: المستشار = أساسي، التفاصيل = ثانوي داكن، حفظ/قارن = ثانوي هادئ */
    [class*="st-key-pbtn_"] [data-testid="stBaseButton-primary"] { box-shadow: 0 2px 8px rgba(201,162,75,.25); }
    [class*="st-key-pbtn_"] [data-testid="stColumn"]:nth-child(n+3) [data-testid="stBaseButton-secondary"] {
        border-color: var(--color-border); background: var(--color-white); color: var(--color-dark);
    }
    [class*="st-key-pbtn_"] [data-testid="stColumn"]:nth-child(n+3) [data-testid="stBaseButton-secondary"]:hover {
        border-color: var(--color-accent); background: #FBFAF6; color: var(--color-dark);
    }

    /* أرقام وأسعار داخل نص عربي: تفضل في مكانها الصحيح */
    .prop-card-price, .prop-spec b, .dlg-price, .spec-val, .fin-box .v, .fin-box .v-xl, .fin-box .v-hl, .stat-num { unicode-bidi: isolate; }

    /* تابلت: أزرار الكارت 2×2 عشان ما تتزاحمش */
    @media (max-width: 1100px) {
        [class*="st-key-pbtn_"] [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        [class*="st-key-pbtn_"] [data-testid="stColumn"] { flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
        .prop-spec { padding: 0 9px; }
    }

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
        .prop-img-box { height: 300px; }
        .prop-card-price { font-size: 22px; }
        .page-title { font-size: 26px; }
        .gal-grid { height: 240px; }
        .dlg-title { font-size: 20px; }
        .spec-grid { grid-template-columns: repeat(auto-fit, minmax(96px, 1fr)); }
        .fin-box { grid-template-columns: 1fr; padding: 18px; }
        .fin-box .v-xl { font-size: 22px; }
        /* أزرار الكارت: 2×2 بدل 4 تحت بعض */
        [class*="st-key-pbtn_"] [data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: wrap !important; }
        [class*="st-key-pbtn_"] [data-testid="stColumn"] { flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
        /* شريط المقارنة العائم يفضل في صف واحد */
        .st-key-cmp_tray [data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: nowrap !important; gap: 6px !important; }
        .st-key-cmp_tray [data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 0 !important; }
        .st-key-cmp_tray [data-testid="stColumn"]:first-child { flex: 2.4 1 0 !important; }
        .cmp-tray-sub { display: none; }
        .cmp-thumb { width: 36px; height: 36px; }
        .cmp-tray-title { font-size: 13px; }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2) تحميل البيانات من قاعدة البيانات (SQLite)
# ═══════════════════════════════════════════════════════════════
DB_FILE = db.DB_FILE
PAGE_SIZE = 12


@st.cache_data
def load_properties(version):
    return db.list_properties_legacy()


if not DB_FILE.exists():
    st.error("قاعدة البيانات غير موجودة. شغّل: python migrate.py")
    st.stop()

all_props = load_properties(db.properties_version())
st.session_state.properties_list = all_props


@st.cache_data(ttl=60)
def load_company_logos(company_ids):
    """شعارات الشركات (logo_url من جدول الشركات). بتتحدّث كل دقيقة بعد ما الشركة تغيّرها."""
    by_id, by_name = {}, {}
    for cid in company_ids:
        try:
            c = dict(db.get_company(cid) or {})
        except Exception:
            continue
        if c.get("logo_url"):
            by_id[cid] = c["logo_url"]
            by_name[c.get("name")] = c["logo_url"]
    return by_id, by_name


COMPANY_LOGOS_BY_ID, COMPANY_LOGOS_BY_NAME = load_company_logos(
    tuple(sorted({p["company_id"] for p in all_props if p.get("company_id")})))
st.session_state.setdefault("guest_favorites", [])
_user = st.session_state.get("user")
if _user:
    if st.session_state.guest_favorites:   # دمج مفضلة الزائر في حسابه أول ما يسجّل دخول
        db.add_favorites(_user["id"], st.session_state.guest_favorites)
        st.session_state.guest_favorites = []
    st.session_state.favorites = db.list_favorites(_user["id"])
else:
    st.session_state.favorites = list(st.session_state.guest_favorites)
st.session_state.setdefault("prop_page", 1)
st.session_state.setdefault("compare", [])

# ═══════════════════════════════════════════════════════════════
# 3) الهيدر
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
    is_admin = st.session_state.get("is_admin_logged_in", False)
    with st.container(key="topnav"):
        st.page_link("App.py", label="الرئيسية")
        st.page_link("pages/Properties.py", label="معرض العقارات")
        st.page_link("pages/Customer Service.py", label="المستشار الذكي")
        st.page_link("pages/Calculator.py", label="حاسبة التمويل")
        if is_admin:
            st.page_link("pages/Admin.py", label="لوحة الإدارة")
        if (st.session_state.get("user") or {}).get("role") == "company":
            st.page_link("pages/Company.py", label="لوحة الشركة")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 4) دوال مساعدة
# ═══════════════════════════════════════════════════════════════
def toggle_fav(pid):
    user = st.session_state.get("user")
    if user:
        db.toggle_favorite(user["id"], pid)
        st.session_state.favorites = db.list_favorites(user["id"])
    else:
        g = st.session_state.guest_favorites
        if pid in g:
            g.remove(pid)
        else:
            g.append(pid)
        st.session_state.favorites = list(g)


MAX_COMPARE = 3


def toggle_compare(pid):
    cmp_ids = st.session_state.compare
    if pid in cmp_ids:
        cmp_ids.remove(pid)
    elif len(cmp_ids) >= MAX_COMPARE:
        st.toast(f"أقصى عدد للمقارنة {MAX_COMPARE} وحدات. أزل وحدة أولاً.", icon="⚠️")
    else:
        cmp_ids.append(pid)


def go_advisor(prop):
    st.session_state["chat_property_context"] = prop["title"]
    st.session_state.active_prop_data = prop
    st.switch_page("pages/Customer Service.py")


def go_calculator(prop):
    st.session_state["selected_property_for_calc"] = {"id": prop["id"], "title": prop["title"], "price": prop["price"]}
    st.switch_page("pages/Calculator.py")


def floor_text(prop):
    return "أرضي" if prop.get("floor") in (None, 0) else f"الدور {prop['floor']}"


def status_cls(s):
    s = str(s or "")
    if any(k in s for k in ("إنشاء", "انشاء", "قيد")):
        return "st-build"
    if any(k in s for k in ("جاهز", "فوري", "تسليم")):
        return "st-ready"
    return "st-other"


_FEAT_ICONS = [
    (("مسبح", "حمام سباحة", "بول"), "fa-water-ladder"),
    (("جراج", "موقف", "ركن"), "fa-car"),
    (("أمن", "امن", "حراسة", "كاميرات"), "fa-shield-halved"),
    (("جيم", "رياض", "نادي"), "fa-dumbbell"),
    (("مصعد", "أسانسير", "اسانسير"), "fa-elevator"),
    (("حديقة", "جاردن", "خضراء"), "fa-tree"),
    (("تكييف",), "fa-snowflake"),
    (("إنترنت", "انترنت", "واي"), "fa-wifi"),
    (("بلكونة", "شرفة", "تراس", "روف"), "fa-umbrella-beach"),
    (("مطبخ",), "fa-kitchen-set"),
    (("إطلالة", "اطلالة", "بحر", "نيل"), "fa-binoculars"),
    (("مدرسة", "مدارس"), "fa-school"),
    (("مول", "تجاري", "سوق"), "fa-bag-shopping"),
]


def feat_icon(text):
    for keys, icon in _FEAT_ICONS:
        if any(k in text for k in keys):
            return icon
    return "fa-circle-check"


# شعارات الشركات (المولّد في utils.py): بنسجّل توزيع الشعارات على كل الشركات + شعارات logo_url الحقيقية
_logos_by_name = dict(COMPANY_LOGOS_BY_NAME)
for _p in all_props:
    if _p.get("company_name") and COMPANY_LOGOS_BY_ID.get(_p.get("company_id")):
        _logos_by_name[_p["company_name"]] = COMPANY_LOGOS_BY_ID[_p["company_id"]]
set_branding(
    build_logo_registry(tuple(sorted({(p.get("company_id") or 0, p["company_name"]) for p in all_props if p.get("company_name")}))),
    _logos_by_name,
)


def card_html(p):
    st_cls = status_cls(p["status"])
    raw_name = p.get("company_name")
    raw_logo = (p.get("company_logo") or COMPANY_LOGOS_BY_ID.get(p.get("company_id"))
                or COMPANY_LOGOS_BY_NAME.get(raw_name))
    p = safe(p)
    name = p.get("company_name")
    company_html = (
        f'<div class="prop-company">{company_logo_html(raw_name, raw_logo)}'
        f'<div class="prop-company-txt"><span>بواسطة</span><b>{name}</b></div></div>'
    ) if name else ""
    img = p["main_image"]
    ppm = f"{p['price_val'] // p['area']:,}"
    heart = '<div class="prop-fav"><i class="fa-solid fa-heart"></i></div>' if p["id"] in st.session_state.favorites else ""
    return (
        '<div class="prop-card-box">'
        f'<div class="prop-img-box"><div class="prop-img" style="background-image:url({img})"></div>'
        f'<div class="prop-badge">{p["type"]}</div>'
        f'<div class="prop-top-left">{heart}<div class="prop-status {st_cls}">{p["status"]}</div></div>'
        '<div class="prop-panel">'
        '<div class="prop-panel-top"><div>'
        f'<div class="prop-card-price">{p["price"]}<small>ج.م</small></div>'
        f'<div class="prop-card-ppm">{ppm} ج.م للمتر</div></div>'
        f'<div class="prop-idpill">#{p["id"]}</div></div>'
        f'<div class="prop-card-title">{p["title"]}</div>'
        '<div class="prop-panel-bottom">'
        f'<div class="prop-card-location"><i class="fa-solid fa-location-dot"></i>{p["location"]}</div>'
        '<div class="prop-card-specs">'
        f'<div class="prop-spec"><b><i class="fa-solid fa-bed"></i>{p["beds"]}</b><span>غرف</span></div>'
        f'<div class="prop-spec"><b><i class="fa-solid fa-bath"></i>{p["baths"]}</b><span>حمام</span></div>'
        f'<div class="prop-spec"><b><i class="fa-solid fa-ruler-combined"></i>{p["area"]}</b><span>م²</span></div>'
        '</div></div></div></div>'
        f'<div class="prop-card-content">{company_html}<div class="prop-chips">'
        f'<span class="chip">{p["finishing"]}</span><span class="chip">{floor_text(p)}</span>'
        f'<span class="chip">استلام: {p["delivery"]}</span></div></div>'
        '</div>'
    )


@st.dialog("تفاصيل العقار", width="large")
def show_property_modal(p):
    e = safe(p)
    imgs = [e["main_image"]] + e.get("gallery", [])[:2]
    while len(imgs) < 3:
        imgs.append(imgs[0])
    down = p["price_val"] * 0.10
    monthly = (p["price_val"] - down) / (8 * 12)
    feats = "".join(f'<div class="amen"><i class="fa-solid {feat_icon(f)}"></i>{f}</div>' for f in e.get("features", []))
    feats_block = f'<div class="dlg-h">المميزات</div><div class="amen-grid">{feats}</div>' if feats else ""
    ccomp = company_chip(p.get("company_name"))
    st.markdown(
        f'{ccomp}<div class="gal-grid">'
        f'<div class="gal-img main" style="background-image:url({imgs[0]})"></div>'
        f'<div class="gal-img" style="background-image:url({imgs[1]})"></div>'
        f'<div class="gal-img" style="background-image:url({imgs[2]})"></div></div>'
        '<div class="dlg-head"><div>'
        f'<div class="dlg-title">{e["title"]}</div>'
        f'<div class="dlg-sub"><i class="fa-solid fa-location-dot"></i> {e["location"]} · وحدة #{e["id"]}</div></div>'
        f'<div class="dlg-price">{e["price"]} ج.م</div></div>'
        '<div class="spec-grid">'
        f'<div class="spec-box"><div class="spec-ico"><i class="fa-solid fa-bed"></i></div><div class="spec-val">{e["beds"]}</div><div class="spec-lbl">غرف نوم</div></div>'
        f'<div class="spec-box"><div class="spec-ico"><i class="fa-solid fa-bath"></i></div><div class="spec-val">{e["baths"]}</div><div class="spec-lbl">حمامات</div></div>'
        f'<div class="spec-box"><div class="spec-ico"><i class="fa-solid fa-ruler-combined"></i></div><div class="spec-val">{e["area"]} م²</div><div class="spec-lbl">المساحة</div></div>'
        f'<div class="spec-box"><div class="spec-ico"><i class="fa-solid fa-layer-group"></i></div><div class="spec-val">{floor_text(p)}</div><div class="spec-lbl">الموقع بالمبنى</div></div>'
        f'<div class="spec-box"><div class="spec-ico"><i class="fa-solid fa-key"></i></div><div class="spec-val">{e["delivery"]}</div><div class="spec-lbl">الاستلام</div></div>'
        '</div>'
        f'<div style="margin-bottom:8px;"><span class="chip">{e["type"]}</span><span class="chip">{e["finishing"]}</span>'
        f'<span class="chip">{e["status"]}</span></div>'
        '<div class="dlg-h">عن العقار</div>'
        f'<p class="dlg-desc">{e["desc"]}</p>'
        f'{feats_block}'
        '<div class="fin-box">'
        f'<div><div class="k">سعر الوحدة</div><div class="v-xl">{e["price"]} ج.م</div></div>'
        f'<div><div class="k">مقدم تقديري (10%)</div><div class="v">{down:,.0f} ج.م</div></div>'
        f'<div><div class="k">قسط شهري تقديري (8 سنوات)</div><div class="v-hl">{monthly:,.0f} ج.م</div></div>'
        '<div class="fin-note"><i class="fa-solid fa-circle-info"></i>ملاحظة: تقدير تقريبي بدون فوائد. استخدم الحاسبة للتفاصيل</div>'
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


@st.dialog("مقارنة الوحدات", width="large")
def show_compare_modal():
    by_id = {p["id"]: p for p in all_props}
    ids = [i for i in st.session_state.compare if i in by_id]
    st.session_state.compare = ids
    units = [by_id[i] for i in ids]
    st.markdown(compare_view.CSS, unsafe_allow_html=True)
    if len(units) < 2:
        st.info("اختر وحدتين على الأقل من المعرض بالضغط على زر «قارن» في كارت الوحدة.")
        return
    st.markdown('<div class="cmp-hint"><i class="fa-solid fa-star"></i> الخانة المظللة هي الأفضل في كل بند.</div>',
                unsafe_allow_html=True)
    st.markdown(compare_view.build_table(units), unsafe_allow_html=True)
    cols = st.columns([0.22] + [1] * len(units))
    for col, p in zip(cols[1:], units):
        with col:
            if st.button("اسأل المستشار", key=f"cmp_ask_{p['id']}", icon=":material/support_agent:",
                         type="primary", width="stretch"):
                go_advisor(p)
            if st.button("حاسبة التمويل", key=f"cmp_calc_{p['id']}", icon=":material/calculate:", width="stretch"):
                go_calculator(p)
            st.button("إزالة من المقارنة", key=f"cmp_rm_{p['id']}", icon=":material/close:",
                      on_click=toggle_compare, args=(p["id"],), width="stretch")
    st.caption("القسط الشهري تقديري (مقدم 10% وباقي المبلغ على 8 سنوات بدون فوائد). للتفاصيل الدقيقة استخدم حاسبة التمويل.")


# ═══════════════════════════════════════════════════════════════
# 5) العنوان وشريط الإحصائيات
# ═══════════════════════════════════════════════════════════════
st.markdown(
    '<div class="page-head"><div class="page-title">معرض العقارات المتاحة</div>'
    '<p class="page-desc">تصفح أحدث الوحدات السكنية والاستثمارية، وقارن بين الأسعار، واحفظ ما يعجبك في المفضلة.</p></div>',
    unsafe_allow_html=True,
)

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
if not st.session_state.get("user"):
    st.caption("سجّل دخولك لحفظ مفضلتك على حسابك والرجوع لها في أي وقت.")
st.markdown("<br>", unsafe_allow_html=True)

_valid = [i for i in st.session_state.compare if i in {p["id"] for p in all_props}]
st.session_state.compare = _valid
if _valid:
    st.markdown("<style>.block-container{padding-bottom:130px !important;}</style>", unsafe_allow_html=True)
    _by_id = {p["id"]: p for p in all_props}
    _thumbs = "".join(
        f'<div class="cmp-thumb" style="background-image:url({safe(_by_id[i])["main_image"]})"></div>' for i in _valid
    )
    _thumbs += '<div class="cmp-thumb empty"><i class="fa-solid fa-plus"></i></div>' * (MAX_COMPARE - len(_valid))
    _hint = "جاهز للمقارنة" if len(_valid) >= 2 else "أضف وحدة أخرى على الأقل"
    with st.container(key="cmp_tray"):
        cb1, cb2, cb3 = st.columns([3, 1.3, 0.9])
        cb1.markdown(
            f'<div class="cmp-tray-info"><div class="cmp-thumbs">{_thumbs}</div>'
            f'<div><div class="cmp-tray-title">{len(_valid)} من {MAX_COMPARE} وحدات للمقارنة</div>'
            f'<div class="cmp-tray-sub">{_hint}</div></div></div>',
            unsafe_allow_html=True)
        if cb2.button("قارن الآن", icon=":material/compare_arrows:", type="primary",
                      disabled=len(_valid) < 2, width="stretch"):
            show_compare_modal()
        cb3.button("مسح", icon=":material/close:", on_click=lambda: st.session_state.update(compare=[]), width="stretch")

# ═══════════════════════════════════════════════════════════════
# 6) الفلاتر والترتيب
# ═══════════════════════════════════════════════════════════════
TYPE_OPTS = ["الكل"] + sorted({p["type"] for p in all_props})
CITY_OPTS = ["الكل"] + sorted({p["city"] for p in all_props})
COMPANY_OPTS = ["الكل"] + sorted({p["company_name"] for p in all_props if p.get("company_name")})
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
    st.session_state.f_company = "الكل"
    st.session_state.f_price = (MIN_M, MAX_M)
    st.session_state.f_beds = "الكل"
    st.session_state.f_sort = SORT_OPTS[0]
    st.session_state.f_fav = False


if st.session_state.get("f_company") not in COMPANY_OPTS:
    st.session_state.f_company = "الكل"
with st.container(key="filters_card"):
    st.markdown('<div class="filters-head"><i class="fa-solid fa-sliders"></i>تصفية النتائج</div>', unsafe_allow_html=True)
    r1 = st.columns([2.2, 1, 1.2, 1.4])
    f_search = r1[0].text_input("بحث", key="f_search", placeholder="المدينة، الكمبوند، أو رقم الوحدة مثل 15")
    f_type = r1[1].selectbox("نوع العقار", TYPE_OPTS, key="f_type")
    f_city = r1[2].selectbox("المنطقة", CITY_OPTS, key="f_city")
    f_company = r1[3].selectbox("الشركة", COMPANY_OPTS, key="f_company")

    st.markdown('<div class="filter-sep"></div>', unsafe_allow_html=True)
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
    if f_company != "الكل" and p.get("company_name") != f_company:
        continue
    if not (f_price[0] * 1e6 <= p["price_val"] <= f_price[1] * 1e6):
        continue
    if f_beds == "5+" and p["beds"] < 5:
        continue
    if f_beds not in ("الكل", "5+") and p["beds"] != int(f_beds):
        continue
    if f_fav and p["id"] not in st.session_state.favorites:
        continue
    if q and q not in f"{p['title']} {p['location']} {p['type']} {p.get('company_name') or ''}".lower() and q != str(p["id"]):
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
sig = (f_search, f_type, f_city, f_company, f_price, f_beds, f_sort, f_fav)
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
            with st.container(key=f"pcard_{prop['id']}"):
                st.markdown(card_html(prop), unsafe_allow_html=True)
                with st.container(key=f"pbtn_{prop['id']}"):
                    b1, b2, b3, b4 = st.columns([1.2, 1.2, 1, 1.1])
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
                    with b4:
                        in_cmp = prop["id"] in st.session_state.compare
                        st.button("مُضافة" if in_cmp else "قارن", key=f"cmp_{prop['id']}",
                                  icon=":material/check_circle:" if in_cmp else ":material/compare_arrows:",
                                  on_click=toggle_compare, args=(prop["id"],), width="stretch")

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