import sys, math
from PIL import Image, ImageDraw
from engine import *
from videos import card, vs, dilemma, BOX_A, BOX_B

A = 'audio/'


def s0(img, t, sc):
    big_title(img, ['hangisi', 'daha kötü?'], t, 0.1, y=430, size=118, colors=[WHITE, PINK])
    sticker(img, 'AYOL!', 220, 300, t, 0.05, rot=-10)
    draw_emoji(img, '🪫', 360, 760, 160, scale=ease_back(prog(t, 0.4, 0.45)), rot=8 * math.sin(t * 3))
    draw_emoji(img, '🧦', 720, 760, 160, scale=ease_back(prog(t, 0.6, 0.45)), rot=-8 * math.sin(t * 3))
    chip(img, tr_upper('sadece birini seç'), 540, 930, t, 2.6, bg=GOLD)

def s3(img, t, sc):
    dilemma('🪨', 'Ayakkabında ömür boyu taş', '🧦', 'Çorabın hep hafif ıslak')(img, t, sc)
    sticker(img, tr_upper('ikisi de kâbus!'), 600, 625, t, sc.vdur - 2.6, rot=-6, size=56)

def s4(img, t, sc):
    big_title(img, ["aykut'un", 'cevapları'], t, 0.0, y=330, size=92, colors=[WHITE, GOLD])
    for k, (ans, col, fg) in enumerate([('A', PINK, WHITE), ('B', GOLD, INK), ('A', PINK, WHITE)]):
        answer_bar(img, str(k + 1), ans, 540, 600 + k * 125, t, 1.0 + k * 0.45, color=col, fg=fg)
    chip(img, tr_upper('seninkiler? yorumlara!'), 540, 950, t, 3.4, bg=WHITE, fg=INK, size=44)

VIDEOS = {}
VIDEOS['s27'] = dict(category='seç bakalım', seed=11, scenes=lambda: [
    Scene(A + 's27_s0.wav', ['*Ayol,*', 'bu akşam seni çok zor', 'bir *seçim* bekliyor.', 'Sadece *birini* seçebilirsin', '*şekerim.* Hazır mısın?'], s0, expr='smug'),
    Scene(A + 's27_s1.wav', ['Bir: Telefonunun şarjı', 'hep *yüzde* *bir* mi kalsın,', 'yoksa internetin hep', '*tek* *çizgi* mi çeksin?'],
          dilemma('🪫', 'Şarj hep yüzde bir', '📶', 'İnternet hep tek çizgi')),
    Scene(A + 's27_s2.wav', ['İki: Yazdığın her mesaj', '*annene* de mi gitsin,', 'yoksa her sesli mesajın', 'herkesin içinde', '*hoparlörden* mi çalsın?'],
          dilemma('📩', 'Her mesaj annene de gider', '🔊', 'Sesli mesajlar hoparlörden')),
    Scene(A + 's27_s3.wav', ['Üç: Ayakkabında ömür boyu', 'küçük bir *taş* mı olsun,', 'yoksa çorabın hep', 'hafif *ıslak* mı kalsın?', '*Kızım* ikisi de kâbus,', 'bayılıyorum *şu* *an!*'], s3,
          expr=lambda t: 'shock' if t > 5.6 else 'sass'),
    Scene(A + 's27_s4.wav', ['Benim cevaplarım:', '*A,* *B* ve tabii ki *A.*', 'Seninkiler ne?', 'Yorumlara yaz,', 'bunu hiç karar veremeyen', 'arkadaşına gönder, *öptüm!*'], s4),
])

if __name__ == '__main__':
    name, mode = sys.argv[1], sys.argv[2]
    v = VIDEOS[name]; scenes = v['scenes']()
    if mode == 'preview':
        import engine
        t0s = np.cumsum([0] + [s.dur for s in scenes]); total = t0s[-1] + 1.3
        scenes[-1].dur += 1.3
        shots = []
        fi = int(1.5 * FPS); shots.append(engine.frame(scenes[0], 0, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        for si, sc in enumerate(scenes):
            for frac in (0.85,):
                fi = int(sc.dur * frac * FPS); shots.append(engine.frame(sc, si, len(scenes), fi, t0s, total, v['category'], 'ÖPTÜM'))
        sheet = Image.new('RGB', (360 * len(shots), 640))
        for i, s in enumerate(shots): sheet.paste(s.convert('RGB').resize((360, 640)), (360 * i, 0))
        sheet.save(f'out/{name}_sheet.jpg', quality=85)
        print([round(s.dur, 2) for s in scenes], round(sum(s.dur for s in scenes), 1))
    else:
        print(render_video(name, v['category'], scenes, music_seed=v['seed']))
