import base64
import hashlib
import re
from functools import lru_cache
from html import escape


def esc(v):
    """يهرّب النص قبل ما يتحط جوه HTML (unsafe_allow_html)."""
    return escape(str(v if v is not None else ""), quote=True)


def safe(d):
    """نسخة من dict وحدة/تذكرة كل نصوصها مهرّبة (للعرض في HTML بس)."""
    out = {}
    for k, v in d.items():
        if isinstance(v, str):
            out[k] = esc(v)
        elif isinstance(v, list):
            out[k] = [esc(x) if isinstance(x, str) else x for x in v]
        else:
            out[k] = v
    return out


def company_tag(name, kind="bar"):
    """سطر اسم الشركة المالكة فوق صورة الوحدة (bar = كروت كاملة العرض، pill = صناديق)."""
    if not name:
        return ""
    return f'<div class="company-{kind}"><i class="fa-solid fa-building"></i> {esc(name)}</div>'


# ═══════════════════════════════════════════════════════════════
# شعارات الشركات: شعار الشركة الحقيقي (logo_url) لو متوفر، وإلا شعار SVG أصلي بيتولّد من اسمها.
# صفحة المعرض بتسجّل توزيع الشعارات على كل الشركات (set_branding) عشان ما يتكررش شعار بين شركتين.
# ═══════════════════════════════════════════════════════════════
BRAND_TONES = ["#14161C", "#1B2A41", "#1F3D36", "#3B2A2A", "#2E2A3F", "#3A3322", "#22303C", "#40262F"]
SKIP_WORDS = {"شركة", "شركه", "مجموعة", "مجموعه", "group", "company", "co", "co."}

