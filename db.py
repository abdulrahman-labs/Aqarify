import json
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "aqarify.db"
BACKUP_DIR = ROOT / "backups"


def get_conn():
    ensure_schema()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


_SCHEMA_READY = False

# شركات تجريبية (أسماء افتراضية) بتتوزع عليها الكمبوندات أول تشغيل؛ عدّلها من لوحة الأدمن
DEMO_COMPANIES = [
    ("الأفق للتطوير العقاري", "شركة تطوير متخصصة في المجتمعات السكنية المتكاملة."),
    ("النيل للتعمير", "مشروعات سكنية وتجارية بتشطيبات عالية الجودة."),
    ("واحة مصر للتنمية", "مجتمعات عمرانية خضراء بخدمات متكاملة."),
    ("سكاي لاين للاستثمار العقاري", "وحدات حديثة في أرقى المواقع."),
    ("المدائن العقارية", "تطوير وتسويق وحدات سكنية فاخرة."),
    ("الريادة للمقاولات والتطوير", "خبرة طويلة في البناء والتطوير العقاري."),
    ("بيت المستقبل", "حلول سكنية عصرية بأنظمة سداد مرنة."),
    ("جولدن جيت للتطوير", "مشروعات ساحلية وسكنية متميزة."),
]


def _table_exists(conn, table):
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None


def _has_col(conn, table, col):
    return any(r[1] == col for r in conn.execute(f"PRAGMA table_info({table})"))


def _seed_companies(conn):
    """لو مفيش وحدة مربوطة بشركة: نوزّع الكمبوندات على الشركات (كل كمبوند لشركة واحدة)."""
    if conn.execute("SELECT COUNT(*) FROM properties WHERE company_id IS NOT NULL").fetchone()[0]:
        return
    if not conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]:
        return
    if not conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]:
        conn.executemany("INSERT INTO companies (name, description) VALUES (?,?)", DEMO_COMPANIES)
    ids = [r[0] for r in conn.execute("SELECT id FROM companies ORDER BY id")]
    compounds = [r[0] for r in conn.execute("SELECT DISTINCT compound FROM properties ORDER BY compound")]
    for i, comp in enumerate(compounds):
        conn.execute("UPDATE properties SET company_id = ? WHERE compound IS ?", (ids[i % len(ids)], comp))


