import sys, math
from PIL import Image, ImageDraw
from engine import *

A = 'audio/'

# ======================= VİDEO 1: Şaşırtıcı bilgiler =======================
def v1_s0(img, t, sc):
    big_title(img, ['3 bilgi', 'biri seni', 'bitirecek'], t, 0.1, y=490, colors=[WHITE, GOLD, PINK])
    sticker(img, 'AYOL!', 820, 320, t, 0.05, rot=10)
    draw_emoji(img, '🤯', 250, 320, 140, scale=ease_back(prog(t, 0.3, 0.4)), rot=8 * math.sin(t * 3))

def v1_s1(img, t, sc):
    badge(img, 1, t)
    draw_emoji(img, '🐙', 540, 640, 330, scale=ease_back(prog(t, 0.15, 0.5)), rot=6 * math.sin(t * 2.4))
    for k, (x, y) in enumerate([(270, 520), (810, 520), (540, 860)]):
        p = ease_back(prog(t, 0.9 + k * 0.3, 0.35))
        beat = 1 + 0.12 * max(0, math.sin(t * 8 + k)) ** 8
        draw_emoji(img, '❤️', x, y, 120, scale=p * beat)

def v1_s2(img, t, sc):
    badge(img, 2, t)
    draw_emoji(img, '🍯', 540, 600, 300, scale=ease_back(prog(t, 0.15, 0.5)), rot=5 * math.sin(t * 2))
    draw_emoji(img, '🏺', 830, 770, 150, scale=ease_back(prog(t, 1.6, 0.4)), rot=-8)
    chip(img, tr_upper('binlerce yıllık'), 540, 900, t, 1.9, bg=GOLD)

def planet(img, t, cx, cy, r):
    S = 2; size = int(r * 2 + 120)
    L = Image.new('RGBA', (size * S, size * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L); c = size * S / 2; R = r * S
    for k in range(6, 0, -1):
        rr = R + k * 14 * S; d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=(255, 200, 120, 12))
    d.ellipse([c - R, c - R, c + R, c + R], fill=(236, 176, 92, 255))
    mask = Image.new('L', L.size, 0); ImageDraw.Draw(mask).ellipse([c - R, c - R, c + R, c + R], fill=255)
    bands = Image.new('RGBA', L.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bands); off = (t * 20 * S) % (240 * S)
    for yy, hh, col in [(-0.65, 0.16, (210, 140, 60)), (-0.25, 0.25, (252, 205, 125)), (0.15, 0.14, (200, 125, 55)), (0.45, 0.2, (246, 190, 110))]:
        for j in range(-3, 4):
            x = c + j * 240 * S + off
            bd.ellipse([x - 150 * S, c + yy * R, x + 150 * S, c + (yy + hh) * R], fill=col + (210,))
    empty = Image.new('RGBA', L.size, (0, 0, 0, 0))
    L.alpha_composite(Image.composite(bands, empty, mask))
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([c - R + 0.45 * R, c - R - 30 * S, c + R + 0.9 * R, c + R + 30 * S], fill=(30, 6, 40, 130))
    L.alpha_composite(Image.composite(sh, empty, mask))
    L = L.resize((size, size), Image.LANCZOS)
    paste_center(img, L, cx, cy)

def v1_s3(img, t, sc):
    badge(img, 3, t)
    p = ease_back(prog(t, 0.15, 0.5))
    if p > 0: planet(img, t, 540, 600, 200 * p)
    chip(img, tr_upper('kendi turu: 243 gün'), 540, 865, t, 1.3, bg=PINK, fg=WHITE)
    chip(img, tr_upper('güneş turu: 225 gün'), 540, 955, t, 3.6, bg=GOLD)
    sticker(img, tr_upper('pazartesi bitmiyor!'), 540, 430, t, sc.vdur - 1.6, rot=-7, size=56)

def v1_s4(img, t, sc):
    big_title(img, ['hangisini', 'biliyordun?'], t, 0.05, y=430, size=104, colors=[WHITE, GOLD])
    for k, e in enumerate(['1️⃣', '2️⃣', '3️⃣']):
        draw_emoji(img, e, 330 + k * 210, 760, 150, scale=ease_back(prog(t, 0.6 + k * 0.15, 0.35)), rot=6 * math.sin(t * 3 + k))

