import streamlit as st

st.set_page_config(
    page_title="Aqarify | بيتك القادم يبدأ من هنا",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# ─── PWA Injector ───
pwa_code = """
<script>
  // 1. إضافة Meta Tags الخاصة بالتطبيق
  if (!document.querySelector('link[rel="manifest"]')) {
    const manifestLink = document.createElement('link');
    manifestLink.rel = 'manifest';
    manifestLink.href = '/manifest.json';
    document.head.appendChild(manifestLink);
  }

  // 2. ضبط إعدادات العرض الشاشي للموبايل
  const metaTheme = document.createElement('meta');
  metaTheme.name = 'theme-color';
  metaTheme.content = '#14161C';
  document.head.appendChild(metaTheme);

  const metaApp = document.createElement('meta');
  metaApp.name = 'apple-mobile-web-app-capable';
  metaApp.content = 'yes';
  document.head.appendChild(metaApp);
</script>
"""
st.markdown(pwa_code, unsafe_allow_html=True)
st.markdown("""
<div style="background: linear-gradient(135deg, #14161C 0%, #1E222B 100%); border: 1.5px solid #C9A24B; padding: 18px 22px; border-radius: 14px; margin: 15px 0 25px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 8px;">
        <span style="font-size: 22px;">📲</span>
        <h4 style="color: #FFFFFF; font-size: 17px; margin: 0; font-family: 'Cairo', sans-serif;">نزّل تطبيق Aqarify على هاتفك</h4>
    </div>
    <p style="color: #B0B5C1; font-size: 13px; margin: 0 0 12px 0; font-family: 'Cairo', sans-serif;">لتجربة أسرع وتصفح العقارات بشاشة كاملة مثل التطبيقات الرسمية:</p>
    <div style="background: rgba(201, 162, 75, 0.1); border: 1px dashed #C9A24B; padding: 8px 12px; border-radius: 8px; display: inline-block;">
        <span style="color: #C9A24B; font-weight: bold; font-size: 13px; font-family: 'Cairo', sans-serif;">
            افتح قائمة المتصفح ( <span style="font-size: 16px;">⋮</span> ) واضغط على <span style="color: #FFF; background: #C9A24B; color: #14161C; padding: 2px 6px; border-radius: 4px;">إضافة إلى الشاشة الرئيسية</span>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
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

    /* Navbar Links */
    .nav-bar-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 28px;
        padding-top: 10px;
    }
    .nav-link {
        position: relative;
        color: var(--color-dark) !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        transition: color 0.2s ease;
    }
    .nav-link:hover, .nav-link.active {
        color: var(--color-accent) !important;
    }
    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 100%;
        height: 2px;
        background-color: var(--color-accent);
    }

    /* ─── الهيرو ورسوخ الأزرار ─── */
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

    /* أزرار Streamlit المخصصة بالألوان والتأثيرات */
    .stButton>button {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    /* زر أساسي (Primary) */
    .btn-hero-primary>button {
        background-color: var(--color-accent) !important;
        color: var(--color-dark) !important;
        border: none !important;
        padding: 14px 28px !important;
        font-size: 17px !important;
        width: 100% !important;
    }
    .btn-hero-primary>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(201, 162, 75, 0.35) !important;
    }

    /* زر ثانوي (Outline) */
    .btn-hero-outline>button {
        background-color: transparent !important;
        color: var(--color-dark) !important;
        border: 1px solid var(--color-dark) !important;
        padding: 14px 28px !important;
        font-size: 17px !important;
        width: 100% !important;
    }
    .btn-hero-outline>button:hover {
        background-color: var(--color-dark) !important;
        color: var(--color-white) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(20, 22, 28, 0.2) !important;
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
</style>
""", unsafe_allow_html=True)

# ─── 2. الشعار والهيدر العلوي ───
col_header_right, col_header_left = st.columns([1.5, 2.2])

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
    # إظهار رابط لوحة الإدارة فقط إذا سجل الأدمن دخوله
    admin_link_html = ""
    if st.session_state.get("is_admin_logged_in", False):
        admin_link_html = """
        <a href="?page=admin" target="_self" class="nav-link">
            <i class="fa-solid fa-sliders"></i> لوحة الإدارة
        </a>
        """

    st.markdown(f"""
    <div class="nav-bar-container">
        <a href="?page=home" target="_self" class="nav-link active">
            <i class="fa-solid fa-house"></i> الرئيسية
        </a>
        <a href="?page=props" target="_self" class="nav-link">
            <i class="fa-solid fa-city"></i> معرض العقارات
        </a>
        <a href="?page=chat" target="_self" class="nav-link">
            <i class="fa-solid fa-user-tie"></i> المستشار الذكي
        </a>
        <a href="?page=calc" target="_self" class="nav-link">
            <i class="fa-solid fa-calculator"></i> حاسبة التمويل
        </a>
        {admin_link_html}
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("<div class='btn-hero-primary'>", unsafe_allow_html=True)
        if st.button("تحدث مع المستشار الذكي 💬", width="stretch"):
            st.switch_page("pages/Customer Service.py")
        st.markdown("</div>", unsafe_allow_html=True)

    with btn_c2:
        st.markdown("<div class='btn-hero-outline'>", unsafe_allow_html=True)
        if st.button("استكشف المعرض 🏢", width="stretch"):
            st.switch_page("pages/Properties.py")
        st.markdown("</div>", unsafe_allow_html=True)

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

st.markdown("<div style='margin-top: 20px; text-align: center;'>", unsafe_allow_html=True)
col_btn_center = st.columns([1, 1.2, 1])
with col_btn_center[1]:
    st.markdown("<div class='btn-hero-outline'>", unsafe_allow_html=True)
    if st.button("عرض كل العقارات 🏢", width="stretch"):
        st.switch_page("pages/Properties.py")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

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
    st.markdown("<div class='btn-hero-primary'>", unsafe_allow_html=True)
    if st.button("ابدأ المحادثة الآن 🚀", key="cta_bottom_btn", width="stretch"):
        st.switch_page("pages/Customer Service.py")
    st.markdown("</div>", unsafe_allow_html=True)

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
# في نهاية ملف App.py خالص
st.markdown("---")
st.markdown("<h3 style='text-align: center; font-size: 18px;'>تطبيق الهاتف</h3>", unsafe_allow_html=True)