def ensure_schema():
    """ترقية تلقائية وآمنة (مرة لكل تشغيل): جدول الشركات + عمود company_id. مفيش حذف لأي داتا."""
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return
    _SCHEMA_READY = True
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
                logo_url    TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )""")
        for table in ("properties", "users", "tickets"):
            if _table_exists(conn, table) and not _has_col(conn, table, "company_id"):
                conn.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER REFERENCES companies(id)")
        if _table_exists(conn, "properties"):
            _seed_companies(conn)
        conn.commit()
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# الشركات (marketplace): كل وحدة تابعة لشركة، وكل شركة لها حساب (users.company_id)
# ═══════════════════════════════════════════════════════════════
def list_companies():
    conn = get_conn()
    try:
        try:
            rows = conn.execute(
                "SELECT c.id, c.name, c.logo_url, c.description, "
                "(SELECT COUNT(*) FROM properties p WHERE p.company_id = c.id) AS units, "
                "(SELECT COUNT(*) FROM users u WHERE u.company_id = c.id) AS accounts "
                "FROM companies c ORDER BY c.name").fetchall()
        except sqlite3.OperationalError:   # جدول users لسه ما اتعملش
            rows = conn.execute(
                "SELECT c.id, c.name, c.logo_url, c.description, "
                "(SELECT COUNT(*) FROM properties p WHERE p.company_id = c.id) AS units, 0 AS accounts "
                "FROM companies c ORDER BY c.name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_company(cid):
    conn = get_conn()
    try:
        row = conn.execute("SELECT id, name, logo_url, description FROM companies WHERE id = ?", (cid,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_company_accounts(company_id):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, name, email FROM users WHERE company_id = ? ORDER BY id", (company_id,))
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def create_company(name, logo_url="", description=""):
    """يرجّع رقم الشركة، أو None لو الاسم فاضي/مكرر."""
    name = (name or "").strip()
    if not name:
        return None
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute("INSERT INTO companies (name, logo_url, description) VALUES (?,?,?)",
                               (name, (logo_url or "").strip(), (description or "").strip()))
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_company(cid, name, logo_url="", description=""):
    name = (name or "").strip()
    if not name:
        return False
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute("UPDATE companies SET name = ?, logo_url = ?, description = ? WHERE id = ?",
                               (name, (logo_url or "").strip(), (description or "").strip(), cid))
            if cur.rowcount == 0:
                return False
            _bump_version(conn)   # اسم الشركة ظاهر في كاش الوحدات
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_company(cid):
    """يرجّع (نجح؟, رسالة). ما بيحذفش شركة عندها وحدات أو حسابات."""
    conn = get_conn()
    try:
        with conn:
            units = conn.execute("SELECT COUNT(*) FROM properties WHERE company_id = ?", (cid,)).fetchone()[0]
            try:
                accts = conn.execute("SELECT COUNT(*) FROM users WHERE company_id = ?", (cid,)).fetchone()[0]
            except sqlite3.OperationalError:
                accts = 0
            if units or accts:
                return False, f"لا يمكن حذف الشركة: عندها {units} وحدة و{accts} حساب. انقل الوحدات أو احذفها أولاً."
            try:   # التذاكر القديمة تفضل محفوظة بس من غير ربط بالشركة
                conn.execute("UPDATE tickets SET company_id = NULL WHERE company_id = ?", (cid,))
            except sqlite3.OperationalError:
                pass
            cur = conn.execute("DELETE FROM companies WHERE id = ?", (cid,))
            if cur.rowcount == 0:
                return False, "الشركة غير موجودة."
            _bump_version(conn)
        return True, ""
    finally:
        conn.close()


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

    comps = {}
    cids = sorted({p["company_id"] for p in props if p.get("company_id")})
    if cids:
        cmarks = ",".join("?" * len(cids))
        for r in conn.execute(f"SELECT id, name, logo_url FROM companies WHERE id IN ({cmarks})", cids):
            comps[r["id"]] = r

    for p in props:
        p["features"] = feats.get(p["id"], [])
        p["gallery"] = imgs.get(p["id"], [])
        c = comps.get(p.get("company_id"))
        p["company_name"] = c["name"] if c else None
        p["company_logo"] = c["logo_url"] if c else None
    return props


def search_properties(
    text=None, city=None, ptype=None, min_price=None, max_price=None,
    beds=None, status=None, sort="newest", limit=None, company_id=None,
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
    if company_id:
        where.append("company_id = ?");    params.append(company_id)

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


def to_legacy(p):
    """يحوّل صف الـ DB لشكل الواجهة (price نص منسّق، price_val رقم، desc)."""
    p = dict(p)
    p["price_val"] = int(p["price"])
    p["price"] = f"{p['price_val']:,}"
    p["desc"] = p.pop("description", "") or ""
    if isinstance(p.get("area"), float) and p["area"].is_integer():
        p["area"] = int(p["area"])
    return p


def list_properties_legacy(company_id=None):
    """كل الوحدات بشكل الواجهة، مرتبة بالرقم تصاعدياً."""
    items = [to_legacy(p) for p in search_properties(sort="newest", company_id=company_id)]
    return sorted(items, key=lambda p: p["id"])


def _bump_version(conn):
    """يزوّد رقم نسخة الوحدات (جوه نفس الـ Transaction بتاعة الكتابة)."""
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value INTEGER NOT NULL)")
    conn.execute("INSERT INTO meta (key, value) VALUES ('properties_version', 1) "
                 "ON CONFLICT(key) DO UPDATE SET value = value + 1")


def properties_version():
    """مفتاح للكاش: بيتغير لما الوحدات تتغير بس (مش مع كل رسالة شات)."""
    conn = get_conn()
    try:
        try:
            row = conn.execute("SELECT value FROM meta WHERE key = 'properties_version'").fetchone()
        except sqlite3.OperationalError:
            row = None
        n, top = conn.execute("SELECT COUNT(*), COALESCE(MAX(id), 0) FROM properties").fetchone()
        return (row[0] if row else 0, n, top)
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
        u.get("desc"), u.get("company_id"),
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
                    area, floor, finishing, status, delivery, main_image, description, company_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                _values(u),
            )
            pid = cur.lastrowid
            _save_children(conn, pid, u)
            _bump_version(conn)
        return pid
    finally:
        conn.close()


def update_property(pid, u, company_id=None):
    """يعدّل وحدة موجودة. يرجّع True لو الوحدة موجودة واتعدلت."""
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                """UPDATE properties SET
                   title=?, type=?, city=?, compound=?, location=?, price=?, beds=?,
                   baths=?, area=?, floor=?, finishing=?, status=?, delivery=?,
                   main_image=?, description=?, company_id=COALESCE(?, company_id)
                   WHERE id=?""" + (" AND company_id=?" if company_id else ""),
                _values(u) + (pid,) + ((company_id,) if company_id else ()),
            )
            if cur.rowcount == 0:
                return False
            _save_children(conn, pid, u)
            _bump_version(conn)
        return True
    finally:
        conn.close()


def delete_property(pid, company_id=None):
    """يحذف الوحدة ومميزاتها وصورها. يرجّع True لو اتحذفت.
    company_id: لو اتحدد، الحذف بيتم بس لو الوحدة تابعة للشركة دي."""
    conn = get_conn()
    try:
        with conn:
            if company_id and not conn.execute(
                    "SELECT 1 FROM properties WHERE id = ? AND company_id = ?", (pid, company_id)).fetchone():
                return False
            conn.execute("DELETE FROM property_features WHERE property_id = ?", (pid,))
            conn.execute("DELETE FROM property_images WHERE property_id = ?", (pid,))
            cur = conn.execute("DELETE FROM properties WHERE id = ?", (pid,))
            if cur.rowcount > 0:
                _bump_version(conn)
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
                company_id     INTEGER REFERENCES companies(id),
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
            company_id = None
            if property_id:
                row = conn.execute("SELECT company_id FROM properties WHERE id = ?", (property_id,)).fetchone()
                company_id = row[0] if row else None
            conn.execute(
                "INSERT INTO tickets (code, user_id, name, phone, topic, notes, property_id, property_title, company_id) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (code, user_id, name, phone, topic, notes or "", property_id, property_title, company_id))
        return code
    finally:
        conn.close()


def list_tickets(user_id=None, company_id=None):
    """كل التذاكر من الأقدم للأحدث (أو تذاكر مستخدم معيّن)."""
    conn = get_conn()
    try:
        where, params = [], []
        if user_id is not None:
            where.append("user_id = ?"); params.append(user_id)
        if company_id is not None:
            where.append("company_id = ?"); params.append(company_id)
        sql = "SELECT * FROM tickets" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY id ASC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_ticket_status(pk, status, company_id=None):
    if status not in TICKET_STATUSES:
        return False
    conn = get_conn()
    try:
        with conn:
            if company_id is None:
                cur = conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, pk))
            else:
                cur = conn.execute("UPDATE tickets SET status = ? WHERE id = ? AND company_id = ?",
                                   (status, pk, company_id))
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


# ═══════════════════════════════════════════════════════════════
# المفضلة (مربوطة بحساب المستخدم، وبتتشال تلقائياً لو الوحدة اتحذفت)
# ═══════════════════════════════════════════════════════════════
def init_favorites_table():
    conn = get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, property_id)
            )""")
        conn.commit()
    finally:
        conn.close()