def v1_expr3(t): return 'shock' if t > 7.5 else 'sass'

VIDEOS = {}
VIDEOS['v1'] = dict(category='şaşırtıcı bilgi', seed=1, scenes=lambda: [
    Scene(A + 'v1_s0.wav', ['*Ayol* durun!', 'Size üç bilgi getirdim,', 'oturduğunuz yerden *düşeceksiniz.*', 'Sonuncusu beni bile *bitirdi!*'], v1_s0, expr='shock'),
    Scene(A + 'v1_s1.wav', ['Bir: Ahtapotların', 'tam *üç* *kalbi* varmış.', '*Üç!*', 'Kızım ben bir tanesini', '*idare* *edemiyorum,*', 'bunlar üç tane taşıyor!'], v1_s1),
    Scene(A + 'v1_s2.wav', ['İki: Bal neredeyse', 'hiç *bozulmuyor.*', 'Mısır mezarlarında', '*binlerce* *yıllık* bal bulmuşlar.', 'Ben üç günde sararıyorum,', '*haksızlık* bu!'], v1_s2),
    Scene(A + 'v1_s3.wav', ['Üç, *tutunun:*', 'Venüs kendi etrafında bir turu', '*243* *günde* atıyor,', "Güneş'in etrafını ise", '*225* *günde* dönüyor.', 'Yani orada pazartesiler', '*bitmek* *bilmiyor* ayol!'], v1_s3, expr=v1_expr3),
    Scene(A + 'v1_s4.wav', ['*Hangisini* biliyordun?', 'Yorumlara yaz,', 'takip etmeyi de *unutma.*', '*Öptüm!*'], v1_s4),
])