# رموز الشعارات (شبكة 64×64) — الأولى تعبئة ذهبية خفيفة والتانية الخطوط. كل رمز بيعبّر عن معنى اسم الشركة.
EMBLEMS = {
    "skyline": ("M10 50V32h9v18zM23 50V16h10v34zM37 50V26h8v24zM49 50V36h6v14z",
                "M10 50V32h9v18M23 50V16h10v34M37 50V26h8v24M49 50V36h6v14M6 50h52M28 24h.01M28 32h.01M28 40h.01M14 39h.01"),
    "tower": ("M25 50V26l7-8 7 8v24z", "M32 8v10M25 50V26l7-8 7 8v24M18 50h28M29 32h6M29 39h6M29 46h6"),
    "horizon": ("M16 42a16 16 0 0 1 32 0z", "M16 42a16 16 0 0 1 32 0M32 14v6M14 24l4 4M50 24l-4 4M6 42h52M16 50h32M24 56h16"),
    "arches": ("M10 52V40a5 5 0 0 1 10 0v12zM44 52V40a5 5 0 0 1 10 0v12zM22 52V28a10 10 0 0 1 20 0v24z",
               "M6 52h52M10 52V40a5 5 0 0 1 10 0v12M44 52V40a5 5 0 0 1 10 0v12M22 52V28a10 10 0 0 1 20 0v24M32 12h.01"),
    "peak": ("M14 36L32 18l18 18z", "M14 36L32 18l18 18M14 48L32 30l18 18M32 8h.01"),
    "diamond": ("M32 10l18 22-18 22-18-22z", "M32 10l18 22-18 22-18-22zM14 32h36M24 20l8 12 8-12M24 44l8-12 8 12"),
    "waves": ("", "M8 22c6-7 10 7 16 0s10 7 16 0 10 7 16 0M8 34c6-7 10 7 16 0s10 7 16 0 10 7 16 0M8 46c6-7 10 7 16 0s10 7 16 0 10 7 16 0"),
    "leaf": ("M32 40C20 40 16 30 16 20c12 0 16 8 16 20zM32 34c9 0 14-7 14-16-9 0-14 7-14 16z",
             "M32 56V26M32 40C20 40 16 30 16 20c12 0 16 8 16 20zM32 34c9 0 14-7 14-16-9 0-14 7-14 16zM22 56h20"),
    "crown": ("M12 46V22l13 13 7-17 7 17 13-13v24z", "M12 46V22l13 13 7-17 7 17 13-13v24zM12 54h40M12 15h.01M32 11h.01M52 15h.01"),
    "house": ("M22 36V28l10-7 10 7v8z", "M32 8l22 13v22L32 56 10 43V21zM22 36V28l10-7 10 7v8zM28 44V36h8v8"),
    "key": ("M33 22a9 9 0 1 1-18 0 9 9 0 0 1 18 0z", "M33 22a9 9 0 1 1-18 0 9 9 0 0 1 18 0zM30 29l20 21M41 40l7-7M46 45l6-6M24 22h.01"),
    "star": ("M32 8l6 18 18 6-18 6-6 18-6-18-18-6 18-6z", "M32 8l6 18 18 6-18 6-6 18-6-18-18-6 18-6zM32 32h.01"),
    "columns": ("M10 26h44L32 12z", "M8 54h48M12 48h40M18 48V28M32 48V28M46 48V28M10 26h44L32 12z"),
    "bridge": ("", "M6 44h52M6 52h52M10 44C14 24 50 24 54 44M20 44V33M32 44V28M44 44V33"),
    "hexes": ("M32 11l9.5 5.5v11L32 33l-9.5-5.5v-11z",
              "M32 11l9.5 5.5v11L32 33l-9.5-5.5v-11zM20 34l9.5 5.5v11L20 56l-9.5-5.5v-11zM44 34l9.5 5.5v11L44 56l-9.5-5.5v-11z"),
    "shield": ("M32 10l18 6v14c0 12-8 20-18 24-10-4-18-12-18-24V16z", "M32 10l18 6v14c0 12-8 20-18 24-10-4-18-12-18-24V16zM24 32l6 6 11-12"),
}
EMBLEM_ORDER = list(EMBLEMS)
# كلمات مفتاحية في اسم الشركة → الرمز المناسب (الكلمة الأولى ليها الأولوية)
_EMBLEM_KEYS = [
    (("سكاي", "sky", "لاين", "line"), "skyline"),
    (("برج", "ابراج", "tower"), "tower"),
    (("افق", "horizon", "شروق", "شمس", "sun"), "horizon"),
    (("مدائن", "مداين", "مدين", "city", "قصر"), "arches"),
    (("ريادة", "رواد", "pioneer", "قمة", "summit"), "peak"),
    (("نخبة", "elite", "الماس", "ماس", "diamond"), "diamond"),
    (("نيل", "ساحل", "بحر", "مارينا", "marina", "bay", "خليج", "لاجون", "lagoon"), "waves"),
    (("جاردن", "garden", "حدائق", "حديقة", "خضر", "green", "نخيل", "palm", "واحة"), "leaf"),
    (("ملكي", "ملك", "royal", "تاج", "crown"), "crown"),
    (("بيت", "بيوت", "منزل", "home", "house", "دار", "سكن", "مسكن"), "house"),
    (("مفتاح", "مفاتيح", "key"), "key"),
    (("نجوم", "نجمة", "star", "بوصلة", "compass"), "star"),
    (("اعمدة", "عمود", "كلاسيك", "classic", "pillar"), "columns"),
    (("جسر", "جسور", "bridge"), "bridge"),
    (("مجتمع", "مجتمعات", "كمبوند", "compound", "community"), "hexes"),
    (("امان", "حصن", "درع", "shield", "fort"), "shield"),
]


def _norm_ar(text):
    t = str(text).lower()
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        t = t.replace(a, b)
    return t


_EMBLEM_LOOKUP = [(tuple(_norm_ar(k) for k in keys), shape) for keys, shape in _EMBLEM_KEYS]
_SKIP_NORM = {_norm_ar(w) for w in SKIP_WORDS}


def _md5_int(text):
    return int(hashlib.md5(str(text).encode("utf-8")).hexdigest(), 16)


def company_emblem(name):
    """الرمز المناسب لمعنى الاسم (لو فيه كلمة دالة)، وإلا None."""
    words = [w for w in _norm_ar(name).replace("-", " ").split() if w not in _SKIP_NORM]
    words = [w[2:] if w.startswith("ال") and len(w) > 3 else w for w in words]
    for w in words:
        for keys, shape in _EMBLEM_LOOKUP:
            if any(w.startswith(k) for k in keys):
                return shape
    return None


