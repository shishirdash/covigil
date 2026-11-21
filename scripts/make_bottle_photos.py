"""Render invented pill-bottle "photos" for the patient screen demo.

Usage:  python scripts/make_bottle_photos.py [data/bottles]

ALL CONTENT IS SYNTHETIC. No real patient, clinician, pharmacy or product is
described. Rx labels copy each drug's MOST RECENT row in data/pharmacy_fills.csv
(pharmacy, prescriber, strength, directions, quantity, fill date). Rx numbers,
addresses, phone numbers and refill counts are invented. The labels say only
what a real label would say; they carry no review conclusions.
No apixaban bottle: the intake form says there is none.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import csv, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "bottles")
os.makedirs(out, exist_ok=True)

W = H = 900
SYN = "SYNTHETIC – DEMO ONLY"
PATIENT = "HECTOR M REYES"

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(size, bold=False, cond=False):
    name = "DejaVuSans" + ("Condensed" if cond else "") + ("-Bold" if bold else "") + ".ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default(size)

# Invented pharmacy details, keyed by the pharmacy string in the fill history.
PHARMACIES = {
    "Corner Rx #12 (Maple Hollow OH)": ("CORNER RX #12", "215 Main St, Maple Hollow, OH", "(555) 010-0161"),
    "Corner Rx #88 (New York NY)":     ("CORNER RX #88", "1040 Fulton Ave, New York, NY", "(555) 010-0188"),
}
# Invented Rx numbers and refill counts (labels only; not in any other source).
RX = {
    "metformin":    ("SYN-6041127", 2),
    "losartan":     ("SYN-6043390", 1),
    "lisinopril":   ("SYN-6041128", 2),
    "furosemide":   ("SYN-6043391", 1),
    "tamsulosin":   ("SYN-6044512", 4),
    "atorvastatin": ("SYN-5098214", 1),
}
FORM = {"tab": "TABLETS", "cap": "CAPSULES"}

def latest_fills():
    with open(os.path.join(ROOT, "data", "pharmacy_fills.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    last = {}
    for r in rows:
        if r["drug"] not in last or r["fill_date"] > last[r["drug"]]["fill_date"]:
            last[r["drug"]] = r
    return last

def us_date(iso):
    y, m, d = iso.split("-")
    return f"{m}/{d}/{y}"

def prescriber(p):          # "Whitcombe A" -> "DR. A. WHITCOMBE"
    last, first = p.rsplit(" ", 1)
    return f"DR. {first}. {last.upper()}"

def directions(sig):        # "1 tab twice daily" -> "TAKE 1 TABLET BY MOUTH TWICE DAILY"
    words = sig.split(" ", 2)
    unit = {"tab": "TABLET", "cap": "CAPSULE"}[words[1]]
    return f"TAKE {words[0]} {unit} BY MOUTH {words[2].upper()}"

# ---------- drawing helpers ----------

def background(seed, warm):
    """Table top: soft wood-like gradient with grain and a little noise."""
    rnd = random.Random(seed)
    base = (196, 170, 138) if warm else (186, 186, 180)
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1.0 - 0.18 * (y / H) + 0.04 * ((y // 7) % 2)
        c = tuple(int(v * k) for v in base)
        d.line([(0, y), (W, y)], fill=c)
    for _ in range(60):                       # grain
        y = rnd.randint(0, H)
        c = tuple(int(v * rnd.uniform(0.85, 1.05)) for v in base)
        d.line([(0, y), (W, y + rnd.randint(-30, 30))], fill=c, width=rnd.randint(1, 3))
    img = img.filter(ImageFilter.GaussianBlur(2))
    noise = Image.effect_noise((W, H), 18).convert("RGB")
    return Image.blend(img, noise, 0.06)

def shadow(img, box, radius=40, offset=(26, 22), strength=110):
    sh = Image.new("L", (W, H), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle(
        (x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]), radius, fill=strength)
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (W, H), (30, 22, 15))
    img.paste(dark, (0, 0), sh)

def cylinder_shade(img, box, base, mask_radius=36, highlight=True):
    """Fill box with a horizontally shaded colour so it reads as a cylinder."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    layer = Image.new("RGB", (w, y1 - y0), base)
    d = ImageDraw.Draw(layer)
    for x in range(w):
        t = x / (w - 1)
        k = 0.62 + 0.55 * (1 - abs(t - 0.38) * 1.9) if highlight else 1.0
        k = max(0.55, min(1.18, k))
        c = tuple(min(255, int(v * k)) for v in base)
        d.line([(x, 0), (x, y1 - y0)], fill=c)
    m = Image.new("L", layer.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, y1 - y0 - 1), mask_radius, fill=255)
    img.paste(layer, (x0, y0), m)