# ======================= VİDEO 2: Göz yanılması =======================
def ml_figure(img, t, fins=1.0, guides=0.0, appear=1.0):
    S = 2; L = Image.new('RGBA', (W * S, 760 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x0, x1 = 290, 790; ys = [230, 530]; f = 95; lw = 18
    for i, y in enumerate(ys):
        p = ease_back(prog(appear, i * 0.25, 0.5))
        if p <= 0: continue
        col = WHITE + (255,)
        mx = (x0 + x1) / 2; hx = (x1 - x0) / 2 * p
        d.line([(mx - hx) * S, y * S, (mx + hx) * S, y * S], fill=col, width=lw * S)
        if fins > 0 and p > 0.9:
            fc = WHITE + (int(255 * fins),)
            sgn = -1 if i == 0 else 1  # üst: dışa açık >—<, alt: içe <—>
            for ex, dirx in [(x0, 1), (x1, -1)]:
                for dy in (-1, 1):
                    d.line([ex * S, y * S, (ex + sgn * dirx * f) * S, (y + dy * f) * S], fill=fc, width=lw * S)
            for ex in (x0, x1):
                d.ellipse([(ex - lw / 2) * S, (y - lw / 2) * S, (ex + lw / 2) * S, (y + lw / 2) * S], fill=col)
    if guides > 0:
        gc = PINK + (int(255 * guides),)
        for ex in (x0, x1):
            yy = 120
            while yy < 640:
                d.line([ex * S, yy * S, ex * S, (yy + 30) * S], fill=gc, width=8 * S); yy += 52
    L = L.resize((W, 760), Image.LANCZOS)
    img.alpha_composite(L, (0, 260))

def v2_s0(img, t, sc):
    ml_figure(img, t, appear=t)
    chip(img, 'A', 130, 490, t, 0.3, bg=PINK, fg=WHITE, size=56)
    chip(img, 'B', 130, 790, t, 0.55, bg=GOLD, size=56)
    draw_emoji(img, '🤔', 930, 330, 120, scale=ease_back(prog(t, 1.2, 0.4)), rot=10 * math.sin(t * 3))

def v2_s1(img, t, sc):
    fins = 1 - prog(t, sc.vdur - 1.3, 0.8)
    ml_figure(img, t, fins=fins, guides=prog(t, 1.4, 0.4))
    chip(img, 'A', 130, 490, t, -1, bg=PINK, fg=WHITE, size=56)
    chip(img, 'B', 130, 790, t, -1, bg=GOLD, size=56)
    sticker(img, tr_upper('aynı boy!'), 540, 640, t, 1.6, rot=-8)

def v2_s2(img, t, sc):
    draw_emoji(img, '🧠', 540, 560, 270, scale=ease_back(prog(t, 0.05, 0.45)), rot=6 * math.sin(t * 2.5))
    draw_emoji(img, '🤥', 790, 420, 140, scale=ease_back(prog(t, 1.1, 0.4)), rot=-10)
    chip(img, tr_upper('beyin yalancı'), 540, 800, t, 0.8, bg=PINK, fg=WHITE)
    chip(img, tr_upper('"5 dk\'ya çıkıyorum"'), 540, 900, t, 2.6, bg=GOLD)

def ebb(img, t, surround=1.0, slide=0.0, appear=1.0):
    S = 2; L = Image.new('RGBA', (W * S, 700 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    OR = (255, 140, 40, 255); GR = (205, 190, 235)
    cy = 330
    centers = [(290 + 140 * ease_out(slide), cy), (790 - 140 * ease_out(slide), cy)]
    def C(x, y, r, col): d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col)
    a = int(255 * surround)
    p1 = ease_back(prog(appear, 0, 0.5)); p2 = ease_back(prog(appear, 0.25, 0.5))
    if a > 0:
        for k in range(6):
            ang = k * math.pi / 3; C(290 + 175 * math.cos(ang) * p1, cy + 175 * math.sin(ang) * p1, 82 * p1, GR + (a,))
        for k in range(8):
            ang = k * math.pi / 4; C(790 + 102 * math.cos(ang) * p2, cy + 102 * math.sin(ang) * p2, 26 * p2, GR + (a,))
    C(centers[0][0], cy, 62 * p1, OR); C(centers[1][0], cy, 62 * p2, OR)
    L = L.resize((W, 700), Image.LANCZOS)
    img.alpha_composite(L, (0, 290))

def v2_s3(img, t, sc):
    ebb(img, t, appear=t)
    chip(img, tr_upper('sol'), 290, 925, t, 1.6, bg=PINK, fg=WHITE)
    chip(img, tr_upper('sağ'), 790, 925, t, 1.8, bg=GOLD)

def v2_s4(img, t, sc):
    ebb(img, t, surround=1 - prog(t, 0.0, 0.6), slide=prog(t, 0.4, 0.8))
    sticker(img, tr_upper('yine aynı!'), 540, 420, t, 0.3, rot=7)
    p = ease_back(prog(t, 1.0, 0.3))
    if p > 0: draw_emoji(img, '🟰', 540, 790, 90, scale=p)

VIDEOS['v2'] = dict(category='beyin yakan', seed=2, scenes=lambda: [
    Scene(A + 'v2_s0.wav', ['*Şekerim,*', 'sana basit bir soru.', 'Bu iki çizgiden hangisi', 'daha *uzun?*', 'Hemen cevap ver,', '*düşünme!*'], v2_s0),
    Scene(A + 'v2_s1.wav', ['Üstteki dedin,', 'değil mi?', '*Ayol,* ikisi de', '*aynı* *boyda!*', 'Bak, okları siliyorum.'], v2_s1, expr=lambda t: 'shock' if 1.2 < t < 2.6 else 'sass'),
    Scene(A + 'v2_s2.wav', ['Beynin okların yönüne bakıp', 'sana *yalan* söylüyor.', 'Tıpkı *5* *dakikaya* *çıkıyorum*', 'diyen arkadaşın gibi!'], v2_s2, expr='smug'),
    Scene(A + 'v2_s3.wav', ['Şimdi *ikinci* soru.', 'Ortadaki *turuncu* dairelerden', 'hangisi daha *büyük?*', 'Sol mu, sağ mı?'], v2_s3),
    Scene(A + 'v2_s4.wav', ['Yine *aynı!*', 'Kızım bugün gözlerine', 'hiç *güvenme.*', 'Kaçında kandın?', 'Yorumlara yaz, *öptüm!*'], v2_s4),
])

# ======================= VİDEO 3: Hangisini seçerdin (absürt) =======================
def card(img, t, t_in, box, color, fg, letter, emoji, label, from_left=True, pulse=0.0):
    p = ease_out(prog(t, t_in, 0.45))
    if p <= 0: return
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    S = 2; L = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], 46 * S, fill=WHITE + (255,))
    d.rounded_rectangle([10 * S, 10 * S, w * S - 10 * S, h * S - 10 * S], 38 * S, fill=color + (255,))
    # harf rozeti
    d.ellipse([34 * S, 34 * S, 124 * S, 124 * S], fill=WHITE + (255,))
    f = font(64 * S, 'Black'); lw = text_w(letter, f)
    d.text((79 * S - lw / 2, 38 * S), letter, font=f, fill=color + (255,))
    # etiket
    fl = font(54 * S, 'Black'); words = tr_upper(label).split(); lines = ['']
    for wd in words:
        if text_w((lines[-1] + ' ' + wd).strip(), fl) > 500 * S: lines.append(wd)
        else: lines[-1] = (lines[-1] + ' ' + wd).strip()
    ty = h * S / 2 - len(lines) * 66 * S / 2
    for i, ln in enumerate(lines):
        d.text((330 * S, ty + i * 66 * S), ln, font=fl, fill=fg + (255,))
    L = L.resize((w, h), Image.LANCZOS)
    e = emoji_img(emoji, 160)
    L.alpha_composite(e, (int(225 - e.width / 2), int(h / 2 - e.height / 2)))
    dx = (1 - p) * (-W if from_left else W)
    sc = 1 + 0.05 * pulse
    paste_center(img, L, x0 + w / 2 + dx, y0 + h / 2, scale=sc, rot=(-2 if from_left else 2) * (1 - p))

def vs(img, t, t_in):
    p = ease_back(prog(t, t_in, 0.35))
    if p <= 0: return
    S = 2; L = Image.new('RGBA', (180 * S, 180 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse([0, 0, 180 * S - 1, 180 * S - 1], fill=INK + (255,)); d.ellipse([10 * S, 10 * S, 170 * S, 170 * S], fill=WHITE + (255,))
    f = font(70 * S, 'Black'); w = text_w('VS', f); d.text((90 * S - w / 2, 42 * S), 'VS', font=f, fill=INK + (255,))
    paste_center(img, L.resize((180, 180), Image.LANCZOS), 540, 625, scale=p, rot=10 * math.sin(t * 3))

BOX_A = (70, 275, 1010, 585); BOX_B = (70, 665, 1010, 975)

def dilemma(a_emoji, a_label, b_emoji, b_label, pulse_b_after=None):
    def f(img, t, sc):
        card(img, t, 0.05, BOX_A, PINK, WHITE, 'A', a_emoji, a_label, True)
        pb = 0
        if pulse_b_after is not None and t > pulse_b_after: pb = max(0, math.sin((t - pulse_b_after) * 8))
        card(img, t, 0.25, BOX_B, GOLD, INK, 'B', b_emoji, b_label, False, pulse=pb)
        vs(img, t, 0.6)
    return f

def v3_s0(img, t, sc):
    big_title(img, ['sadece', 'birini', 'seç!'], t, 0.1, y=500, colors=[WHITE, GOLD, PINK], size=124)
    sticker(img, 'AYOL!', 220, 320, t, 0.05, rot=-10)
    draw_emoji(img, '⚖️', 860, 330, 140, scale=ease_back(prog(t, 0.4, 0.4)), rot=10 * math.sin(t * 2.5))

_conf_rng = np.random.default_rng(3)
CONF = [(_conf_rng.uniform(-1, 1), _conf_rng.uniform(-1.6, -0.4), _conf_rng.choice(6), _conf_rng.uniform(0, 6)) for _ in range(60)]
def v3_s2(img, t, sc):
    dilemma('🎊', 'Hapşırınca konfeti', '👏', 'Gülünce alkış')(img, t, sc)
    t0 = 1.6
    if t > t0:
        tt = t - t0; d = ImageDraw.Draw(img)
        cols = [PINK, GOLD, (90, 200, 255), (120, 230, 140), WHITE, PINK_L]
        for vx, vy, ci, ph in CONF:
            x = 260 + vx * 600 * tt; y = 430 + vy * 900 * tt + 900 * tt * tt
            if y > 1900: continue
            s = 14; a = ph + tt * 8
            pts = [(x + s * math.cos(a + k * math.pi / 2), y + s * 0.6 * math.sin(a + k * math.pi / 2)) for k in range(4)]
            d.polygon(pts, fill=cols[ci] + (255,))

def v3_s3(img, t, sc):
    dilemma('🎤', 'Sadece şarkıyla konuşmak', '💅', "Her cümle 'ayol' ile biter", pulse_b_after=sc.vdur - 2.4)(img, t, sc)
    sticker(img, tr_upper('zaten yapıyorum!'), 600, 625, t, sc.vdur - 2.2, rot=-6, size=56)

def v3_s4(img, t, sc):
    big_title(img, ["aykut'un", 'cevapları'], t, 0.0, y=330, size=92, colors=[WHITE, GOLD])
    for k, (n, ans, col) in enumerate([(1, 'B', GOLD), (2, 'A', PINK), (3, 'B', GOLD)]):
        chip(img, f'{n}  →  {ans}', 540, 600 + k * 115, t, 1.0 + k * 0.45, bg=col, fg=(INK if col == GOLD else WHITE), size=58)

VIDEOS['v3'] = dict(category='seç bakalım', seed=3, scenes=lambda: [
    Scene(A + 'v3_s0.wav', ['*Ayol,*', 'hayatının kararını vereceksin.', 'Sadece *birini* seçebilirsin.', 'Hazır mısın?'], v3_s0),
    Scene(A + 'v3_s1.wav', ['Bir: Ömür boyu her şeyi', '*fısıldayarak* mı konuşmak,', 'yoksa her şeyi', '*bağırarak* mı söylemek?'],
          dilemma('🤫', 'Ömür boyu fısıldamak', '📢', 'Ömür boyu bağırmak')),
    Scene(A + 'v3_s2.wav', ['İki: Her hapşırdığında', 'etrafa *konfeti* mi saçılsın,', 'yoksa her güldüğünde', 'arkadan *alkış* sesi mi gelsin?'], v3_s2),
    Scene(A + 'v3_s3.wav', ['Üç: Bir hafta boyunca', 'sadece *şarkı* söyleyerek mi konuşmak,', 'yoksa her cümlenin sonuna', '*ayol* demek zorunda olmak mı?', 'Ben ikinciyi zaten yapıyorum,', '*ayol!*'], v3_s3,
          expr=lambda t: 'smug' if t > 6.8 else 'sass'),
    Scene(A + 'v3_s4.wav', ['Benim cevaplarım:', '*B,* *A* ve tabii ki *B.*', 'Seninkiler ne?', 'Yorumlara yaz, *öptüm!*'], v3_s4),
])

if __name__ == '__main__':
    name, mode = sys.argv[1], sys.argv[2]
    v = VIDEOS[name]; scenes = v['scenes']()
    if mode == 'preview':
        import engine
        t0s = np.cumsum([0] + [s.dur for s in scenes]); total = t0s[-1] + 1.3
        scenes[-1].dur += 1.3
        shots = []
        for si, sc in enumerate(scenes):
            for frac in (0.55,):
                fi = int(sc.dur * frac * FPS); shots.append(engine.frame(sc, si, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        fi = int((scenes[-1].dur - 0.4) * FPS); shots.append(engine.frame(scenes[-1], len(scenes) - 1, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        sheet = Image.new('RGB', (360 * len(shots), 640))
        for i, s in enumerate(shots): sheet.paste(s.convert('RGB').resize((360, 640)), (360 * i, 0))
        sheet.save(f'out/{name}_sheet.jpg', quality=85)
        print([round(s.dur, 2) for s in scenes], round(sum(s.dur for s in scenes), 1))
    else:
        print(render_video(name, v['category'], scenes, music_seed=v['seed']))