def list_favorites(user_id):
    """أرقام الوحدات المفضلة للمستخدم (الأحدث أولاً)."""
    init_favorites_table()
    conn = get_conn()
    try:
        rows = conn.execute("SELECT property_id FROM favorites WHERE user_id = ? "
                            "ORDER BY created_at DESC, rowid DESC", (user_id,))
        return [r[0] for r in rows]
    finally:
        conn.close()


def toggle_favorite(user_id, property_id):
    """يضيف الوحدة للمفضلة أو يشيلها. يرجّع True لو بقت في المفضلة."""
    init_favorites_table()
    conn = get_conn()
    try:
        with conn:
            if conn.execute("DELETE FROM favorites WHERE user_id = ? AND property_id = ?",
                            (user_id, property_id)).rowcount:
                return False
            conn.execute("INSERT INTO favorites (user_id, property_id) VALUES (?,?)", (user_id, property_id))
            return True
    except sqlite3.IntegrityError:   # وحدة مش موجودة
        return False
    finally:
        conn.close()


def add_favorites(user_id, property_ids):
    """يضيف مجموعة وحدات للمفضلة (للموجود منها بس، ويتخطى المكرر)."""
    init_favorites_table()
    conn = get_conn()
    try:
        with conn:
            for pid in property_ids:
                conn.execute("INSERT OR IGNORE INTO favorites (user_id, property_id) "
                             "SELECT ?, id FROM properties WHERE id = ?", (user_id, int(pid)))
    finally:
        conn.close()