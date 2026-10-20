import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "aqarify.db"
BACKUP_DIR = ROOT / "backups"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ═══════════════════════════════════════════════════════════════
# القراءة والبحث
# ═══════════════════════════════════════════════════════════════
def _attach_details(conn, props):
    """يضيف features و gallery لكل وحدة بـ استعلامين بس (مش استعلام لكل وحدة)."""
    if not props:
        return props
    ids = [p["id"] for p in props]
    marks = ",".join("?" * len(ids))

    feats, imgs = {}, {}
    for r in conn.execute(
        f"SELECT property_id, feature FROM property_features "
        f"WHERE property_id IN ({marks})", ids):
        feats.setdefault(r["property_id"], []).append(r["feature"])
    for r in conn.execute(
        f"SELECT property_id, url FROM property_images "
        f"WHERE property_id IN ({marks}) ORDER BY position", ids):
        imgs.setdefault(r["property_id"], []).append(r["url"])

    for p in props:
        p["features"] = feats.get(p["id"], [])
        p["gallery"] = imgs.get(p["id"], [])
    return props


def search_properties(
    text=None, city=None, ptype=None, min_price=None, max_price=None,
    beds=None, status=None, sort="newest", limit=None,
):
    """بحث وفلترة محلية بالكامل. كل الفلاتر اختيارية."""
    where, params = [], []

    if text:
        where.append("(title LIKE ? OR city LIKE ? OR compound LIKE ? "
                     "OR location LIKE ? OR CAST(id AS TEXT) = ?)")
        like = f"%{text}%"
        params += [like, like, like, like, text.strip()]
    if city:
        where.append("city = ?");          params.append(city)
    if ptype:
        where.append("type = ?");          params.append(ptype)
    if min_price is not None:
        where.append("price >= ?");        params.append(min_price)
    if max_price is not None:
        where.append("price <= ?");        params.append(max_price)
    if beds:
        where.append("beds >= ?");         params.append(beds)
    if status:
        where.append("status = ?");        params.append(status)

    # ORDER BY من قائمة ثابتة (مش من مدخل المستخدم) = آمن من SQL Injection
    order = {
        "newest": "id DESC",
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "area_desc": "area DESC",
    }.get(sort, "id DESC")

    sql = "SELECT * FROM properties"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY {order}"
    if limit:
        sql += " LIMIT ?"
        params.append(int(limit))

    conn = get_conn()
    try:
        props = [dict(r) for r in conn.execute(sql, params).fetchall()]
        return _attach_details(conn, props)
    finally:
        conn.close()


def get_property(prop_id):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM properties WHERE id = ?", (prop_id,)).fetchone()
        if not row:
            return None
        return _attach_details(conn, [dict(row)])[0]
    finally:
        conn.close()


