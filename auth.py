import getpass
import hashlib
import math
import re
import secrets
import sqlite3
import sys
import time

import bcrypt

import db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8
SESSION_DAYS = 14


def init_users_table():
    conn = db.get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'user'
                              CHECK (role IN ('admin', 'user')),
                company_id    INTEGER REFERENCES companies(id),
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
    finally:
        conn.close()


def _hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _public(row):
    """بيانات المستخدم للواجهة. حساب الشركة = role 'user' + company_id (من غير تغيير قيد role في الجدول)."""
    role = "company" if row["role"] == "user" and row["company_id"] else row["role"]
    return {"id": row["id"], "name": row["name"], "email": row["email"],
            "role": role, "company_id": row["company_id"]}


def create_user(name, email, password, role="user", company_id=None):
    """يرجّع (نجح؟, رسالة)."""
    name, email = name.strip(), email.strip().lower()
    if not name:
        return False, "الاسم مطلوب."
    if not EMAIL_RE.match(email):
        return False, "البريد الإلكتروني غير صحيح."
    if len(password) < MIN_PASSWORD:
        return False, f"كلمة المرور لازم تكون {MIN_PASSWORD} أحرف على الأقل."
    if len(password.encode("utf-8")) > 72:
        return False, "كلمة المرور طويلة جداً (الحد الأقصى 72 بايت)."
    if role not in ("admin", "user"):
        return False, "صلاحية غير معروفة."
    if company_id and not db.get_company(company_id):
        return False, "الشركة غير موجودة."

    init_users_table()
    conn = db.get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role, company_id) VALUES (?,?,?,?,?)",
            (name, email, _hash(password), role, company_id or None),
        )
        conn.commit()
        return True, "تم إنشاء الحساب."
    except sqlite3.IntegrityError:
        return False, "هذا البريد مسجّل بالفعل."
    finally:
        conn.close()


def authenticate(email, password):
    """يرجّع بيانات المستخدم (من غير الهاش) أو None لو البيانات غلط."""
    init_users_table()
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT id, name, email, role, company_id, password_hash FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))
    except ValueError:
        return None
    if not ok:
        return None
    return _public(row)


# ═══════════════════════════════════════════════════════════════
# جلسات الدخول الدائمة (تفضل شغالة بعد Refresh)
#   بنخزّن هاش التوكن بس (مش التوكن نفسه) في جدول sessions
# ═══════════════════════════════════════════════════════════════
def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def init_sessions_table():
    conn = db.get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sess_user ON sessions(user_id);
        """)
        conn.commit()
    finally:
        conn.close()


def create_session(user_id):
    """يعمل توكن عشوائي جديد ويرجّعه (بيتخزّن هاشه بس)."""
    init_sessions_table()
    token = secrets.token_urlsafe(32)
    conn = db.get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= datetime('now')")
            conn.execute(
                "INSERT INTO sessions (token_hash, user_id, expires_at) "
                "VALUES (?,?,datetime('now', ?))",
                (_token_hash(token), user_id, f"+{SESSION_DAYS} days"))
        return token
    finally:
        conn.close()


def user_from_token(token):
    """يرجّع بيانات المستخدم لو التوكن سليم وما انتهاش، وإلا None."""
    if not token:
        return None
    init_users_table()
    init_sessions_table()
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT u.id, u.name, u.email, u.role, u.company_id FROM sessions s "
            "JOIN users u ON u.id = s.user_id "
            "WHERE s.token_hash = ? AND s.expires_at > datetime('now')",
            (_token_hash(token),)).fetchone()
        return _public(row) if row else None
    finally:
        conn.close()


def delete_session(token):
    if not token:
        return
    init_sessions_table()
    conn = db.get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# قفل محاولات الدخول (على القاعدة، فمبيتصفّرش بالـ Refresh)
# ═══════════════════════════════════════════════════════════════
MAX_ATTEMPTS = 5
LOCK_SECONDS = 60


def _akey(email):
    return (email or "").strip().lower()[:254]


def init_attempts_table():
    conn = db.get_conn()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS login_attempts ("
                     "email TEXT PRIMARY KEY, fails INTEGER NOT NULL DEFAULT 0, "
                     "locked_until REAL NOT NULL DEFAULT 0)")
        conn.commit()
    finally:
        conn.close()


def lock_remaining(email):
    """عدد الثواني المتبقية على فك القفل (0 = مش مقفول)."""
    init_attempts_table()
    conn = db.get_conn()
    try:
        row = conn.execute("SELECT locked_until FROM login_attempts WHERE email = ?", (_akey(email),)).fetchone()
    finally:
        conn.close()
    return max(0, math.ceil(row[0] - time.time())) if row else 0


def register_failure(email):
    """يسجّل محاولة فاشلة، وبعد MAX_ATTEMPTS بيقفل الإيميل LOCK_SECONDS ثانية."""
    init_attempts_table()
    now = time.time()
    conn = db.get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM login_attempts WHERE fails = 0 AND locked_until < ?", (now,))
            row = conn.execute("SELECT fails FROM login_attempts WHERE email = ?", (_akey(email),)).fetchone()
            fails = (row[0] if row else 0) + 1
            locked = 0.0
            if fails >= MAX_ATTEMPTS:
                fails, locked = 0, now + LOCK_SECONDS
            conn.execute(
                "INSERT INTO login_attempts (email, fails, locked_until) VALUES (?,?,?) "
                "ON CONFLICT(email) DO UPDATE SET fails = excluded.fails, locked_until = excluded.locked_until",
                (_akey(email), fails, locked))
    finally:
        conn.close()


def clear_failures(email):
    init_attempts_table()
    conn = db.get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM login_attempts WHERE email = ?", (_akey(email),))
    finally:
        conn.close()


def _cli_create_admin():
    print("إنشاء حساب أدمن")
    name = input("الاسم: ")
    email = input("البريد الإلكتروني: ")
    pw1 = getpass.getpass("كلمة المرور: ")
    pw2 = getpass.getpass("أعد كتابتها: ")
    if pw1 != pw2:
        print("كلمتا المرور غير متطابقتين.")
        return
    ok, msg = create_user(name, email, pw1, role="admin")
    print(msg)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-admin":
        _cli_create_admin()
    else:
        print("الاستخدام: python auth.py create-admin")