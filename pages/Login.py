import time

import streamlit as st

import auth
import session

st.set_page_config(
    page_title="تسجيل الدخول | Aqarify",
    page_icon=":material/login:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    :root { --dark:#14161C; --accent:#C9A24B; --bg:#FAFAF8; --border:#E4E2DA; }
    html, body, .stApp { direction: rtl; }
    .stApp { background: var(--bg); color: var(--dark); }
    .stApp *:not(i):not([data-testid="stIconMaterial"]) { font-family: 'Cairo', sans-serif !important; }
    .stApp [data-testid="stMarkdownContainer"] { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }
    .login-title { font-size: 34px; font-weight: 800; margin: 10px 0 4px; }
    .login-title span { color: var(--accent); }
    .login-sub { color: #666; margin-bottom: 18px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; }
    [data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--accent); color: var(--dark); border: 1px solid var(--accent);
        font-weight: 700; border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

MAX_ATTEMPTS = 5
LOCK_SECONDS = 60

st.markdown('<div class="login-title">Aqarify<span>.</span></div>'
            '<div class="login-sub">سجّل دخولك أو أنشئ حساباً جديداً</div>',
            unsafe_allow_html=True)

user = session.current_user()
if user:
    st.success(f"أنت مسجّل دخول باسم {user['name']} ({'أدمن' if user['role'] == 'admin' else 'مستخدم'}).")
    c1, c2 = st.columns(2)
    if c1.button("الرئيسية", width="stretch"):
        st.switch_page("App.py")
    if c2.button("تسجيل الخروج", width="stretch"):
        session.logout_user()
        st.rerun()
    st.stop()

tab_login, tab_reg = st.tabs(["تسجيل الدخول", "حساب جديد"])

with tab_login:
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        go = st.form_submit_button("دخول", type="primary", width="stretch")

    if go:
        locked_until = st.session_state.get("lock_until", 0)
        if time.time() < locked_until:
            st.error(f"محاولات كثيرة. جرّب بعد {int(locked_until - time.time())} ثانية.")
        else:
            u = auth.authenticate(email, password)
            if u:
                st.session_state["fail_count"] = 0
                session.login_user(u)
                st.switch_page("App.py")
            else:
                st.session_state["fail_count"] = st.session_state.get("fail_count", 0) + 1
                if st.session_state["fail_count"] >= MAX_ATTEMPTS:
                    st.session_state["lock_until"] = time.time() + LOCK_SECONDS
                    st.session_state["fail_count"] = 0
                st.error("البريد أو كلمة المرور غير صحيحة.")

with tab_reg:
    with st.form("register_form", clear_on_submit=True):
        r_name = st.text_input("الاسم")
        r_email = st.text_input("البريد الإلكتروني", key="r_email")
        r_pw1 = st.text_input("كلمة المرور (8 أحرف على الأقل)", type="password", key="r_pw1")
        r_pw2 = st.text_input("أعد كتابة كلمة المرور", type="password", key="r_pw2")
        reg = st.form_submit_button("إنشاء حساب", type="primary", width="stretch")

    if reg:
        if r_pw1 != r_pw2:
            st.error("كلمتا المرور غير متطابقتين.")
        else:
            # التسجيل العام دايماً role=user، الأدمن بيتعمل من الـ Terminal بس
            ok, msg = auth.create_user(r_name, r_email, r_pw1, role="user")
            (st.success if ok else st.error)(msg + (" سجّل دخولك من التبويب الأول." if ok else ""))