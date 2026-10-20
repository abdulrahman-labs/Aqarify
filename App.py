import streamlit as st

st.set_page_config(
    page_title="Aqarify | بيتك القادم يبدأ من هنا",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# ─── إدارة حالة تسجيل دخول الأدمن ───
if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False

# ─── التنسيق البصري الشامل (CSS & Theme Variables) ───
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;800&display=swap');

    :root {
        --color-dark: #14161C;
        --color-white: #FFFFFF;
        --color-accent: #C9A24B;
        --color-bg: #FAFAF8;
        --color-border: #E4E2DA;
        --color-text-muted: #666666;
    }

    /* تطبيق خط Cairo بأوزانه وأحجامه بدقة على كافة العناصر */
    html, body, [class*="css"], .stApp, div, p, span, h1, h2, h3, h4, h5, h6, button, input {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        background-color: var(--color-bg) !important;
        color: var(--color-dark) !important;
    }

    /* إخفاء شريط Streamlit الجانبي */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ─── الهيدر والشعار مع الأيقونة المربعة المكبرة ─── */
    .brand-logo-link {
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 14px;
    }
    .brand-icon-box {
        background: var(--color-dark);
        color: var(--color-accent);
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(20, 22, 28, 0.15);
    }
    .brand-logo-text {
        font-size: 34px !important;
        font-weight: 800 !important;
        color: var(--color-dark) !important;
        line-height: 1 !important;
        margin: 0 !important;
    }
    .brand-logo-dot {
        color: var(--color-accent) !important;
    }
    .brand-logo-sub {
        font-size: 13px !important;
        font-weight: 400 !important;
        color: var(--color-text-muted) !important;
        margin-top: 4px !important;
        display: block;
    }

    /* ─── شريط التنقل (st.page_link) ─── */
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
    .st-key-topnav [data-testid="stPageLink-NavLink"] * { background: transparent !important; }
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
    .st-key-topnav [data-testid="stPageLink-NavLink"][href*="Login"]::before      { content: "\\f2f6"; }

    .st-key-topnav [data-testid="stPageLink-NavLink"]:hover { color: var(--color-accent) !important; }
    /* الصفحة الحالية = الرئيسية (أي رابط مش من الروابط التانية) */
    .st-key-topnav [data-testid="stPageLink-NavLink"]:not([href*="Properties"]):not([href*="Customer"]):not([href*="Calculator"]):not([href*="Admin"]):not([href*="Login"]) {
        color: var(--color-accent) !important;
    }
    .st-key-topnav [data-testid="stPageLink-NavLink"]:not([href*="Properties"]):not([href*="Customer"]):not([href*="Calculator"]):not([href*="Admin"]):not([href*="Login"])::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 100%; height: 2px; background: var(--color-accent);
    }

    /* ─── الهيرو ─── */
    .hero-title-main {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: var(--color-dark) !important;
        line-height: 1.3 !important;
        margin-bottom: 12px !important;
    }
    .hero-title-sub {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: var(--color-accent) !important;
        margin-bottom: 20px !important;
    }
    .hero-desc {
        font-size: 17px !important;
        font-weight: 400 !important;
        line-height: 1.9 !important;
        color: var(--color-text-muted) !important;
        margin-bottom: 35px !important;
    }

    /* ─── الأزرار الرئيسية (مربوطة بالـ key عشان التنسيق يتطبق فعلاً) ─── */
    .st-key-hero_chat button, .st-key-cta_bottom_btn button,
    .st-key-hero_explore button, .st-key-all_props_btn button {
        min-height: 56px !important;
        padding: 0 28px !important;
        border-radius: 14px !important;
        cursor: pointer !important;
        transition: transform .25s ease, box-shadow .25s ease, background .25s ease,
                    color .25s ease, border-color .25s ease, filter .25s ease !important;
    }
    .st-key-hero_chat button *, .st-key-cta_bottom_btn button *,
    .st-key-hero_explore button *, .st-key-all_props_btn button * {
        background: transparent !important;
        color: inherit !important;
        font-size: 17px !important;
        font-weight: 800 !important;
        text-align: center !important;
    }
    .st-key-hero_chat button p::before, .st-key-cta_bottom_btn button p::before,
    .st-key-hero_explore button p::before, .st-key-all_props_btn button p::before {
        font-family: "Font Awesome 6 Free" !important; font-weight: 900 !important;
        display: inline-block; margin-left: 10px; font-size: 16px;
        transition: transform .25s ease, color .25s ease;
    }
    .st-key-hero_chat button p::before      { content: "\\f086"; }
    .st-key-cta_bottom_btn button p::before { content: "\\f135"; }
    .st-key-hero_explore button p::before   { content: "\\f1ad"; }
    .st-key-all_props_btn button p::before  { content: "\\f1ad"; }

    /* زر ذهبي (Primary) */
    .st-key-hero_chat button, .st-key-cta_bottom_btn button {
        background: linear-gradient(135deg, #DDB964 0%, #C9A24B 100%) !important;
        color: var(--color-dark) !important;
        border: 1px solid var(--color-accent) !important;
        box-shadow: 0 4px 14px rgba(201, 162, 75, 0.28) !important;
    }
    .st-key-hero_chat button:hover, .st-key-cta_bottom_btn button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 28px rgba(201, 162, 75, 0.5) !important;
        filter: brightness(1.06);
    }
    .st-key-hero_chat button:hover p::before, .st-key-cta_bottom_btn button:hover p::before {
        transform: translateX(-4px) scale(1.2) rotate(-8deg);
    }

    /* زر بإطار (Outline) */
    .st-key-hero_explore button, .st-key-all_props_btn button {
        background: var(--color-white) !important;
        color: var(--color-dark) !important;
        border: 1.5px solid var(--color-dark) !important;
        box-shadow: 0 2px 8px rgba(20, 22, 28, 0.06) !important;
    }
    .st-key-hero_explore button:hover, .st-key-all_props_btn button:hover {
        background: var(--color-dark) !important;
        color: var(--color-white) !important;
        border-color: var(--color-dark) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 28px rgba(20, 22, 28, 0.28) !important;
    }
    .st-key-hero_explore button:hover p::before, .st-key-all_props_btn button:hover p::before {
        color: var(--color-accent) !important;
        transform: translateX(-4px) scale(1.2);
    }

    /* ضغطة الزر */
    .st-key-hero_chat button:active, .st-key-cta_bottom_btn button:active,
    .st-key-hero_explore button:active, .st-key-all_props_btn button:active {
        transform: translateY(0) scale(0.97) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }

    /* صورة الهيرو والإحصائية */
    .hero-img-box {
        position: relative;
        width: 100%;
        border-radius: 24px;
        overflow: hidden;
        border: 1px solid var(--color-border);
    }
    .hero-img-box img {
        width: 100%;
        height: 420px;
        object-fit: cover;
        display: block;
    }
    .floating-stats-card {
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid var(--color-border);
        border-radius: 16px;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }

    /* ─── الكروت العامة للخدمات والعقارات ─── */
    .custom-card {
        background-color: var(--color-white) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        height: 100% !important;
        transition: all 0.3s ease !important;
    }
    .custom-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 28px rgba(0,0,0,0.06) !important;
        border-color: var(--color-accent) !important;
    }

    /* كروت خطوات كيف يعمل */
    .step-card {
        background-color: var(--color-white) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 20px !important;
        padding: 28px 20px !important;
        text-align: center !important;
        position: relative;
        height: 100%;
    }
    .step-number {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background-color: var(--color-accent);
        color: var(--color-dark);
        font-weight: 800;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px auto;
    }

    /* كروت العقارات المميزة */
    .prop-card-home {
        background-color: var(--color-white);
        border: 1px solid var(--color-border);
        border-radius: 20px;
        overflow: hidden;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .prop-card-home:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.06);
        border-color: var(--color-accent);
    }
    .prop-card-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .prop-card-body {
        padding: 18px;
    }

    /* بانر دعوة للتصرف CTA */
    .cta-banner {
        background-color: var(--color-dark) !important;
        border-radius: 24px !important;
        padding: 45px 30px !important;
        text-align: center !important;
        color: var(--color-white) !important;
        margin: 40px 0 !important;
    }

    /* الفوتر Footer */
    .footer-box {
        background-color: var(--color-white);
        border-top: 1px solid var(--color-border);
        padding: 40px 0 20px 0;
        margin-top: 60px;
    }
    .footer-link {
        color: var(--color-dark) !important;
        text-decoration: none !important;
        display: block;
        margin-bottom: 8px;
        font-size: 15px;
    }
    .footer-link:hover {
        color: var(--color-accent) !important;
    }

    #MainMenu, footer {visibility: hidden;}

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
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ─── 2. الشعار والهيدر العلوي ───
col_header_right, col_header_left = st.columns([1.4, 3])