def edge_shade(img, box, strength=70, width=40):
    """Darken the left/right edges of a flat label so it looks wrapped."""
    x0, y0, x1, y1 = box
    ov = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ov)
    for i in range(width):
        a = int(strength * (1 - i / width) ** 2)
        d.line([(x0 + i, y0), (x0 + i, y1)], fill=a)
        d.line([(x1 - i, y0), (x1 - i, y1)], fill=a)
    img.paste(Image.new("RGB", (W, H), (40, 30, 20)), (0, 0), ov)

def text_lines(d, x, y, lines, maxw):
    """lines: list of (text, font, colour, gap_after). Shrinks a line if too wide."""
    for text, f, col, gap in lines:
        size = f.size
        while d.textlength(text, font=f) > maxw and size > 14:
            size -= 1
            f = ImageFont.truetype(f.path, size)
        d.text((x, y), text, font=f, fill=col)
        y += f.size + gap
    return y

def finish(img, seed):
    """Slight camera feel: tiny rotation, vignette, soft blur, noise."""
    rnd = random.Random(seed)
    img = img.rotate(rnd.uniform(-2.2, 2.2), resample=Image.BICUBIC, fillcolor=img.getpixel((5, 5)))
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-180, -180, W + 180, H + 180), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(img, Image.new("RGB", (W, H), (25, 20, 15)), vig)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    noise = Image.effect_noise((W, H), 30).convert("RGB")
    return Image.blend(img, noise, 0.035)

# ---------- Rx bottle ----------

def rx_bottle(drug, row, path, seed):
    img = background(seed, warm=True)
    bx0, bx1 = 150, 750                       # bottle body
    cap = (130, 70, 770, 190)
    body = (bx0, 165, bx1, 850)
    shadow(img, (cap[0], cap[1], body[2], body[3]))
    cylinder_shade(img, body, (170, 88, 22), mask_radius=48)          # amber
    cylinder_shade(img, cap, (238, 238, 232), mask_radius=22)         # white cap
    d = ImageDraw.Draw(img)
    for x in range(cap[0] + 14, cap[2] - 10, 16):                     # cap ridges
        d.line([(x, cap[1] + 8), (x, cap[3] - 8)], fill=(205, 205, 198), width=3)
    d.rectangle((bx0 + 4, 190, bx1 - 4, 214), fill=(140, 70, 16))     # neck lip

    lab = (172, 240, 728, 820)                                       # white label
    d.rectangle(lab, fill=(250, 250, 246))
    name, addr, phone = PHARMACIES[row["pharmacy"]]
    rxno, refills = RX[drug]
    unit = row["directions"].split(" ")[1]
    x, maxw = lab[0] + 24, lab[2] - lab[0] - 48

    d.rectangle((lab[0], lab[1], lab[2], lab[1] + 74), fill=(28, 74, 128))   # header band
    d.text((x, lab[1] + 8), name, font=font(34, bold=True), fill="white")
    d.text((x, lab[1] + 46), f"{addr}  {phone}", font=font(19, cond=True), fill=(225, 232, 245))

    y = lab[1] + 88
    d.text((x, y), f"RX# {rxno}", font=font(26, bold=True), fill=(20, 20, 20))
    y += 40
    y = text_lines(d, x, y, [
        (PATIENT, font(40, bold=True), (10, 10, 10), 10),
        (directions(row["directions"]), font(29, bold=True), (10, 10, 10), 12),
        (f"{drug.upper()} {row['strength'].upper()} {FORM[unit]}", font(33, bold=True), (10, 10, 10), 10),
        (f"QTY: {row['quantity']}    REFILLS: {refills}", font(26), (25, 25, 25), 6),
        (f"DATE FILLED: {us_date(row['fill_date'])}", font(26, bold=True), (20, 20, 20), 6),
        (f"PRESCRIBER: {prescriber(row['prescriber'])}", font(26), (25, 25, 25), 14),
    ], maxw)
    d.line([(x, y), (lab[2] - 24, y)], fill=(160, 160, 160), width=2)
    y += 12
    if drug == "metformin":                   # standard auxiliary text for this drug
        d.text((x, y), "TAKE WITH FOOD", font=font(22, bold=True), fill=(25, 25, 25))
        y += 32
    # synthetic stamp
    sy = lab[3] - 62
    d.rectangle((lab[0] + 14, sy, lab[2] - 14, sy + 48), fill=(255, 236, 120), outline=(180, 30, 30), width=3)
    f = font(30, bold=True)
    tw = d.textlength(SYN, font=f)
    d.text(((lab[0] + lab[2] - tw) / 2, sy + 6), SYN, font=f, fill=(170, 20, 20))
    # fake barcode
    rnd = random.Random(seed)
    bxs = lab[2] - 150
    by = y
    if by + 50 < sy - 6:
        bx = bxs
        while bx < lab[2] - 26:
            wbar = rnd.choice((2, 2, 3, 5))
            d.rectangle((bx, by, bx + wbar - 1, by + 44), fill=(20, 20, 20))
            bx += wbar + rnd.choice((2, 3))
    edge_shade(img, lab)
    finish(img, seed).save(path)