def get_filter_options():
    """القيم المتاحة للقوائم المنسدلة (المدن، الأنواع، الحالات، نطاق السعر)."""
    conn = get_conn()
    try:
        def col(c):
            return [r[0] for r in conn.execute(
                f"SELECT DISTINCT {c} FROM properties "
                f"WHERE {c} IS NOT NULL ORDER BY {c}")]
        lo, hi = conn.execute(
            "SELECT MIN(price), MAX(price) FROM properties").fetchone()
        return {
            "cities": col("city"),
            "types": col("type"),
            "statuses": col("status"),
            "min_price": lo,
            "max_price": hi,
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# الكتابة (إضافة / تعديل / حذف) — لوحة الأدمن
#   الدوال دي بتستقبل وحدة بنفس شكل build_unit في Admin.py:
#   title, type, city, compound, location, price_val, beds, baths, area,
#   floor, finishing, status, delivery, main_image, desc, features[], gallery[]
# ═══════════════════════════════════════════════════════════════
def _values(u):
    return (
        u["title"], u["type"], u.get("city", ""), u.get("compound"), u.get("location"),
        float(u["price_val"]), u.get("beds"), u.get("baths"), u.get("area"), u.get("floor"),
        u.get("finishing"), u.get("status"), u.get("delivery"), u.get("main_image"),
        u.get("desc"),
    )


def _save_children(conn, pid, u):
    """يستبدل المميزات والصور بالقيم الجديدة (حذف القديم ثم إدخال الجديد)."""
    conn.execute("DELETE FROM property_features WHERE property_id = ?", (pid,))
    conn.execute("DELETE FROM property_images WHERE property_id = ?", (pid,))
    for feat in u.get("features", []):
        conn.execute(
            "INSERT INTO property_features (property_id, feature) VALUES (?,?)",
            (pid, feat))
    for i, url in enumerate(u.get("gallery", [])):
        conn.execute(
            "INSERT INTO property_images (property_id, url, position) VALUES (?,?,?)",
            (pid, url, i))


def next_property_id():
    conn = get_conn()
    try:
        return conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM properties").fetchone()[0]
    finally:
        conn.close()


def add_property(u):
    """يضيف وحدة جديدة ويرجّع رقمها. كله في Transaction واحدة (يا تنجح كلها يا تتلغي كلها)."""
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                """INSERT INTO properties
                   (title, type, city, compound, location, price, beds, baths,
                    area, floor, finishing, status, delivery, main_image, description)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                _values(u),
            )
            pid = cur.lastrowid
            _save_children(conn, pid, u)
        return pid
    finally:
        conn.close()


def update_property(pid, u):
    """يعدّل وحدة موجودة. يرجّع True لو الوحدة موجودة واتعدلت."""
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                """UPDATE properties SET
                   title=?, type=?, city=?, compound=?, location=?, price=?, beds=?,
                   baths=?, area=?, floor=?, finishing=?, status=?, delivery=?,
                   main_image=?, description=?
                   WHERE id=?""",
                _values(u) + (pid,),
            )
            if cur.rowcount == 0:
                return False
            _save_children(conn, pid, u)
        return True
    finally:
        conn.close()


def delete_property(pid):
    """يحذف الوحدة ومميزاتها وصورها. يرجّع True لو اتحذفت."""
    conn = get_conn()
    try:
        with conn:
            conn.execute("DELETE FROM property_features WHERE property_id = ?", (pid,))
            conn.execute("DELETE FROM property_images WHERE property_id = ?", (pid,))
            cur = conn.execute("DELETE FROM properties WHERE id = ?", (pid,))
        return cur.rowcount > 0
    finally:
        conn.close()


def backup_db():
    """نسخة احتياطية من aqarify.db في فولدر backups/ (بتتعمل قبل أي حذف)."""
    if not DB_FILE.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"aqarify_{stamp}.db"
    shutil.copy2(DB_FILE, dest)
    return dest
# ═══════════════════════════════════════════════════════════════
# سجل المحادثات (كل مستخدم يشوف محادثاته هو بس)
#   conversations: محادثة واحدة لكل صف، مربوطة بالمستخدم
#   messages:      رسايل المحادثة بالترتيب (مع أرقام الوحدات المرشحة)
# ═══════════════════════════════════════════════════════════════
import json


def init_chat_tables():
    conn = get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title          TEXT NOT NULL DEFAULT 'محادثة جديدة',
                active_prop_id INTEGER,
                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content         TEXT NOT NULL,
                prop_ids        TEXT NOT NULL DEFAULT '[]',
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id, updated_at);
            CREATE INDEX IF NOT EXISTS idx_msg_conv  ON messages(conversation_id, id);
        """)
        conn.commit()
    finally:
        conn.close()


def _clean_title(text):
    t = " ".join(str(text or "").split())
    if not t:
        return "محادثة جديدة"
    return t[:40] + "…" if len(t) > 40 else t


def _ids_from(raw):
    try:
        return [int(i) for i in json.loads(raw or "[]")]
    except Exception:
        return []


def create_conversation(user_id, title="", active_prop_id=None):
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO conversations (user_id, title, active_prop_id) VALUES (?,?,?)",
                (user_id, _clean_title(title), active_prop_id))
        return cur.lastrowid
    finally:
        conn.close()


def list_conversations(user_id, limit=50):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM conversations WHERE user_id = ? "
            "ORDER BY updated_at DESC, id DESC LIMIT ?", (user_id, int(limit))).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_conversation(conv_id, user_id):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, title, active_prop_id FROM conversations WHERE id = ? AND user_id = ?",
            (conv_id, user_id)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_messages(conv_id, user_id):
    """يرجّع رسايل المحادثة لو تابعة للمستخدم ده بس، وإلا قائمة فاضية."""
    conn = get_conn()
    try:
        owner = conn.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND user_id = ?",
            (conv_id, user_id)).fetchone()
        if not owner:
            return []
        rows = conn.execute(
            "SELECT role, content, prop_ids FROM messages "
            "WHERE conversation_id = ? ORDER BY id", (conv_id,)).fetchall()
        return [{"role": r["role"], "content": r["content"], "ids": _ids_from(r["prop_ids"])}
                for r in rows]
    finally:
        conn.close()


def add_message(conv_id, user_id, role, content, ids=None):
    """يضيف رسالة ويحدّث وقت المحادثة. يرجّع False لو المحادثة مش بتاعة المستخدم."""
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE conversations SET updated_at = datetime('now') "
                "WHERE id = ? AND user_id = ?", (conv_id, user_id))
            if cur.rowcount == 0:
                return False
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, prop_ids) VALUES (?,?,?,?)",
                (conv_id, role, content, json.dumps([int(i) for i in (ids or [])])))
        return True
    finally:
        conn.close()


