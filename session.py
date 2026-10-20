import streamlit as st

LOGIN_PAGE = "pages/Login.py"


def current_user():
    return st.session_state.get("user")


def login_user(user):
    st.session_state["user"] = user
    # نفس المفتاح اللي صفحات الموقع الحالية بتستخدمه في الـ Nav
    st.session_state["is_admin_logged_in"] = user["role"] == "admin"


def logout_user():
    st.session_state.pop("user", None)
    st.session_state["is_admin_logged_in"] = False


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