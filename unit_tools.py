"""منطق نموذج الوحدة المشترك لصفحات الشركات (إضافة/تعديل وحدة)."""
import re

import streamlit as st

STATUSES = ["جاهز للتسليم", "تحت الإنشاء"]
FINISHES = ["ألترا سوبر لوكس", "سوبر لوكس", "تشطيب كامل", "نصف تشطيب"]
BASE_TYPES = ["شقة", "فيلا", "دوبلكس", "تاون هاوس", "بنتهاوس", "شاليه", "استوديو"]
DEFAULT_IMG = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"


def build_unit(f):
    price = int(f["price"])
    city = f["city_new"].strip() or f["city"]
    compound = f["compound"].strip()
    feats = list(f["features"]) + [x.strip() for x in re.split(r"[،,]", f["feat_extra"]) if x.strip()]
    title = f["title"].strip() or f"{f['type']} للبيع في {compound}"
    area, beds, baths = int(f["area"]), int(f["beds"]), int(f["baths"])
    desc = f["desc"].strip() or (f"{f['type']} بمساحة {area} م² و{beds} غرفة نوم و{baths} حمام داخل {compound} في {city}.")
    gallery = [g.strip() for g in (f["g1"], f["g2"]) if g.strip()]
    return {
        "title": title, "type": f["type"], "city": city, "compound": compound,
        "location": f"{city} - {compound}", "price_val": price, "price": f"{price:,}",
        "beds": beds, "baths": baths, "area": area,
        "floor": None if int(f["floor"]) == 0 else int(f["floor"]),
        "finishing": f["finishing"], "status": f["status"], "delivery": f["delivery"].strip() or "فوري",
        "features": feats, "main_image": f["main_image"].strip() or DEFAULT_IMG,
        "gallery": gallery or [DEFAULT_IMG, DEFAULT_IMG], "desc": desc,
        "company_id": f.get("company_id"),
    }


def validate(f):
    if not f["compound"].strip():
        return "اكتب اسم الكمبوند أو المشروع."
    if int(f["price"]) <= 0 or int(f["area"]) <= 0:
        return "السعر والمساحة يجب أن يكونا أكبر من صفر."
    return None


def unit_form(form_key, u, types, cities, feature_opts):
    """نموذج الوحدة. يرجّع dict لو اتضغط حفظ، وإلا None."""
    d = u or {}
    with st.form(form_key, clear_on_submit=u is None):
        a, b = st.columns(2)
        with a:
            utype = st.selectbox("نوع الوحدة", types, index=types.index(d["type"]) if d.get("type") in types else 0)
            city = st.selectbox("المنطقة", cities, index=cities.index(d["city"]) if d.get("city") in cities else 0)
            city_new = st.text_input("منطقة جديدة (اختياري، تتجاوز الاختيار أعلاه)")
            compound = st.text_input("الكمبوند أو المشروع", value=d.get("compound", ""))
            title = st.text_input("عنوان الإعلان (اختياري، يُولَّد تلقائياً)", value=d.get("title", ""))
            price = st.number_input("السعر (ج.م)", 100_000, 200_000_000, int(d.get("price_val", 3_000_000)), 50_000)
            area = st.number_input("المساحة (م²)", 20, 5000, int(d.get("area", 150)), 5)
        with b:
            beds = st.number_input("غرف النوم", 1, 15, int(d.get("beds", 3)))
            baths = st.number_input("الحمامات", 1, 15, int(d.get("baths", 2)))
            floor = st.number_input("الدور (0 = أرضي)", 0, 60, int(d.get("floor") or 0))
            finishing = st.selectbox("التشطيب", FINISHES, index=FINISHES.index(d["finishing"]) if d.get("finishing") in FINISHES else 0)
            status = st.selectbox("الحالة", STATUSES, index=STATUSES.index(d["status"]) if d.get("status") in STATUSES else 0)
            delivery = st.text_input("موعد الاستلام", value=d.get("delivery", "فوري"))
            features = st.multiselect("المميزات", feature_opts, default=[x for x in d.get("features", []) if x in feature_opts])
            feat_extra = st.text_input("مميزات إضافية (افصل بفاصلة)")
        main_image = st.text_input("رابط الصورة الرئيسية", value=d.get("main_image", ""))
        g = d.get("gallery", ["", ""]) + ["", ""]
        g1 = st.text_input("رابط صورة داخلية 1", value=g[0])
        g2 = st.text_input("رابط صورة داخلية 2", value=g[1])
        desc = st.text_area("الوصف (اختياري، يُولَّد تلقائياً)", value=d.get("desc", ""))
        sub = st.form_submit_button("حفظ التعديلات" if u else "إضافة الوحدة", icon=":material/save:",
                                    type="primary", width="stretch")
    if sub:
        return {"type": utype, "city": city, "city_new": city_new, "compound": compound, "title": title,
                "price": price, "area": area, "beds": beds, "baths": baths, "floor": floor,
                "finishing": finishing, "status": status, "delivery": delivery, "features": features,
                "feat_extra": feat_extra, "main_image": main_image, "g1": g1, "g2": g2, "desc": desc}
    return None
