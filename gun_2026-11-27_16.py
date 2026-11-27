import sys, math
from PIL import Image, ImageDraw
from engine import *

A = 'audio/'


def s0(img, t, sc):
    big_title(img, ['bunu kimse', 'yapamıyor!'], t, 0.1, y=430, size=118, colors=[WHITE, PINK])
    sticker(img, 'AYOL!', 840, 300, t, 0.05, rot=10)
    draw_emoji(img, '🦶', 400, 760, 170, scale=ease_back(prog(t, 0.4, 0.45)), rot=8 * math.sin(t * 3))
    draw_emoji(img, '✋', 690, 740, 160, scale=ease_back(prog(t, 0.6, 0.45)), rot=-8 * math.sin(t * 3))
    chip(img, tr_upper('iddiaya var mısın?'), 540, 910, t, 2.6, bg=GOLD)

def s1(img, t, sc):
    badge(img, 1, t, cx=180, cy=330)
    chip(img, tr_upper('sağ ayak'), 560, 330, t, 0.2, bg=PINK, fg=WHITE, size=56)
    spin_ring(img, 540, 640, 200, t, 1.2, direction=1, speed=3.2)
    draw_emoji(img, '🦶', 540, 640, 170, scale=ease_back(prog(t, 1.4, 0.4)), rot=10 * math.sin(t * 3.2))
    chip(img, tr_upper('saat yönünde'), 540, 910, t, 2.4, bg=GOLD)

def s2(img, t, sc):
    badge(img, 2, t, cx=180, cy=330)
    chip(img, tr_upper('sağ el'), 560, 330, t, 0.2, bg=PINK, fg=WHITE, size=56)
    spin_ring(img, 300, 780, 110, t, 0.3, direction=1, speed=3.2, width=12)
    draw_emoji(img, '🦶', 300, 780, 100, scale=ease_back(prog(t, 0.4, 0.4)))
    trace_path(img, six_path(700, 640, 1.0), t, 1.6, 2.2)
    draw_emoji(img, '✍️', 880, 470, 110, scale=ease_back(prog(t, 1.2, 0.4)), rot=10 * math.sin(t * 4))
    chip(img, tr_upper('havaya 6 yaz'), 540, 930, t, 1.3, bg=GOLD)

def s3(img, t, sc):
    sticker(img, tr_upper('yön değişti!'), 540, 320, t, 0.05, rot=-6, size=60)
    spin_ring(img, 540, 600, 190, t, 0.3, direction=1, speed=3.2, flip_at=1.4, color=PINK)
    draw_emoji(img, '🦶', 540, 600, 150, scale=ease_back(prog(t, 0.4, 0.4)))
    draw_emoji(img, '😵‍💫', 820, 470, 110, scale=ease_back(prog(t, 1.6, 0.35)))
    p = ease_back(prog(t, 3.0, 0.45))
    if p > 0:
        draw_emoji(img, '🧠', 300, 470, 120, scale=p, rot=6 * math.sin(t * 3))
    chip(img, tr_upper('beyin karışıyor'), 540, 880, t, 3.2, bg=GOLD)

def s4(img, t, sc):
    big_title(img, ['başardın mı?'], t, 0.05, y=420, size=112, colors=[GOLD])
    draw_emoji(img, '✅', 380, 700, 160, scale=ease_back(prog(t, 0.5, 0.35)), rot=6 * math.sin(t * 3))
    draw_emoji(img, '❌', 700, 700, 160, scale=ease_back(prog(t, 0.8, 0.35)), rot=-6 * math.sin(t * 3))
    chip(img, tr_upper('yorumlara yaz'), 540, 880, t, 1.4, bg=PINK, fg=WHITE)

VIDEOS = {}
VIDEOS['b27'] = dict(category='bunu dene', seed=7, scenes=lambda: [
    Scene(A + 'b27_s0.wav', ['*Ayol* dur!', 'Bunu *kimse* yapamıyor.', 'Sen de yapamayacaksın', '*şekerim,* iddiaya varım!'], s0, expr='smug'),
    Scene(A + 'b27_s1.wav', ['Otur kızım.', '*Sağ* ayağını kaldır', 've *saat* *yönünde*', 'daireler çiz.', 'Durmak *yok!*'], s1),
    Scene(A + 'b27_s2.wav', ['Şimdi ayağın dönerken,', '*sağ* elinle havaya', '*altı* rakamını yaz.', 'Hadi, *hadi!*'], s2),
    Scene(A + 'b27_s3.wav', ['Ne oldu?', 'Ayağın *yön* *değiştirdi,*', 'değil mi?', 'Beyin aynı taraftaki', 'el ve ayağı *ters* yönlere', 'döndürmekte *zorlanıyor.*', 'Ben bile yapamadım', '*ayol,* ben!'], s3,
          expr=lambda t: 'shock' if t < 2.5 else ('smug' if t > 7 else 'sass')),
    Scene(A + 'b27_s4.wav', ['*Başarabildin* mi?', 'Dürüst ol, *yorumlara* yaz.', 'Bunu her şeye *ben* *yaparım*', 'diyen arkadaşına gönder,', '*öptüm!*'], s4),
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
