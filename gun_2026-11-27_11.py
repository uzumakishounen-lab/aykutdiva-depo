import sys, math
from PIL import Image, ImageDraw
from engine import *

A = 'audio/'

def s0(img, t, sc):
    big_title(img, ['bu videoda', 'esneyeceksin'], t, 0.1, y=470, size=110, colors=[WHITE, PINK])
    sticker(img, 'AYOL!', 830, 300, t, 0.05, rot=10)
    draw_emoji(img, '🥱', 540, 745, 180, scale=ease_back(prog(t, 0.4, 0.45)), rot=7 * math.sin(t * 2.5))
    chip(img, tr_upper('iddiaya var mısın?'), 540, 895, t, 2.6, bg=GOLD)

def s1(img, t, sc):
    chip(img, tr_upper('esneme bulaşıcı'), 540, 330, t, 0.1, bg=PINK, fg=WHITE, size=56)
    domino_emojis(img, t, 0.3, '😐', '🥱', n=5, cy=560, size=150)
    for k, (e, lab) in enumerate([('👀', 'görmek'), ('👂', 'duymak'), ('📖', 'okumak')]):
        tin = 2.0 + k * 1.2
        p = ease_back(prog(t, tin, 0.35))
        if p > 0:
            x = 220 + k * 320
            draw_emoji(img, e, x, 760, 120, scale=p)
            chip(img, tr_upper(lab), x, 880, t, tin + 0.1, bg=GOLD if k != 2 else PINK, fg=INK if k != 2 else WHITE, size=40)

def s2(img, t, sc):
    draw_emoji(img, '🧠', 540, 520, 250, scale=ease_back(prog(t, 0.05, 0.45)), rot=6 * math.sin(t * 2.5))
    chip(img, tr_upper('taklit + empati'), 540, 710, t, 1.0, bg=PINK, fg=WHITE)
    p = ease_back(prog(t, 4.2, 0.4))
    if p > 0:
        beat = 1 + 0.1 * max(0, math.sin(t * 7)) ** 6
        draw_emoji(img, '💞', 540, 830, 110, scale=p * beat)
    chip(img, tr_upper('yakınlarından daha çok'), 540, 910, t, 4.6, bg=GOLD, size=44)

def s3(img, t, sc):
    sticker(img, tr_upper('asıl şok'), 540, 310, t, 0.05, rot=-6, size=60)
    draw_emoji(img, '🐶', 360, 600, 230, scale=ease_back(prog(t, 1.3, 0.45)), rot=6 * math.sin(t * 2.2))
    p = ease_back(prog(t, 2.6, 0.35))
    if p > 0: draw_emoji(img, '🥱', 560, 470, 110, scale=p, rot=-10)
    cat_in = sc.vdur - 3.2
    q = ease_back(prog(t, cat_in, 0.4))
    if q > 0:
        draw_emoji(img, '🐱', 800, 680, 170, scale=q, rot=-6 * math.sin(t * 2))
        draw_emoji(img, '🙄', 900, 560, 90, scale=ease_back(prog(t, cat_in + 0.4, 0.3)))
    chip(img, tr_upper('köpekler de kapıyor'), 540, 870, t, 2.2, bg=GOLD)

def s4(img, t, sc):
    big_title(img, ['esnedin mi?'], t, 0.05, y=420, size=118, colors=[GOLD])
    draw_emoji(img, '🥱', 380, 700, 170, scale=ease_back(prog(t, 0.5, 0.35)), rot=6 * math.sin(t * 3))
    draw_emoji(img, '💬', 700, 700, 150, scale=ease_back(prog(t, 1.2, 0.35)), rot=-6 * math.sin(t * 3))
    chip(img, tr_upper('yorumlara yaz'), 540, 880, t, 1.4, bg=PINK, fg=WHITE)

VIDEOS = {}
VIDEOS['a27'] = dict(category='neden?', seed=4, scenes=lambda: [
    Scene(A + 'a27_s0.wav', ['*Ayol* dur!', 'Bu videoyu izlerken', '*esneyeceksin.*', 'İddiaya girelim mi *şekerim?*'], s0, expr='smug'),
    Scene(A + 'a27_s1.wav', ['Esneme *bulaşıcıdır* kızım.', 'Birinin esnediğini *görmek,*', '*duymak,*', 'hatta sadece esneme', 'kelimesini *okumak* bile', 'seni esnetebiliyor.'], s1),
    Scene(A + 'a27_s2.wav', ['Bilim insanları bunu', 'beynin *taklit* sistemine', 've *empatiye* bağlıyor.', 'Hatta sevdiğin, *yakın*', 'olduğun insanların esnemesi', 'sana *daha* *çok* bulaşıyormuş.'], s2),
    Scene(A + 'a27_s3.wav', ['Asıl *şoku* söyleyeyim mi?', '*Köpekler* bile', 'sahiplerinden esneme', '*kapabiliyor.*', 'Benim kedim ise', 'beni hiç *umursamıyor,* ayol!'], s3,
          expr=lambda t: 'shock' if 1.2 < t < 3.5 else 'sass'),
    Scene(A + 'a27_s4.wav', ['E, *esnedin* mi?', 'Dürüst ol, yorumlara yaz.', 'Bunu sürekli *esneyen*', 'arkadaşına gönder, *öptüm!*'], s4),
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
            for frac in (0.3, 0.8):
                fi = int(sc.dur * frac * FPS); shots.append(engine.frame(sc, si, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        fi = int(1.5 * FPS); shots.insert(0, engine.frame(scenes[0], 0, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        sheet = Image.new('RGB', (270 * len(shots), 480))
        for i, s in enumerate(shots): sheet.paste(s.convert('RGB').resize((270, 480)), (270 * i, 0))
        sheet.save(f'out/{name}_sheet.jpg', quality=85)
        print([round(s.dur, 2) for s in scenes], round(sum(s.dur for s in scenes), 1))
    else:
        print(render_video(name, v['category'], scenes, music_seed=v['seed']))