@lru_cache(maxsize=8)
def build_logo_registry(companies):
    """companies = tuple من (id, name). بيرجّع {name: (emblem, tone)} من غير تكرار: الرمز مش بيتكرر
    طول ما فيه رموز فاضية، وبعدها التركيبة (رمز + لون) بتفضل مختلفة. الشركات الأقدم (id أصغر) بتحافظ
    على شعارها لما تتضاف شركات جديدة."""
    used_emblems, used_pairs, registry = set(), set(), {}
    ordered = sorted(companies, key=lambda c: (company_emblem(c[1]) is None, c[0], str(c[1])))
    n_e, n_t = len(EMBLEM_ORDER), len(BRAND_TONES)
    for _, name in ordered:
        if name in registry:
            continue
        pref = company_emblem(name)
        start = EMBLEM_ORDER.index(pref) if pref else _md5_int(name) % n_e
        cands = [EMBLEM_ORDER[(start + i) % n_e] for i in range(n_e)]
        emblem = next((e for e in cands if e not in used_emblems), cands[0])
        t0 = _md5_int("tone:" + str(name)) % n_t
        tones = [BRAND_TONES[(t0 + i) % n_t] for i in range(n_t)]
        tone = next((t for t in tones if (emblem, t) not in used_pairs), tones[0])
        used_emblems.add(emblem)
        used_pairs.add((emblem, tone))
        registry[name] = (emblem, tone)
    return registry


def _shade(hexcolor, f):
    """تفتيح (f>0) أو تغميق (f<0) للون."""
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    t = 255 if f > 0 else 0
    return "#{:02X}{:02X}{:02X}".format(*(round(c + (t - c) * abs(f)) for c in (r, g, b)))


@lru_cache(maxsize=256)
def company_logo_src(emblem, tone):
    """شعار SVG عالي الدقة (vector): خلفية متدرجة + حلقتين رفيعتين + رمز ذهبي بتدرّج وتعبئة خفيفة."""
    fill, line = EMBLEMS[emblem]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><defs>'
        f'<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{_shade(tone, .22)}"/>'
        f'<stop offset="1" stop-color="{_shade(tone, -.28)}"/></linearGradient>'
        '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4DD92"/>'
        '<stop offset="1" stop-color="#C9A24B"/></linearGradient></defs>'
        '<rect width="128" height="128" rx="36" fill="url(#b)"/>'
        '<rect x="3" y="3" width="122" height="122" rx="33" fill="none" stroke="#C9A24B" stroke-opacity=".6" stroke-width="2"/>'
        '<rect x="10" y="10" width="108" height="108" rx="27" fill="none" stroke="#E6C878" stroke-opacity=".16" stroke-width="1.5"/>'
        '<g transform="translate(16 16) scale(1.5)">'
        + (f'<path d="{fill}" fill="#E6C878" fill-opacity=".17"/>' if fill else "")
        + f'<path d="{line}" fill="none" stroke="url(#g)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '</g></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


_BRANDING = {"registry": {}, "logos": {}}


def set_branding(registry, logos_by_name=None):
    """بتسجّلها صفحة المعرض: توزيع الشعارات المولّدة + شعارات logo_url الحقيقية (بالاسم)."""
    _BRANDING["registry"] = registry or {}
    _BRANDING["logos"] = logos_by_name or {}


def company_logo_html(name, logo=None):
    """مربع شعار الشركة (class=prop-company-ico). الشعار الحقيقي لو متوفر، وإلا المولّد."""
    if not name:
        return ""
    logo = logo or _BRANDING["logos"].get(name)
    if logo and str(logo).startswith(("http://", "https://", "data:image/", "/")):
        return f'<div class="prop-company-ico has-logo"><img src="{esc(logo)}" alt=""></div>'
    emblem, _ = _BRANDING["registry"].get(name) or (
        company_emblem(name) or EMBLEM_ORDER[_md5_int(name) % len(EMBLEM_ORDER)], None)
    fill, line = EMBLEMS[emblem]
    return ('<div class="prop-company-ico soft"><svg viewBox="4 4 56 56" fill="none">'
            + (f'<path d="{fill}" fill="rgba(201,162,75,.2)"/>' if fill else "")
            + f'<path d="{line}" stroke="#A8832F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')


