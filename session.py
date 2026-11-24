import streamlit as st
import streamlit.components.v1 as components

import auth

LOGIN_PAGE = "pages/Login.py"
COOKIE = "aq_session"
MAX_AGE = auth.SESSION_DAYS * 86400


def _flush_cookie():
    """ينفّذ (مرة واحدة) أمر كتابة/مسح الكوكي اللي اتسجّل وقت login/logout."""
    op = st.session_state.pop("_cookie_op", None)
    if op:
        value, age = op
        components.html(
            f"<script>try{{window.parent.document.cookie="
            f"'{COOKIE}={value}; path=/; max-age={age}; SameSite=Lax';}}catch(e){{}}</script>",
            height=0)


def restore_login():
    """نادي عليها في أول كل صفحة (بعد set_page_config): بترجّع الدخول من الكوكي بعد Refresh."""
    if "is_admin_logged_in" not in st.session_state:
        st.session_state["is_admin_logged_in"] = False
    if not st.session_state.get("user"):
        try:
            token = st.context.cookies.get(COOKIE)
        except Exception:
            token = None
        user = auth.user_from_token(token)
        if user:
            st.session_state["user"] = user
            st.session_state["is_admin_logged_in"] = user["role"] == "admin"
            st.session_state["_session_token"] = token
    _flush_cookie()


def current_user():
    restore_login()
    return st.session_state.get("user")


def login_user(user):
    st.session_state["user"] = user
    # نفس المفتاح اللي صفحات الموقع الحالية بتستخدمه في الـ Nav
    st.session_state["is_admin_logged_in"] = user["role"] == "admin"
    token = auth.create_session(user["id"])
    st.session_state["_session_token"] = token
    st.session_state["_cookie_op"] = (token, MAX_AGE)


def logout_user():
    auth.delete_session(st.session_state.pop("_session_token", None))
    st.session_state.pop("user", None)
    st.session_state["is_admin_logged_in"] = False
    st.session_state["_cookie_op"] = ("", 0)


def require_role(role=None):
    """حط السطر ده في أول أي صفحة محمية. لو مفيش صلاحية بيوقف الصفحة."""
    user = current_user()
    if not user:
        st.warning("لازم تسجّل الدخول الأول.")
        st.page_link(LOGIN_PAGE, label="تسجيل الدخول")
        st.stop()
    if role and user["role"] != role:
        st.error("ليس لديك صلاحية الوصول لهذه الصفحة.")
        st.stop()
    return user