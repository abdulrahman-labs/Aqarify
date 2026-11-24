"""جدول مقارنة الوحدات (بيتعرض جوه نافذة منبثقة في معرض العقارات)."""
from utils import company_chip, esc

FIN_RANK = {"ألترا سوبر لوكس": 4, "سوبر لوكس": 3, "تشطيب كامل": 2, "نصف تشطيب": 1}


def money(v):
    return f"{int(round(v)):,}"


def floor_text(p):
    return "أرضي" if p.get("floor") in (None, 0) else f"الدور {p['floor']}"


def monthly(p):
    """قسط شهري تقديري: مقدم 10% والباقي على 8 سنوات بدون فوائد (نفس تقدير باقي الموقع)."""
    return p["price_val"] * 0.9 / 96


# (البند، قيمة المقارنة، النص المعروض، الأفضل: min/max/None)
ROWS = [
    ("السعر (ج.م)", lambda p: p["price_val"], lambda p: money(p["price_val"]), "min"),
    ("سعر المتر (ج.م)", lambda p: p["price_val"] / p["area"], lambda p: money(p["price_val"] / p["area"]), "min"),
    ("القسط الشهري التقديري", monthly, lambda p: money(monthly(p)) + " ج.م", "min"),
    ("المساحة (م²)", lambda p: p["area"], lambda p: str(p["area"]), "max"),
    ("غرف النوم", lambda p: p["beds"], lambda p: str(p["beds"]), "max"),
    ("الحمامات", lambda p: p["baths"], lambda p: str(p["baths"]), "max"),
    ("التشطيب", lambda p: FIN_RANK.get(p["finishing"], 0), lambda p: p["finishing"], "max"),
    ("الدور", None, floor_text, None),
    ("الحالة", None, lambda p: p["status"], None),
    ("موعد الاستلام", None, lambda p: p["delivery"], None),
    ("النوع", None, lambda p: p["type"], None),
    ("الشركة", None, lambda p: p.get("company_name") or "—", None),
]


def best_set(val, mode, items):
    """أرقام الأعمدة صاحبة أفضل قيمة (ولا شيء لو كل القيم متساوية)."""
    if not val or not mode:
        return set()
    vals = [val(p) for p in items]
    if len(set(vals)) == 1:
        return set()
    target = min(vals) if mode == "min" else max(vals)
    return {i for i, v in enumerate(vals) if v == target}


def build_table(items):
    head_cells = "".join(
        f'<th>{company_chip(p.get("company_name"))}'
        f'<div class="cmp-img" style="background-image:url({esc(p["main_image"])})"></div>'
        f'<div class="cmp-title">{esc(p["title"])}</div>'
        f'<div class="cmp-loc"><i class="fa-solid fa-location-dot"></i> {esc(p["location"])} · #{p["id"]}</div></th>'
        for p in items)
    body = ""
    for label, val, disp, mode in ROWS:
        best = best_set(val, mode, items)
        cells = "".join(f'<td class="{"best" if i in best else ""}">{esc(disp(p))}</td>' for i, p in enumerate(items))
        body += f"<tr><th>{label}</th>{cells}</tr>"
    feats = "".join(
        '<td>' + "".join(f'<span class="chip">{esc(f)}</span>' for f in p.get("features", [])) + '</td>' for p in items)
    body += f"<tr><th>المميزات</th>{feats}</tr>"
    return f'<div class="box cmp-wrap"><table class="cmp"><tr><th></th>{head_cells}</tr>{body}</table></div>'


CSS = """
<style>
    .cmp-wrap { overflow-x: auto; background: var(--color-white); border: 1px solid var(--color-border);
        border-radius: 18px; padding: 0; box-shadow: none; margin-bottom: 14px; }
    .cmp { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 14px; min-width: 520px; }
    .cmp th, .cmp td { padding: 13px 12px; border-bottom: 1px solid var(--color-border); vertical-align: top; text-align: center; }
    .cmp td { font-weight: 700; border-inline-start: 1px solid var(--color-border); unicode-bidi: isolate; }
    .cmp tr > th:first-child { width: 17%; text-align: right; background: #FBFAF6; color: var(--color-text-muted); font-size: 13px; font-weight: 700; }
    .cmp tr:first-child th { padding: 14px 12px; }
    .cmp td.best { background: rgba(201,162,75,.14); color: #6B4E0C; font-weight: 800; }
    .cmp td.best::after { content: "\\f005"; font-family: "Font Awesome 6 Free"; font-weight: 900;
        font-size: 11px; color: var(--color-accent); margin-inline-start: 6px; }
    .cmp td .chip { margin: 3px; }
    .cmp tr:last-child th, .cmp tr:last-child td { border-bottom: none; }
    .cmp-img { height: 120px; border-radius: 14px; background-size: cover; background-position: center; background-color: var(--color-border); margin: 6px 0 10px; }
    .cmp-title { font-size: 15px; font-weight: 800; line-height: 1.4; }
    .cmp-loc { font-size: 12px; color: var(--color-text-muted); font-weight: 600; margin-top: 4px; }
</style>
"""