def company_chip(name):
    """شريحة الشركة (شعار + اسم) لنافذة التفاصيل وجدول المقارنة."""
    if not name:
        return ""
    return f'<div class="company-chip">{company_logo_html(name)}<span>{esc(name)}</span></div>'

# ═══════════════════════════════════════════════════════════════
# دوال وثوابت مشتركة (كانت متكررة في Properties / Calculator / Admin / Company / Customer Service)
# استوردها من هنا بدل ما تعيد كتابتها في كل صفحة:
#   from utils import money, floor_text, status_cls, feat_icon, norm, monthly_estimate
# ═══════════════════════════════════════════════════════════════
BASE_TYPES = ["شقة", "فيلا", "دوبلكس", "تاون هاوس", "بنتهاوس", "شاليه", "استوديو"]
STATUSES = ["جاهز للتسليم", "تحت الإنشاء"]
FINISHES = ["ألترا سوبر لوكس", "سوبر لوكس", "تشطيب كامل", "نصف تشطيب"]
FIN_RANK = {f: len(FINISHES) - i for i, f in enumerate(FINISHES)}   # ألترا = 4 ... نصف تشطيب = 1
DEFAULT_IMG = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"

DOWN_PCT, YEARS = 10, 8   # تقدير الموقع الموحد: مقدم 10% والباقي على 8 سنوات بدون فوائد


def money(v):
    """رقم منسّق بفواصل: 3350000 -> 3,350,000"""
    return f"{int(round(v or 0)):,}"


def floor_text(p):
    return "أرضي" if p.get("floor") in (None, 0) else f"الدور {p['floor']}"


def price_per_meter(p):
    return p["price_val"] / p["area"] if p.get("area") else 0


def monthly_estimate(price, down_pct=DOWN_PCT, years=YEARS):
    """(المقدم، القسط الشهري) التقديري بدون فوائد."""
    down = price * down_pct / 100
    return down, (price - down) / (years * 12)


def status_cls(s):
    """كلاس CSS لحالة الوحدة (st-build / st-ready / st-other)."""
    s = str(s or "")
    if any(k in s for k in ("إنشاء", "انشاء", "قيد")):
        return "st-build"
    if any(k in s for k in ("جاهز", "فوري", "تسليم")):
        return "st-ready"
    return "st-other"


_FEAT_ICONS = [
    (("مسبح", "حمام سباحة", "بول"), "fa-water-ladder"),
    (("جراج", "موقف", "ركن"), "fa-car"),
    (("أمن", "امن", "حراسة", "كاميرات"), "fa-shield-halved"),
    (("جيم", "رياض", "نادي"), "fa-dumbbell"),
    (("مصعد", "أسانسير", "اسانسير"), "fa-elevator"),
    (("حديقة", "جاردن", "خضراء"), "fa-tree"),
    (("تكييف",), "fa-snowflake"),
    (("إنترنت", "انترنت", "واي"), "fa-wifi"),
    (("بلكونة", "شرفة", "تراس", "روف"), "fa-umbrella-beach"),
    (("مطبخ",), "fa-kitchen-set"),
    (("إطلالة", "اطلالة", "بحر", "نيل"), "fa-binoculars"),
    (("مدرسة", "مدارس"), "fa-school"),
    (("مول", "تجاري", "سوق"), "fa-bag-shopping"),
]


def feat_icon(text):
    for keys, icon in _FEAT_ICONS:
        if any(k in text for k in keys):
            return icon
    return "fa-circle-check"


AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_NORM_PAIRS = (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي"))
_DIACRITICS = re.compile(r"[\u064B-\u0652]")


def norm(text):
    """توحيد النص العربي للبحث: أرقام هندية -> عربية، همزات، تاء مربوطة، تشكيل."""
    t = str(text or "").translate(AR_DIGITS).lower()
    for a, b in _NORM_PAIRS:
        t = t.replace(a, b)
    return _DIACRITICS.sub("", t)


PHONE_RE = re.compile(r"(?:20)?0?1[0125]\d{8}")


def clean_phone(phone):
    """ينضّف رقم الموبايل (مسافات/شرطات/+ وأرقام هندية) ويرجّع None لو مش رقم مصري صحيح."""
    p = re.sub(r"[\s\-+]", "", norm(phone))
    return p if PHONE_RE.fullmatch(p) else None