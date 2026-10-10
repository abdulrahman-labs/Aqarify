import sqlite3

def get_db_connection():
    conn = sqlite3.connect('aqarify.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            beds INTEGER NOT NULL,
            baths INTEGER NOT NULL,
            area REAL NOT NULL,
            type TEXT NOT NULL,
            main_image TEXT NOT NULL,
            gallery_images TEXT,
            description TEXT,
            address_details TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM properties")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_properties = [
            (
                "شقة مودرن بكتاليا - القاهرة الجديدة",
                "القاهرة الجديدة - التجمع الخامس",
                4800000,
                3,
                2,
                165,
                "شقة",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1000&auto=format&fit=crop,https://images.unsplash.com/photo-1600585152220-90363fe7e115?q=80&w=1000&auto=format&fit=crop",
                "شقة سكنية فاخرة بتشطيب سوبر لوكس داخل كمبوند متكامل الخدمات، بالقرب من شارع التسعين الجنوبي.",
                "كمبوند القتالية، الحي الخامس، التجمع الخامس، القاهرة الجديدة"
            ),
            (
                "فيلا مستقلة بزد إيست - الشيخ زايد",
                "الشيخ زايد - أكتوبر",
                14500000,
                5,
                4,
                380,
                "فيلا",
                "https://images.unsplash.com/photo-1613977257363-707ba9348227?q=80&w=1000&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1613490493576-7fde63acd811?q=80&w=1000&auto=format&fit=crop,https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1000&auto=format&fit=crop",
                "فيلا مستقلة بحمام سباحة خاص وحديقة واسعة. تصميم مودرن بلمسات معمارية راقية.",
                "زد إيست، الثورة الخضراء، مدينة الشيخ زايد"
            )
        ]
        
        cursor.executemany('''
            INSERT INTO properties (title, location, price, beds, baths, area, type, main_image, gallery_images, description, address_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_properties)
        
    conn.commit()
    conn.close()

def get_all_properties():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM properties").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_property_by_id(prop_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM properties WHERE id = ?", (prop_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

if __name__ == "__main__":
    init_db()