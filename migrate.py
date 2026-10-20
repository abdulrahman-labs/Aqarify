import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "aqarify.db"
JSON_FILE = ROOT / "data" / "properties.json"
BACKUP_DIR = ROOT / "backups"

SCHEMA = """
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS property_images;
DROP TABLE IF EXISTS property_features;
DROP TABLE IF EXISTS properties;

CREATE TABLE properties (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    type        TEXT NOT NULL,
    city        TEXT NOT NULL,
    compound    TEXT,
    location    TEXT,
    price       REAL NOT NULL,
    beds        INTEGER,
    baths       INTEGER,
    area        REAL,
    floor       INTEGER,
    finishing   TEXT,
    status      TEXT,
    delivery    TEXT,
    main_image  TEXT,
    description TEXT
);

CREATE TABLE property_features (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    feature     TEXT NOT NULL
);

CREATE TABLE property_images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_prop_price  ON properties(price);
CREATE INDEX idx_prop_city   ON properties(city);
CREATE INDEX idx_prop_type   ON properties(type);
CREATE INDEX idx_prop_beds   ON properties(beds);
CREATE INDEX idx_prop_status ON properties(status);
CREATE INDEX idx_feat_prop   ON property_features(property_id);
CREATE INDEX idx_img_prop    ON property_images(property_id);
"""


def backup_db():
    if DB_FILE.exists():
        BACKUP_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUP_DIR / f"aqarify_{stamp}.db"
        shutil.copy2(DB_FILE, dest)
        print(f"Backup saved: {dest.name}")


def main():
    data = json.load(open(JSON_FILE, encoding="utf-8"))
    backup_db()

    conn = sqlite3.connect(DB_FILE)
    conn.executescript(SCHEMA)

    for p in data:
        conn.execute(
            """INSERT INTO properties
               (id, title, type, city, compound, location, price, beds, baths,
                area, floor, finishing, status, delivery, main_image, description)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                p["id"], p["title"], p["type"], p.get("city", ""),
                p.get("compound"), p.get("location"), p["price_val"],
                p.get("beds"), p.get("baths"), p.get("area"), p.get("floor"),
                p.get("finishing"), p.get("status"), p.get("delivery"),
                p.get("main_image"), p.get("desc"),
            ),
        )
        for f in p.get("features", []):
            conn.execute(
                "INSERT INTO property_features (property_id, feature) VALUES (?,?)",
                (p["id"], f),
            )
        for i, url in enumerate(p.get("gallery", [])):
            conn.execute(
                "INSERT INTO property_images (property_id, url, position) VALUES (?,?,?)",
                (p["id"], url, i),
            )

    conn.commit()

    n_props = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    n_feat = conn.execute("SELECT COUNT(*) FROM property_features").fetchone()[0]
    n_img = conn.execute("SELECT COUNT(*) FROM property_images").fetchone()[0]
    print(f"Done: {n_props} properties, {n_feat} features, {n_img} images")
    conn.close()


if __name__ == "__main__":
    main()