def set_conversation_property(conv_id, user_id, prop_id):
    conn = get_conn()
    try:
        with conn:
            conn.execute(
                "UPDATE conversations SET active_prop_id = ? WHERE id = ? AND user_id = ?",
                (prop_id, conv_id, user_id))
    finally:
        conn.close()


def delete_conversation(conv_id, user_id):
    conn = get_conn()
    try:
        with conn:
            owner = conn.execute(
                "SELECT 1 FROM conversations WHERE id = ? AND user_id = ?",
                (conv_id, user_id)).fetchone()
            if not owner:
                return False
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
            conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        return True
    finally:
        conn.close()
        # ═══════════════════════════════════════════════════════════════
# التذاكر (حجز استشارة / معاينة)
#   user_id        : صاحب التذكرة لو كان مسجّل دخول (NULL للزائر)
#   property_id    : رقم الوحدة وقت الحجز (من غير FK عشان الوحدة ممكن تتحذف)
#   property_title : نسخة من عنوان الوحدة وقت الحجز (تحمي من تكرار الأرقام بعد الحذف)
# ═══════════════════════════════════════════════════════════════
import re

TICKET_STATUSES = ("جديدة", "قيد المتابعة", "مكتملة")


def init_tickets_table():
    conn = get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tickets (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                code           TEXT NOT NULL UNIQUE,
                user_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
                name           TEXT NOT NULL,
                phone          TEXT NOT NULL,
                topic          TEXT NOT NULL,
                notes          TEXT NOT NULL DEFAULT '',
                property_id    INTEGER,
                property_title TEXT,
                status         TEXT NOT NULL DEFAULT 'جديدة'
                               CHECK (status IN ('جديدة', 'قيد المتابعة', 'مكتملة')),
                created_at     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_tk_user   ON tickets(user_id);
            CREATE INDEX IF NOT EXISTS idx_tk_status ON tickets(status);
        """)
        conn.commit()
    finally:
        conn.close()


def _next_ticket_code(conn):
    top = 4800
    for (c,) in conn.execute("SELECT code FROM tickets"):
        m = re.search(r"(\d+)$", c or "")
        if m:
            top = max(top, int(m.group(1)))
    return f"TK-{top + 1}"


def create_ticket(user_id, name, phone, topic, notes="", property_id=None, property_title=None):
    """يحفظ تذكرة جديدة ويرجّع كودها (TK-4801 مثلاً)."""
    conn = get_conn()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")   # يمنع تكرار الكود لو اتنين حجزوا في نفس اللحظة
            code = _next_ticket_code(conn)
            conn.execute(
                "INSERT INTO tickets (code, user_id, name, phone, topic, notes, property_id, property_title) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (code, user_id, name, phone, topic, notes or "", property_id, property_title))
        return code
    finally:
        conn.close()


def list_tickets(user_id=None):
    """كل التذاكر من الأقدم للأحدث (أو تذاكر مستخدم معيّن)."""
    conn = get_conn()
    try:
        if user_id is None:
            rows = conn.execute("SELECT * FROM tickets ORDER BY id ASC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE user_id = ? ORDER BY id ASC", (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_ticket_status(pk, status):
    if status not in TICKET_STATUSES:
        return False
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, pk))
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_ticket(pk):
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute("DELETE FROM tickets WHERE id = ?", (pk,))
        return cur.rowcount > 0
    finally:
        conn.close()


def import_tickets_from_json(path):
    """ينقل تذاكر data/tickets.json القديمة للـ DB. آمن لو اتشغّل أكتر من مرة (بيتخطى المكرر).
    يرجّع (عدد المنقول، عدد المتخطّى)."""
    p = Path(path)
    if not p.exists():
        return 0, 0
    try:
        items = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0

    imported = skipped = 0
    conn = get_conn()
    try:
        with conn:
            for t in items:
                code = str(t.get("id") or "").strip()
                if not code or conn.execute(
                        "SELECT 1 FROM tickets WHERE code = ?", (code,)).fetchone():
                    skipped += 1
                    continue
                status = t.get("status") if t.get("status") in TICKET_STATUSES else "جديدة"
                conn.execute(
                    "INSERT INTO tickets (code, name, phone, topic, notes, property_id, status, created_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (code, t.get("name", ""), t.get("phone", ""), t.get("topic", ""),
                     t.get("notes", "") or "", t.get("property_id"), status,
                     t.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M")))
                imported += 1
        return imported, skipped
    finally:
        conn.close()