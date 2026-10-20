import getpass
import re
import sqlite3
import sys

import bcrypt

import db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8


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
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
    finally:
        conn.close()


def _hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_user(name, email, password, role="user"):
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

    init_users_table()
    conn = db.get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            (name, email, _hash(password), role),
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
            "SELECT id, name, email, role, password_hash FROM users WHERE email = ?",
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
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}


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