"""AYKUT video motoru — hesabın imza tarzı.
Mor/pembe/altın palet, çizilmiş diva maskot Aykut (sesle senkron ağız), kelime-öbek altyazıları,
AYOL! çıkartmaları, 'Öptüm' kapanışı.
"""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SR = 24000
MONT = '/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

# palet
BG_TOP = (36, 10, 58)
BG_BOT = (14, 4, 28)
PINK = (255, 46, 136)
PINK_L = (255, 140, 195)
GOLD = (255, 207, 64)
WHITE = (255, 255, 255)
INK = (24, 6, 40)
PURPLE = (120, 52, 200)

# ---------------- yardımcılar ----------------
_fc = {}
def font(size, weight='Black'):
    k = (size, weight)
    if k not in _fc:
        f = ImageFont.truetype(MONT, size); f.set_variation_by_name(weight); _fc[k] = f
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def prog(t, s, d): return clamp((t - s) / d)

def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').upper()

_ec = {}
def emoji_img(ch, size):
    k = (ch, size)
    if k not in _ec:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new('RGBA', (300, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        r = size / max(im.size)
        _ec[k] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _ec[k]

def paste_center(img, im, cx, cy, scale=1.0, rot=0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def draw_emoji(img, ch, cx, cy, size, scale=1.0, rot=0, alpha=1.0):
    paste_center(img, emoji_img(ch, size), cx, cy, scale, rot, alpha)

def text_w(s, f):
    return ImageDraw.Draw(Image.new('L', (1, 1))).textlength(s, font=f)

# ---------------- ses ----------------
def load_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    assert sr == SR, sr
    return a

def trim(a, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    s = max(0, idx[0] - int(0.03 * SR)); e = min(len(a), idx[-1] + int(0.06 * SR))
    return a[s:e]

def envelope(a, fps=FPS):
    hop = SR // fps
    n = int(math.ceil(len(a) / hop))
    pad = np.pad(a, (0, n * hop - len(a)))
    rms = np.sqrt((pad.reshape(n, hop) ** 2).mean(1))
    return rms

def pauses(env, thr):
    """sessizlik aralıklarının orta noktaları (saniye)"""
    quiet = env < thr; out = []; i = 0
    while i < len(env):
        if quiet[i]:
            j = i
            while j < len(env) and quiet[j]: j += 1
            if j - i >= 3: out.append(((i + j) / 2) / FPS)
            i = j
        else: i += 1
    return out

def chunk_times(chunks, voice_start, voice_dur, env):
    """altyazı öbeklerini sese yay; sınırları duraklamalara yapıştır"""
    w = np.array([max(4, len(c.replace('*', ''))) for c in chunks], float)
    cum = np.concatenate([[0], np.cumsum(w) / w.sum()])
    bounds = [voice_start + voice_dur * c for c in cum]
    ps = [voice_start + p for p in pauses(env, max(0.02, env.max() * 0.08))]
    for k in range(1, len(bounds) - 1):
        near = [p for p in ps if abs(p - bounds[k]) < 0.45]
        if near: bounds[k] = min(near, key=lambda p: abs(p - bounds[k]))
    return [(bounds[k], bounds[k + 1]) for k in range(len(chunks))]

# ---------------- arka plan ----------------
def make_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(BG_TOP)[None, None] * (1 - y) + np.array(BG_BOT)[None, None] * y
    arr = np.repeat(arr, W, 1)
    # pembe parıltı
    yy, xx = np.mgrid[0:H, 0:W]
    g = np.exp(-(((xx - W * 0.5) / 650) ** 2 + ((yy - 640) / 560) ** 2))
    arr = arr + g[..., None] * np.array([90, 10, 70])[None, None]
    # ince çapraz çizgiler (imza dokusu)
    stripes = ((xx + yy) // 26 % 2 == 0) * 5
    arr = arr + stripes[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')

BG = None
_star_rng = np.random.default_rng(7)
STARS = [(_star_rng.uniform(40, W - 40), _star_rng.uniform(230, 1250), _star_rng.uniform(8, 22),
          _star_rng.uniform(0, 6.28), _star_rng.uniform(1.2, 2.6), (GOLD if _star_rng.random() < 0.5 else PINK_L)) for _ in range(26)]

def star(d, cx, cy, r, col, a):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4; rr = r if k % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col + (int(255 * a),))

def background(t):
    global BG
    if BG is None: BG = make_bg()
    img = BG.copy()
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (x, y, r, ph, sp, col) in STARS:
        a = (0.5 + 0.5 * math.sin(t * sp + ph)) ** 2
        star(d, x, y + 6 * math.sin(t * 0.7 + ph), r * (0.6 + 0.4 * a), col, 0.15 + 0.55 * a)
    img.alpha_composite(L)
    return img

# ---------------- üst bant ----------------
def top_band(img, category, total_p):
    d = ImageDraw.Draw(img)
    # ilerleme çubuğu
    d.rounded_rectangle([60, 96, W - 60, 106], 5, fill=(255, 255, 255, 50))
    d.rounded_rectangle([60, 96, 60 + (W - 120) * clamp(total_p), 106], 5, fill=PINK + (255,))
    # wordmark
    f1 = font(46, 'Black'); f2 = font(30, 'ExtraBold')
    wm = 'AYKUT'; cat = tr_upper(category)
    w1 = text_w(wm, f1); w2 = text_w(cat, f2)
    tot = w1 + 70 + w2 + 56
    x0 = (W - tot) / 2; y0 = 140
    d.rounded_rectangle([x0, y0, x0 + tot, y0 + 74], 37, fill=WHITE + (255,))
    d.text((x0 + 28, y0 + 10), wm, font=f1, fill=INK + (255,))
    star(d, x0 + 28 + w1 + 35, y0 + 37, 17, PINK, 1)
    d.rounded_rectangle([x0 + 28 + w1 + 62, y0 + 12, x0 + tot - 12, y0 + 62], 25, fill=PINK + (255,))
    d.text((x0 + 28 + w1 + 62 + 16, y0 + 19), cat, font=f2, fill=WHITE + (255,))

# ---------------- altyazı ----------------
def caption(img, text, t_in, t, y=1010):
    """*kelime* pembe vurgulanır. Öbek giriş animasyonu ile."""
    p = ease_back(prog(t, t_in, 0.22))
    if p <= 0: return
    words = text.split(); f = font(74, 'Black'); sp = 22
    toks = []
    for wd in words:
        hl = wd.startswith('*')
        toks.append((tr_upper(wd.strip('*')), hl))
    # satırlara böl (max 900px)
    lines = [[]]; lw = 0
    for tok in toks:
        ww = text_w(tok[0], f)
        if lines[-1] and lw + sp + ww > 920: lines.append([]); lw = 0
        lines[-1].append((tok, ww)); lw += (sp if lw else 0) + ww
    lh = 92; Hh = lh * len(lines) + 40
    L = Image.new('RGBA', (W, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i, ln in enumerate(lines):
        tw = sum(w for _, w in ln) + sp * (len(ln) - 1); x = (W - tw) / 2; yy = 20 + i * lh
        for (word, hl), ww in ln:
            if hl:
                d.rounded_rectangle([x - 12, yy + 2, x + ww + 12, yy + lh - 6], 16, fill=PINK + (255,))
                d.text((x, yy), word, font=f, fill=WHITE + (255,))
            else:
                d.text((x, yy), word, font=f, fill=WHITE + (255,), stroke_width=9, stroke_fill=INK + (255,))
            x += ww + sp
    paste_center(img, L, W / 2, y + Hh / 2 - 40, scale=0.85 + 0.15 * p, alpha=clamp(p * 1.5))

# ---------------- çıkartma / damga ----------------
def sticker(img, text, cx, cy, t, t_in, rot=-8, color=PINK, size=64, txt=WHITE):
    p = ease_back(prog(t, t_in, 0.35))
    if p <= 0: return
    f = font(size, 'Black'); tw = text_w(text, f)
    L = Image.new('RGBA', (int(tw + 90), int(size * 1.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([6, 6, L.width - 6, L.height - 6], 26, fill=WHITE + (255,))
    d.rounded_rectangle([16, 16, L.width - 16, L.height - 16], 20, fill=color + (255,))
    d.text(((L.width - tw) / 2, (L.height - size * 1.18) / 2), text, font=f, fill=txt + (255,))
    wob = 3 * math.sin((t - t_in) * 6)
    paste_center(img, L, cx, cy, scale=p, rot=rot + wob)

def badge(img, n, t, cx=W / 2, cy=330):
    p = ease_back(prog(t, 0, 0.4))
    if p <= 0: return
    S = 2; L = Image.new('RGBA', (260 * S, 260 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = 130 * S; r = 95 * S
    d.ellipse([c - r - 8 * S, c - r - 8 * S, c + r + 8 * S, c + r + 8 * S], fill=WHITE + (255,))
    d.ellipse([c - r, c - r, c + r, c + r], fill=PINK + (255,))
    f = font(130 * S, 'Black'); s = str(n); w = text_w(s, f)
    d.text((c - w / 2, c - 0.70 * 130 * S), s, font=f, fill=WHITE + (255,))
    L = L.resize((260, 260), Image.LANCZOS)
    paste_center(img, L, cx, cy, scale=p, rot=8 * math.sin(t * 2))

def chip(img, text, cx, cy, t, t_in, bg=WHITE, fg=INK, size=48):
    p = ease_back(prog(t, t_in, 0.3))
    if p <= 0: return
    f = font(size, 'Black'); tw = text_w(text, f)
    L = Image.new('RGBA', (int(tw + 64), int(size * 1.7)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, L.width - 1, L.height - 1], L.height // 2, fill=bg + (255,))
    d.text((32, (L.height - size * 1.2) / 2), text, font=f, fill=fg + (255,))
    paste_center(img, L, cx, cy, scale=p)

def big_title(img, lines, t, t_in, y=560, size=112, colors=None):
    """büyük başlık; her satır sırayla zıplar"""
    for i, ln in enumerate(lines):
        p = ease_back(prog(t, t_in + i * 0.18, 0.4))
        if p <= 0: continue
        f = font(size, 'Black'); s = tr_upper(ln); tw = text_w(s, f)
        col = (colors[i] if colors else WHITE)
        L = Image.new('RGBA', (int(tw + 40), int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.text((20, 4), s, font=f, fill=col + (255,), stroke_width=10, stroke_fill=INK + (255,))
        paste_center(img, L, W / 2, y + i * size * 1.12, scale=p)

# ---------------- AYKUT maskotu ----------------
SKIN = (247, 200, 166); SKIN_D = (224, 160, 122); HAIR = (46, 20, 62); HAIR_L = (90, 40, 120)

def aykut(mouth=0.0, blink=0.0, expr='sass', look=(0, 0), t=0.0):
    """500x600 RGBA maskot. expr: sass | shock | smug | kiss"""
    S = 2; Wd, Hd = 500 * S, 600 * S
    L = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def E(cx, cy, rx, ry, **k): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], **k)
    # gövde
    d.rounded_rectangle([90 * S, 470 * S, 410 * S, 640 * S], 90 * S, fill=PURPLE + (255,))
    d.rectangle([215 * S, 420 * S, 285 * S, 490 * S], fill=SKIN_D + (255,))
    # boa (tüylü pembe şal)
    for k in range(15):
        a = math.pi * (0.05 + 0.9 * k / 14)
        x = 250 - 175 * math.cos(a); y = 488 + 40 * math.sin(a) * 0.9 + 14 * math.sin(k * 1.7 + t * 3)
        E(x, y, 38, 34, fill=(PINK if k % 2 else PINK_L) + (255,))
    # kulaklar + küpe
    E(98, 300, 26, 36, fill=SKIN_D + (255,)); E(402, 300, 26, 36, fill=SKIN_D + (255,))
    d.ellipse([388 * S, 330 * S, 424 * S, 374 * S], outline=GOLD + (255,), width=7 * S)
    # kafa
    E(250, 285, 152, 168, fill=SKIN + (255,))
    # saç: kabarık perçem
    E(250, 142, 156, 66, fill=HAIR + (255,))
    E(300, 112, 128, 78, fill=HAIR + (255,))
    E(205, 128, 92, 64, fill=HAIR + (255,))
    E(110, 238, 16, 44, fill=HAIR + (255,)); E(390, 238, 16, 44, fill=HAIR + (255,))  # kısa favoriler
    d.arc([200 * S, 50 * S, 420 * S, 200 * S], 200, 300, fill=PINK + (255,), width=16 * S)  # pembe röfle
    d.arc([180 * S, 70 * S, 380 * S, 210 * S], 205, 290, fill=HAIR_L + (255,), width=8 * S)
    # sakal gölgesi
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([128 * S, 330 * S, 372 * S, 458 * S], fill=(120, 80, 90, 38))
    hm = Image.new('L', L.size, 0); ImageDraw.Draw(hm).ellipse([98 * S, 117 * S, 402 * S, 453 * S], fill=255)
    L.alpha_composite(Image.composite(sh, Image.new('RGBA', L.size, (0, 0, 0, 0)), hm)); d = ImageDraw.Draw(L)
    # yanak allığı
    bl = Image.new('RGBA', L.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    for bx in (165, 335): bd.ellipse([(bx - 34) * S, 330 * S, (bx + 34) * S, 362 * S], fill=(255, 110, 140, 70))
    L.alpha_composite(bl); d = ImageDraw.Draw(L)
    # gözler
    for i, ex in enumerate((192, 308)):
        ey = 292; ry = 38 * (1 - 0.92 * blink)
        if expr == 'shock': ry *= 1.15
        E(ex, ey, 34, max(3, ry), fill=WHITE + (255,))
        if blink < 0.6:
            px = ex + look[0] * 10; py = ey + look[1] * 8 + 4
            E(px, py, 17, min(19, ry * 0.6), fill=INK + (255,)); E(px + 6, py - 7, 5, 5, fill=WHITE + (255,))
        # kirpikler (dış köşe)
        sgn = -1 if i == 0 else 1
        bx = ex + sgn * 32; by = ey - ry * 0.45
        d.line([bx * S, by * S, (bx + sgn * 20) * S, (by - 12) * S], fill=INK + (255,), width=6 * S)  # eyeliner kıvrımı
        # üst göz çizgisi
        d.arc([(ex - 36) * S, (ey - ry - 2) * S, (ex + 36) * S, (ey + ry + 2) * S], 190, 350, fill=INK + (255,), width=6 * S)
    # kaşlar
    lift = {'sass': (26, 0), 'shock': (24, 24), 'smug': (6, 6), 'kiss': (14, 14)}[expr]
    for i, ex in enumerate((192, 308)):
        up = lift[i]; y = 252 - up
        d.arc([(ex - 44) * S, (y - 20) * S, (ex + 44) * S, (y + 30) * S], 200, 340, fill=HAIR + (255,), width=10 * S)
    # burun
    d.arc([235 * S, 318 * S, 268 * S, 350 * S], 20, 160, fill=SKIN_D + (255,), width=5 * S)
    # ağız
    mx, my = 252, 388
    for sg in (-1, 1):  # ince kıvrık bıyık
        d.chord([(mx + sg * 4 - (58 if sg < 0 else 0)) * S, (my - 50) * S, (mx + sg * 4 + (58 if sg > 0 else 0)) * S, (my - 14) * S], 180, 360, fill=HAIR + (255,))
        d.arc([(mx + sg * 54 - 14) * S, (my - 50) * S, (mx + sg * 54 + 14) * S, (my - 22) * S], (90 if sg > 0 else 270) - 120, (90 if sg > 0 else 270) + 60, fill=HAIR + (255,), width=5 * S)
    if expr == 'kiss' and mouth < 0.15:
        E(mx, my, 24, 20, fill=(230, 40, 100, 255)); E(mx, my, 10, 7, fill=(140, 10, 50, 255))
    elif expr == 'shock' and mouth < 0.15:
        E(mx, my + 4, 24, 30, fill=(122, 16, 48, 255))
    elif mouth < 0.08:
        d.arc([(mx - 46) * S, (my - 34) * S, (mx + 46) * S, (my + 12) * S], 25, 155, fill=(150, 30, 60, 255), width=8 * S)
        d.arc([(mx + 30) * S, (my - 22) * S, (mx + 52) * S, (my) * S], 300, 60, fill=(150, 30, 60, 255), width=6 * S)
    else:
        h = 10 + 52 * mouth; w = 44 + 10 * mouth
        d.rounded_rectangle([(mx - w) * S, (my - h / 2) * S, (mx + w) * S, (my + h / 2) * S], int(h / 2 * S), fill=(122, 16, 48, 255))
        d.rectangle([(mx - w + 12) * S, (my - h / 2) * S, (mx + w - 12) * S, (my - h / 2 + 9) * S], fill=WHITE + (255,))
        E(mx, my + h / 2 - 8, w * 0.55, 9 + 6 * mouth, fill=(240, 100, 130, 255))
    return L.resize((500, 600), Image.LANCZOS)

CROC = (92, 186, 96); CROC_D = (54, 138, 72); CROC_L = (196, 232, 150); CROC_DD = (34, 96, 52)

def aykut_croc(mouth=0.0, blink=0.0, expr='sass', look=(0, 0), t=0.0):
    """500x600 RGBA diva timsah Aykut. expr: sass | shock | smug | kiss"""
    S = 2; Wd, Hd = 500 * S, 600 * S
    L = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def E(cx, cy, rx, ry, **k): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], **k)
    # kuyruk (gövdenin arkasında, sallanır)
    sway = math.sin(t * 2.6)
    pts = []
    for k in range(41):
        u = k / 40
        pts.append((370 + 105 * u, 600 - 130 * u * u + 35 * sway * u * u, 44 * (1 - 0.8 * u)))
    for k in range(4, 40, 7):
        x, y, r = pts[k]
        d.polygon([((x - r * 0.35) * S, (y - r * 0.8) * S), ((x + r * 0.35) * S, (y - r * 0.8) * S), (x * S, (y - r * 1.25) * S)], fill=CROC_D + (255,))
    for x, y, r in pts: E(x, y, r, r * 0.9, fill=CROC + (255,))
    # gövde + boyun
    d.rounded_rectangle([90 * S, 470 * S, 410 * S, 640 * S], 90 * S, fill=PURPLE + (255,))
    d.rounded_rectangle([185 * S, 380 * S, 315 * S, 490 * S], 30 * S, fill=CROC_D + (255,))
    # boa
    for k in range(15):
        a = math.pi * (0.05 + 0.9 * k / 14)
        x = 250 - 175 * math.cos(a); y = 488 + 40 * math.sin(a) * 0.9 + 14 * math.sin(k * 1.7 + t * 3)
        E(x, y, 38, 34, fill=(PINK if k % 2 else PINK_L) + (255,))
    # kafa (kafatası) + yanak pulları
    E(250, 240, 165, 110, fill=CROC + (255,))
    for (sx, sy, r) in [(118, 222, 11), (138, 250, 9), (110, 255, 7), (382, 222, 11), (362, 250, 9), (390, 255, 7)]:
        E(sx, sy, r, r, fill=CROC_D + (255,))
    # altın küpe (yan tarafta)
    d.ellipse([392 * S, 280 * S, 428 * S, 324 * S], outline=GOLD + (255,), width=7 * S)
    # göz tümsekleri
    for ex in (178, 322): E(ex, 168, 64, 62, fill=CROC + (255,))
    # saç: kabarık perçem + pembe röfle
    E(250, 84, 62, 38, fill=HAIR + (255,)); E(276, 68, 52, 36, fill=HAIR + (255,)); E(228, 74, 40, 30, fill=HAIR + (255,))
    d.arc([212 * S, 36 * S, 336 * S, 120 * S], 200, 300, fill=PINK + (255,), width=12 * S)
    d.arc([202 * S, 48 * S, 312 * S, 126 * S], 205, 290, fill=HAIR_L + (255,), width=6 * S)
    # gözler
    for i, ex in enumerate((178, 322)):
        ey = 170; ry = 40 * (1 - 0.92 * blink)
        if expr == 'shock': ry *= 1.15
        E(ex, ey, 38, max(3, ry), fill=WHITE + (255,))
        if blink < 0.6:
            px = ex + look[0] * 12; py = ey + look[1] * 8 + 4
            E(px, py, 19, min(22, ry * 0.65), fill=INK + (255,)); E(px + 7, py - 8, 6, 6, fill=WHITE + (255,))
        sgn = -1 if i == 0 else 1
        bx = ex + sgn * 36; by = ey - ry * 0.45
        d.line([bx * S, by * S, (bx + sgn * 22) * S, (by - 14) * S], fill=INK + (255,), width=6 * S)
        d.arc([(ex - 40) * S, (ey - ry - 2) * S, (ex + 40) * S, (ey + ry + 2) * S], 190, 350, fill=INK + (255,), width=6 * S)
    # kaşlar
    lift = {'sass': (24, 0), 'shock': (22, 22), 'smug': (4, 4), 'kiss': (12, 12)}[expr]
    for i, ex in enumerate((178, 322)):
        y = 138 - 0.6 * lift[i]
        d.arc([(ex - 40) * S, (y - 18) * S, (ex + 40) * S, (y + 26) * S], 205, 335, fill=HAIR + (255,), width=11 * S)
    # ağız / çeneler
    jy = 352
    if expr == 'shock' and mouth < 0.15: o = 50
    elif mouth < 0.08: o = 0
    else: o = 8 + 58 * mouth
    if o > 0:
        d.rounded_rectangle([168 * S, (jy - 20) * S, 332 * S, (jy + o + 30) * S], 30 * S, fill=(122, 16, 48, 255))
        E(250, jy + o + 14, 54, 12 + 6 * mouth, fill=(240, 100, 130, 255))
    # alt çene (üst çenenin altına oturur)
    d.rounded_rectangle([150 * S, (jy - 30 + o) * S, 350 * S, (jy + 74 + o) * S], 56 * S, fill=CROC_L + (255,))
    d.rounded_rectangle([150 * S, (jy - 30 + o) * S, 350 * S, (jy + 74 + o) * S], 56 * S, outline=CROC + (255,), width=6 * S)
    lt = jy + o + 2
    for k in range(6):
        x = 192 + k * 23.3
        d.polygon([((x - 7) * S, (lt + 4) * S), ((x + 7) * S, (lt + 4) * S), (x * S, (lt - 12) * S)], fill=WHITE + (255,))
    # üst çene (burun) en üstte
    d.rounded_rectangle([146 * S, 210 * S, 354 * S, jy * S], 70 * S, fill=CROC + (255,))
    for k in range(7):
        x = 180 + k * 23.3
        d.polygon([((x - 8) * S, (jy - 6) * S), ((x + 8) * S, (jy - 6) * S), (x * S, (jy + 12) * S)], fill=WHITE + (255,))
    E(222, 252, 15, 11, fill=CROC_D + (255,)); E(278, 252, 15, 11, fill=CROC_D + (255,))
    E(222, 254, 6, 5, fill=CROC_DD + (255,)); E(278, 254, 6, 5, fill=CROC_DD + (255,))
    bl = Image.new('RGBA', L.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    for bx in (160, 340): bd.ellipse([(bx - 28) * S, 282 * S, (bx + 28) * S, 308 * S], fill=(255, 110, 140, 90))
    L.alpha_composite(bl); d = ImageDraw.Draw(L)
    # ince kıvrık bıyık (ağız çizgisinin hemen üstünde)
    mx, my = 250, jy - 6
    for sg in (-1, 1):
        d.chord([(mx + sg * 4 - (54 if sg < 0 else 0)) * S, (my - 40) * S, (mx + sg * 4 + (54 if sg > 0 else 0)) * S, (my - 12) * S], 180, 360, fill=HAIR + (255,))
        d.arc([(mx + sg * 50 - 13) * S, (my - 40) * S, (mx + sg * 50 + 13) * S, (my - 16) * S], (90 if sg > 0 else 270) - 120, (90 if sg > 0 else 270) + 60, fill=HAIR + (255,), width=5 * S)
    if o == 0 and expr == 'smug':
        d.arc([300 * S, (jy - 30) * S, 350 * S, (jy + 6) * S], 20, 110, fill=CROC_DD + (255,), width=6 * S)
    if o == 0 and expr == 'kiss':
        E(238, jy + 8, 16, 14, fill=(230, 40, 100, 255)); E(262, jy + 8, 16, 14, fill=(230, 40, 100, 255))
        d.polygon([(224 * S, (jy + 12) * S), (276 * S, (jy + 12) * S), (250 * S, (jy + 36) * S)], fill=(230, 40, 100, 255))
    return L.resize((500, 600), Image.LANCZOS)

MASCOT = os.environ.get('AYKUT_MASCOT', 'classic')

class Mouth:
    def __init__(self, env):
        m = env / (np.percentile(env, 92) + 1e-6)
        m = np.clip((m - 0.12) / 0.8, 0, 1)
        sm = np.zeros_like(m)
        for i in range(len(m)): sm[i] = m[i] if i == 0 else 0.55 * m[i] + 0.45 * sm[i - 1]
        self.m = sm
    def __call__(self, fi):
        return float(self.m[fi]) if 0 <= fi < len(self.m) else 0.0

def blink_at(t):
    ph = (t + 0.37) % 3.1
    return clamp(1 - abs(ph - 0.1) / 0.1) if ph < 0.2 else 0.0

def place_aykut(img, mouth, t, expr='sass', cx=270, cy=1480, scale=0.82, enter=1.0):
    bob = 10 * mouth + 6 * math.sin(t * 2.2)
    rot = 4 * math.sin(t * 1.6) + 5 * mouth * math.sin(t * 9)
    look = (0.3 * math.sin(t * 0.9), -0.2)
    im = (aykut_croc if MASCOT == 'croc' else aykut)(mouth, blink_at(t), expr, look, t)
    paste_center(img, im, cx, cy - bob + (1 - enter) * 500, scale=scale, rot=rot)

# ---------------- sahne / render ----------------
class Scene:
    def __init__(self, wav, chunks, visual, expr='sass', lead=0.15, tail=0.35, aykut_pos=None):
        a = trim(load_wav(wav))
        self.voice = a; self.lead = lead; self.vdur = len(a) / SR
        self.dur = lead + self.vdur + tail
        n = int(round(self.dur * FPS))
        full = np.concatenate([np.zeros(int(lead * SR)), a, np.zeros(int(tail * SR) + SR)])[: n * (SR // FPS)]
        self.audio = full
        env = envelope(full)
        self.mouth = Mouth(env)
        self.ctimes = chunk_times(chunks, lead, self.vdur, envelope(a))
        self.chunks = chunks; self.visual = visual; self.expr = expr; self.aykut_pos = aykut_pos

def render_video(name, category, scenes, outro_text='ÖPTÜM', out_dir='out', music_seed=1):
    os.makedirs(out_dir, exist_ok=True)
    total = sum(s.dur for s in scenes); OUT_EXTRA = 1.3
    scenes[-1].dur += OUT_EXTRA
    t0s = np.cumsum([0] + [s.dur for s in scenes])
    files = []
    for si, sc in enumerate(scenes):
        tmp, fin = f'{out_dir}/{name}_s{si}.tmp.mp4', f'{out_dir}/{name}_s{si}.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                              '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', tmp],
                             stdin=subprocess.PIPE)
        nfr = int(round(sc.dur * FPS))
        for fi in range(nfr):
            p.stdin.write(frame(sc, si, len(scenes), fi, t0s, total + OUT_EXTRA, category, outro_text).convert('RGB').tobytes())
        p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); files.append(fin)
    with open(f'{out_dir}/{name}_list.txt', 'w') as f:
        for fn in files: f.write(f"file '{os.path.basename(fn)}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{out_dir}/{name}_list.txt',
                    '-c', 'copy', f'{out_dir}/{name}_v.mp4'], check=True)
    # ses: konuşma + müzik + efekt
    voice = np.concatenate([np.pad(s.audio, (0, max(0, int(round(s.dur * FPS)) * (SR // FPS) - len(s.audio))))[: int(round(s.dur * FPS)) * (SR // FPS)] for s in scenes])
    mix = mixdown(voice, [int(t * SR) for t in t0s[:-1]], seed=music_seed)
    write_wav(f'{out_dir}/{name}_a.wav', mix)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out_dir}/{name}_v.mp4', '-i', f'{out_dir}/{name}_a.wav',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    f'{out_dir}/{name}.mp4'], check=True)
    return f'{out_dir}/{name}.mp4'

def frame(sc, si, nsc, fi, t0s, total, category, outro_text):
    t = fi / FPS; T = t0s[si] + t
    img = background(T)
    sc.visual(img, t, sc)
    top_band(img, category, T / total)
    # altyazı
    for (a, b), ch in zip(sc.ctimes, sc.chunks):
        if a - 0.05 <= t < b + (0.25 if ch is sc.chunks[-1] else 0):
            caption(img, ch, a - 0.05, t)
    # maskot
    m = sc.mouth(fi)
    last = si == nsc - 1
    end_t = sc.lead + sc.vdur + 0.2
    if last and t > end_t:
        k = ease_out(prog(t, end_t, 0.5))
        place_aykut(img, 0, t, 'kiss', cx=270 + (W / 2 - 270) * k, cy=1480 - 400 * k, scale=0.82 + 0.4 * k)
        for j in range(5):
            tt = t - end_t - 0.25 - j * 0.12
            if tt > 0:
                draw_emoji(img, '💋' if j % 2 == 0 else '💖', W / 2 + 150 + j * 30 + 50 * math.sin(tt * 3 + j), 1150 - tt * 420, 70,
                           alpha=clamp(1.4 - tt))
        sticker(img, tr_upper(outro_text), W / 2, 1530, t, end_t + 0.35, rot=6)
    else:
        enter = ease_back(prog(T, 0, 0.5))
        expr = sc.expr(t) if callable(sc.expr) else sc.expr
        cx, cy, scl = sc.aykut_pos if sc.aykut_pos else (270, 1480, 0.82)
        place_aykut(img, m, t, expr, cx=cx, cy=cy, scale=scl, enter=enter)
    # sahne geçişi: beyaz flaş
    if si > 0 and t < 0.12:
        fl = Image.new('RGBA', (W, H), (255, 255, 255, int(120 * (1 - t / 0.12)))); img.alpha_composite(fl)
    return img

# ---------------- müzik ve efektler ----------------
def write_wav(path, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())

def nf(m): return 440 * 2 ** ((m - 69) / 12)

def music(n, seed=1):
    rng = np.random.default_rng(seed)
    bpm = 118; beat = 60 / bpm; out = np.zeros(n)
    progs = [[[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],
             [[50, 53, 57], [55, 59, 62], [48, 52, 55], [57, 60, 64]]]
    chords = progs[seed % 2]
    t = 0.0; i = 0
    while t < n / SR:
        s = int(t * SR)
        ch = chords[(i // 8) % 4]
        # kick her vuruş
        if i % 2 == 0:
            L = int(0.18 * SR); tt = np.arange(min(L, n - s)) / SR
            out[s:s + len(tt)] += 0.55 * np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 18)
        # clap 2 ve 4
        if i % 4 == 2:
            L = int(0.12 * SR); tt = np.arange(min(L, n - s)) / SR
            out[s:s + len(tt)] += 0.18 * rng.standard_normal(len(tt)) * np.exp(-tt * 30)
        # hi-hat
        L = int(0.04 * SR); tt = np.arange(min(L, n - s)) / SR
        hh = rng.standard_normal(len(tt)); hh = np.diff(np.concatenate([[0], hh]))
        out[s:s + len(tt)] += (0.05 if i % 2 else 0.03) * hh * np.exp(-tt * 90)
        # bas (offbeat)
        if i % 2 == 1:
            L = int(beat / 2 * SR); tt = np.arange(min(L, n - s)) / SR
            f = nf(ch[0] - 12)
            out[s:s + len(tt)] += 0.22 * np.tanh(2 * np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 5)
        # pluck arpej
        if i % 2 == 0 or rng.random() < 0.3:
            m = ch[(i // 2) % 3] + 12
            L = int(0.35 * SR); tt = np.arange(min(L, n - s)) / SR; f = nf(m)
            out[s:s + len(tt)] += 0.12 * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 9)
        t += beat / 2; i += 1
    return out / (np.abs(out).max() + 1e-6)

def sfx_sparkle(n=int(0.6 * SR)):
    tt = np.arange(n) / SR; out = np.zeros(n)
    for k, m in enumerate([84, 88, 91, 96]):
        s = int(k * 0.06 * SR); x = tt[: n - s]
        out[s:] += np.sin(2 * np.pi * nf(m) * x) * np.exp(-x * 8)
    return out * 0.25

def sfx_pop(n=int(0.12 * SR)):
    tt = np.arange(n) / SR
    return 0.35 * np.sin(2 * np.pi * (300 + 900 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 35)

def mixdown(voice, scene_starts, seed=1):
    n = len(voice)
    mus = music(n, seed)
    env = np.convolve(np.abs(voice), np.ones(2400) / 2400, mode='same')
    duck = 1 - 0.6 * np.clip(env / 0.03, 0, 1)
    mus = mus * (0.20 * duck)
    fade = int(1.0 * SR); mus[-fade:] *= np.linspace(1, 0, fade); mus[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    v = voice / (np.abs(voice).max() + 1e-6) * 0.92
    out = v + mus
    sp = sfx_sparkle(); out[: len(sp)] += sp
    for s in scene_starts[1:]:
        p = sfx_pop(); out[s:s + len(p)] += p[: n - s]
    # öptüm parıltısı
    s = n - int(1.6 * SR); out[s:s + len(sp)] += sp[: n - s] * 1.2
    return out / max(1.0, np.abs(out).max() / 0.98)