# ---------- OTC products ----------

def otc_box(path, seed):
    """Generic store-brand naproxen sodium box. No real brand or trade dress."""
    img = background(seed, warm=False)
    box = (170, 130, 730, 800)
    shadow(img, box, radius=8)
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=(246, 246, 240))
    d.rectangle((box[0], box[1], box[2], box[1] + 120), fill=(70, 70, 78))
    x, maxw = box[0] + 34, box[2] - box[0] - 68
    d.text((x, box[1] + 18), "STORE BRAND", font=font(26, bold=True), fill=(235, 235, 235))
    d.text((x, box[1] + 58), "Compare to the leading brand", font=font(22), fill=(210, 210, 210))
    y = text_lines(d, x, box[1] + 150, [
        ("Naproxen sodium", font(52, bold=True), (20, 20, 20), 6),
        ("tablets, 220 mg", font(44, bold=True), (20, 20, 20), 18),
        ("Pain reliever / fever reducer (NSAID)", font(28), (40, 40, 40), 30),
    ], maxw)
    d.rounded_rectangle((x, y, x + 300, y + 70), 12, fill=(70, 70, 78))
    d.text((x + 20, y + 13), "100 TABLETS", font=font(36, bold=True), fill="white")
    y += 100
    y = text_lines(d, x, y, [
        ("Read and follow Drug Facts on back of box", font(24), (40, 40, 40), 8),
        ("LOT SYN-N4471    EXP 08/2028", font(24), (40, 40, 40), 8),
    ], maxw)
    sy = box[3] - 80
    d.rectangle((box[0] + 20, sy, box[2] - 20, sy + 54), fill=(255, 236, 120), outline=(180, 30, 30), width=3)
    f = font(32, bold=True)
    d.text(((box[0] + box[2] - d.textlength(SYN, font=f)) / 2, sy + 8), SYN, font=f, fill=(170, 20, 20))
    # box side face for depth
    side = [(box[2], box[1]), (box[2] + 40, box[1] + 26), (box[2] + 40, box[3] - 14), (box[2], box[3])]
    d.polygon(side, fill=(200, 200, 194))
    finish(img, seed).save(path)

def otc_vitamin(path, seed):
    img = background(seed, warm=True)
    cap = (210, 90, 690, 200)
    body = (180, 180, 720, 850)
    shadow(img, (cap[0], cap[1], body[2], body[3]))
    cylinder_shade(img, body, (232, 232, 226), mask_radius=60)        # white plastic
    cylinder_shade(img, cap, (225, 160, 40), mask_radius=20)          # yellow cap
    d = ImageDraw.Draw(img)
    lab = (196, 270, 704, 800)
    d.rectangle(lab, fill=(255, 250, 235))
    d.rectangle((lab[0], lab[1], lab[2], lab[1] + 60), fill=(240, 175, 40))
    x, maxw = lab[0] + 28, lab[2] - lab[0] - 56
    d.text((x, lab[1] + 12), "STORE BRAND", font=font(28, bold=True), fill=(60, 35, 0))
    y = text_lines(d, x, lab[1] + 84, [
        ("Vitamin D3", font(60, bold=True), (30, 30, 30), 8),
        ("1000 IU (25 mcg)", font(42, bold=True), (30, 30, 30), 14),
        ("Dietary supplement", font(30), (50, 50, 50), 8),
        ("100 softgels", font(30), (50, 50, 50), 18),
        ("Suggested use: 1 softgel daily", font(26), (50, 50, 50), 8),
        ("with a meal", font(26), (50, 50, 50), 8),
        ("LOT SYN-D2209    EXP 03/2028", font(22), (60, 60, 60), 8),
    ], maxw)
    sy = lab[3] - 66
    d.rectangle((lab[0] + 14, sy, lab[2] - 14, sy + 50), fill=(255, 236, 120), outline=(180, 30, 30), width=3)
    f = font(30, bold=True)
    d.text(((lab[0] + lab[2] - d.textlength(SYN, font=f)) / 2, sy + 7), SYN, font=f, fill=(170, 20, 20))
    edge_shade(img, lab, strength=60)
    finish(img, seed).save(path)

# ---------- main ----------

RX_IDS = ["metformin", "losartan", "lisinopril", "furosemide", "tamsulosin", "atorvastatin"]
last = latest_fills()
for i, drug in enumerate(RX_IDS):
    rx_bottle(drug, last[drug], os.path.join(out, f"{drug}.jpg"), seed=100 + i)
otc_box(os.path.join(out, "naproxen.jpg"), seed=200)
otc_vitamin(os.path.join(out, "vitamin_d.jpg"), seed=201)
print(len(RX_IDS) + 2, "bottle photos in", out)
