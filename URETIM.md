# Günlük üretim talimatı (zamanlanmış görevler için)

Her slotta bir video üretilir ve Instagram'a paylaşılır. Tarz kuralları: `STIL.md`.

| Slot (İstanbul) | Format | Kategori etiketi |
|---|---|---|
| 11:00 | Şaşırtıcı bilgi (3 bilgi, sonuncusu en çarpıcı) | `şaşırtıcı bilgi` |
| 16:00 | Beyin yakan: göz yanılması / bilmece / mini test | `beyin yakan` |
| 20:00 | Seç bakalım (A/B ikilemi); 3 günde bir yerine absürt/saçma komik video | `seç bakalım` / `saçma ama gerçek` |

## Adımlar
1. **Konu seç.** `KONULAR.md` dosyasındaki eski konuları tekrarlama. Bilgi videolarında yalnızca doğruluğundan emin olduğun bilgileri kullan; şüpheliyse web'de doğrula.
2. **Senaryo yaz.** Toplam 30–40 sn, 5 sahne: kanca → 3 içerik sahnesi → kapanış. Aykut'un diva ağzıyla ("ayol", "şekerim", "kızım"), her bilgiye kendi hayatından dramatik bir tepki. Son sahne daima "...Yorumlara yaz, öptüm!" ile biter. Sayıları yazıyla yaz ("iki yüz kırk üç").
3. **Seslendir.** Her sahne için ayrı Speko `audio.synthesize` çağrısı:
   `{"text": ..., "intent": {"language": "tr"}, "voice": "91e91d74-8eb4-43cd-97d3-7466c21db00d", "speed": 1.1, "constraints": {"allowedProviders": {"tts": ["cartesia"]}}}`
   Dönen wav dosyalarını `audio/<id>_s0.wav` … olarak kopyala.
4. **Görselleri yaz.** `videos.py` kalıbını izleyerek kökte yeni bir dosya oluştur (örn. `gun_2026-11-27_11.py`): `from engine import *`, her sahne için bir görsel fonksiyonu (`big_title`, `badge`, `chip`, `sticker`, `draw_emoji`, kendi çizimlerin), `Scene(wav, altyazı_öbekleri, görsel, expr=...)`. Altyazı öbekleri 2–5 kelime, vurgulu kelimeler `*kelime*`. İçerik alanı y=260–960; altyazı ~1010; Aykut sol altta.
5. **Önizle ve kontrol et.** `python3 <dosya> <id> preview` → `out/<id>_sheet.jpg` dosyasını Read ile aç; üst üste binme, taşma, yanlış yazım varsa düzelt.
6. **Render.** `python3 <dosya> <id> render` → `out/<id>.mp4`. ffprobe ile süre 20–60 sn ve ses akışı var mı kontrol et.
7. **Yayınla.** Videoyu `media/<tarih>/<slot>_<kısa-ad>.mp4` olarak kopyala, senaryo dosyasıyla birlikte commit edip `main`'e push et.
8. **Paylaş.** Windsor `execute_action`: connector `instagram`, account `17841480889670167`, action `create_video_post`, params:
   `{"video_url": "https://raw.githubusercontent.com/uzumakishounen-lab/aykutdiva-depo/main/media/<tarih>/<dosya>.mp4", "caption": ..., "share_to_feed": true, "thumb_offset": 1500}`
   Açıklama: 1 kısa merak cümlesi + yorum çağrısı + "Öptüm 💋" + 3–5 etiket (#keşfet dahil).
9. **Kaydet.** `KONULAR.md` dosyasına tarih, slot, konu ve media id ekle; commit + push.

## Sınırlar
- Başkasının videosunu, müziğini, karakterini kullanma; her şey özgün üretim.
- Gerçek kişileri, siyasi/dini tartışmaları, şiddet ve müstehcenliği konu alma.
- Mizah Aykut'un diva tavrından gelir; hiçbir grupla alay etme.
- Paylaşım başarısız olursa bir kez yeniden dene; yine olmazsa hatayı raporla, başka yol deneme.