with col_header_right:
    st.markdown("""
    <a href="?page=home" target="_self" class="brand-logo-link">
        <div class="brand-icon-box"><i class="fa-solid fa-building-columns"></i></div>
        <div>
            <div class="brand-logo-text">Aqarify<span class="brand-logo-dot">.</span></div>
            <span class="brand-logo-sub">بيتك القادم يبدأ من هنا</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col_header_left:
    with st.container(key="topnav"):
        st.page_link("App.py", label="الرئيسية")
        st.page_link("pages/Properties.py", label="معرض العقارات")
        st.page_link("pages/Customer Service.py", label="المستشار الذكي")
        st.page_link("pages/Calculator.py", label="حاسبة التمويل")
        if st.session_state.get("is_admin_logged_in", False):
            st.page_link("pages/Admin.py", label="لوحة الإدارة")
        if st.session_state.get("user"):
            st.page_link("pages/Login.py", label="حسابي")
        else:
            st.page_link("pages/Login.py", label="تسجيل الدخول")

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

st.markdown("<hr style='margin: 15px 0 35px 0; border-color: var(--color-border);'>", unsafe_allow_html=True)

# ─── 3. قسم الـ Hero والأزرار ───
col_hero_text, col_hero_img = st.columns([1.1, 1.1])

with col_hero_text:
    st.markdown("<div class='hero-title-main'>مستقبل السكن العقاري الذكي</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title-sub'>Future of Modern Living</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-desc'>
        نقدم لك أرقى المجتمعات السكنية والوحدات الفاخرة، مع تجربة استشارة فورية معززة بالذكاء الاصطناعي لاختيار العقار المالي والسكني الأمثل لك ولأسرتك.
    </div>
    """, unsafe_allow_html=True)

    btn_c1, btn_c2 = st.columns([1, 1])
    with btn_c1:
        if st.button("تحدث مع المستشار الذكي", key="hero_chat", width="stretch"):
            st.switch_page("pages/Customer Service.py")

    with btn_c2:
        if st.button("استكشف المعرض", key="hero_explore", width="stretch"):
            st.switch_page("pages/Properties.py")

