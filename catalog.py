"""
catalog.py: طبقة موحدة لقراءة الوحدات من قاعدة البيانات بالشكل اللي الصفحات متعودة عليه.
بدل ما كل صفحة تكرر نفس الدالة (_to_legacy / load_props).
"""
import streamlit as st

import db


def to_legacy(p):
    """يحوّل صف الـ DB لشكل الصفحات: price_val (رقم)، price (نص منسّق)، desc."""
    p = dict(p)
    p["price_val"] = int(p["price"])
    p["price"] = f"{p['price_val']:,}"
    p["desc"] = p.pop("description", "") or ""
    if isinstance(p.get("area"), float) and p["area"].is_integer():
        p["area"] = int(p["area"])
    return p


def _mtime():
    """وقت آخر تعديل لملف الـ DB: بيستخدم كمفتاح للكاش، فأي تعديل من الأدمن بيحدّث الكاش."""
    return db.DB_FILE.stat().st_mtime if db.DB_FILE.exists() else 0.0


@st.cache_data(show_spinner=False)
def _load_cached(mtime):
    items = [to_legacy(p) for p in db.search_properties(sort="newest")]
    return sorted(items, key=lambda p: p["id"])


def load_properties():
    """كل الوحدات مرتبة بالـ id تصاعدياً (من الكاش). قائمة فاضية لو الـ DB مش موجودة."""
    if not db.DB_FILE.exists():
        return []
    return _load_cached(_mtime())


def properties_by_id():
    return {p["id"]: p for p in load_properties()}