with col_hero_img:
    st.markdown("""
    <div class="hero-img-box">
        <img src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80" alt="Aqarify Architecture">
        <div class="floating-stats-card">
            <div style="font-size: 24px; color: var(--color-accent);"><i class="fa-solid fa-shield-halved"></i></div>
            <div>
                <div style="font-weight: 800; font-size: 16px; color: var(--color-dark);">+500 وحدة موثوقة</div>
                <div style="font-size: 13px; color: var(--color-text-muted);">استثمار سكني آمن ومعتمد</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# ─── 4. الأقسام الجديدة بالترتيب بينها مسافة 80px ───

# أ) "لماذا نحن"
st.markdown("<h2 style='text-align: center; font-weight: 800; font-size: 32px; margin-bottom: 35px;'>لماذا نحن؟</h2>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

features = [
    {"icon": "fa-headset", "title": "مستشار ذكي 24/7", "desc": "إجابات فورية واستشارات دقيقة مجهزة بالذكاء الاصطناعي على مدار الساعة."},
    {"icon": "fa-file-contract", "title": "عقود موثقة", "desc": "ضمان قانوني كامل لكافة المعاملات العقارية لضمان استثمارك بشكل آمن."},
    {"icon": "fa-gem", "title": "تشطيبات فاخرة", "desc": "اختيارات حصرية من أفضل الوحدات ذات التشطيب المودرن والأولتر ألوكس."},
    {"icon": "fa-calculator", "title": "تمويل مرن", "desc": "خطط سداد وأقساط مريحة تناسب مختلف الميزانيات بدفعات مقدمة بسيطة."}
]

cols_feat = [c1, c2, c3, c4]
for idx, feat in enumerate(features):
    with cols_feat[idx]:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 32px; color: var(--color-accent); margin-bottom: 12px;"><i class="fa-solid {feat['icon']}"></i></div>
            <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">{feat['title']}</h3>
            <p style="font-size: 17px; font-weight: 400; line-height: 1.9; color: var(--color-text-muted); margin: 0;">{feat['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# ب) "كيف يعمل"
st.markdown("<h2 style='text-align: center; font-weight: 800; font-size: 32px; margin-bottom: 35px;'>كيف يعمل Aqarify؟</h2>", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

steps = [
    {"num": "1", "title": "اسأل المستشار", "desc": "ناقش متطلباتك وميزانيتك مع مستشارنا الذكي لتحصل على ترشيحات فورية."},
    {"num": "2", "title": "اختر عقارك", "desc": "تصفح الصور الحقيقية والمواصفات الكاملة للوحدة المناسبة من المعرض."},
    {"num": "3", "title": "احجز موعد المعاينة", "desc": "تواصل مع فريق الدعم البشري لحجز زيارة ميدانية ومعاينة الموقع."}
]

cols_step = [s1, s2, s3]
for idx, stp in enumerate(steps):
    with cols_step[idx]:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-number">{stp['num']}</div>
            <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">{stp['title']}</h3>
            <p style="font-size: 17px; font-weight: 400; line-height: 1.9; color: var(--color-text-muted); margin: 0;">{stp['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# ج) "عقارات مميزة"
st.markdown("<h2 style='font-weight: 800; font-size: 32px; margin-bottom: 25px;'>عقارات مميزة</h2>", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)

featured_props = [
    {
        "title": "فيلا مودرن بمسبح خاص وحديقة",
        "location": "التجمع الخامس - القاهرة الجديدة",
        "price": "12,000,000 ج.م",
        "img": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
    },
    {
        "title": "شقة عصرية بفيو بانورامي",
        "location": "الشيخ زايد - 6 أكتوبر",
        "price": "3,500,000 ج.م",
        "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    },
    {
        "title": "بنتاهاوس فاخر بروف خاص",
        "location": "العاصمة الإدارية الجديدة",
        "price": "5,800,000 ج.م",
        "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    }
]

cols_prop = [p1, p2, p3]
for idx, prp in enumerate(featured_props):
    with cols_prop[idx]:
        st.markdown(f"""
        <div class="prop-card-home">
            <img src="{prp['img']}" class="prop-card-img" alt="{prp['title']}">
            <div class="prop-card-body">
                <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 6px;">{prp['title']}</h3>
                <div style="font-size: 14px; color: var(--color-text-muted); margin-bottom: 12px;"><i class="fa-solid fa-location-dot"></i> {prp['location']}</div>
                <div style="font-size: 20px; font-weight: 800; color: var(--color-accent);">{prp['price']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
col_btn_center = st.columns([1, 1.2, 1])
with col_btn_center[1]:
    if st.button("عرض كل العقارات", key="all_props_btn", width="stretch"):
        st.switch_page("pages/Properties.py")

st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# د) "آراء العملاء"
st.markdown("<h2 style='text-align: center; font-weight: 800; font-size: 32px; margin-bottom: 35px;'>آراء العملاء</h2>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)

reviews = [
    {"name": "أحمد الشريف", "text": "تجربة استثنائية! المستشار الذكي ساعدني في تحديد الشقة المناسبة بميزانيتي بالضبط قبل المعاينة.", "stars": 5},
    {"name": "م. سارة محمود", "text": "السرعة في التواصل والدقة في عرض المساحات الهندسية جعلت عملية الشراء سهلة وموثوقة جداً.", "stars": 5},
    {"name": "د. كريم عبد العزيز", "text": "منصة ممتازة وحاسبة التمويل كانت دقيقة جداً في حساب القسط الشهري بدون مفاجآت.", "stars": 5}
]

cols_rev = [t1, t2, t3]
for idx, rev in enumerate(reviews):
    with cols_rev[idx]:
        st.markdown(f"""
        <div class="custom-card">
            <div style="color: var(--color-accent); margin-bottom: 10px; font-size: 16px;">
                <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
            </div>
            <p style="font-size: 17px; font-weight: 400; line-height: 1.9; color: var(--color-text-muted); margin-bottom: 15px;">"{rev['text']}"</p>
            <h4 style="font-size: 18px; font-weight: 700; margin: 0;">{rev['name']}</h4>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# هـ) بانر دعوة للتصرف CTA
st.markdown("""
<div class="cta-banner">
    <h2 style="font-size: 32px; font-weight: 800; color: var(--color-white) !important; margin-bottom: 12px;">جاهز تلاقي بيتك؟</h2>
    <p style="font-size: 17px; font-weight: 400; color: #CCCCCC !important; margin-bottom: 25px;">ابدأ الآن محادثتك مع المستشار العقاري الذكي واكتشف أفضل الفرص المتاحة.</p>
</div>
""", unsafe_allow_html=True)

col_cta_btn = st.columns([1, 1.2, 1])
with col_cta_btn[1]:
    if st.button("ابدأ المحادثة الآن", key="cta_bottom_btn", width="stretch"):
        st.switch_page("pages/Customer Service.py")

# و) فوتر الشعار والروابط
st.markdown("""
<div class="footer-box">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px; margin-bottom: 30px;">
            <div style="max-width: 340px;">
                <a href="?page=home" target="_self" class="brand-logo-link" style="margin-bottom: 10px;">
                    <div class="brand-icon-box"><i class="fa-solid fa-building-columns"></i></div>
                    <div>
                        <div class="brand-logo-text">Aqarify<span class="brand-logo-dot">.</span></div>
                        <span class="brand-logo-sub">بيتك القادم يبدأ من هنا</span>
                    </div>
                </a>
                <p style="font-size: 15px; color: var(--color-text-muted); line-height: 1.7; margin-top: 8px;">المنصة العقارية الذكية الأولى للحلول السكنية والاستثمارية الموثوقة.</p>
            </div>
            <div>
                <h4 style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">روابط سريعة</h4>
                <a href="?page=home" target="_self" class="footer-link">الرئيسية</a>
                <a href="?page=props" target="_self" class="footer-link">معرض العقارات</a>
                <a href="?page=chat" target="_self" class="footer-link">المستشار الذكي</a>
                <a href="?page=calc" target="_self" class="footer-link">حاسبة التمويل</a>
            </div>
            <div>
                <h4 style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">بيانات التواصل</h4>
                <p style="font-size: 15px; color: var(--color-text-muted); margin-bottom: 6px;"><i class="fa-solid fa-phone"></i> +20 100 000 0000</p>
                <p style="font-size: 15px; color: var(--color-text-muted); margin-bottom: 6px;"><i class="fa-solid fa-envelope"></i> support@aqarify.com</p>
                <p style="font-size: 15px; color: var(--color-text-muted);"><i class="fa-solid fa-location-dot"></i> القاهرة، مصر</p>
            </div>
        </div>
        <hr style="border-color: var(--color-border); margin-bottom: 20px;">
        <div style="text-align: center; font-size: 14px; color: var(--color-text-muted);">
            جميع الحقوق محفوظة © 2026 منصة Aqarify العقارية.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)