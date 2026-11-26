# Günlük üretim talimatı (zamanlanmış görevler için)

Her slotta bir video üretilir ve Instagram'a paylaşılır. Önce oku: `STIL.md` (tarz), `OGRENIMLER.md` (büyüme kuralları + format rotasyonu), `PERFORMANS.md` (geçmiş sonuçlar), `KONULAR.md` (tekrar etme).

## 0. Ölç ve öğren (her görevin ilk işi)
1. Windsor `get_data`: connector `instagram`, `date_preset: "last_30dT"`, fields:
   `["media_id","timestamp","media_views","media_reach","media_reel_avg_watch_time","media_reel_skip_rate","media_total_like_count","media_total_comments_count","media_shares","media_saved"]`
   (`force_refresh` ve `media_reposts` kullanma; bu hesapta desteklenmiyor.)
2. `PERFORMANS.md` tablosunu güncelle: her media id için izlenme, erişim, ort. izlenme süresi (sn), 3 sn'de geçme oranı, beğeni, yorum, paylaşım, kaydetme ve **skor** = izlenme × (1 + 5·paylaşım/izlenme + 3·kaydetme/izlenme). Format ve konu bilgisini `KONULAR.md`'den eşle. 24 saatten yeni videolarda veriler eksik olabilir; yine de yaz.
3. Formata göre ortalamaları karşılaştır. Net bir örüntü görürsen (örn. "Neden…? videoları 2 kat izleniyor", "geçme oranı 4 sn'den uzun girişlerde yüksek") `OGRENIMLER.md` → "Kendi verilerimizden" bölümüne tarihli tek satır ekle. Format rotasyonu kuralını uygula.

## 1. Konu seç
`OGRENIMLER.md` format rotasyonuna göre bu slotun formatını belirle. En iyi skorlu videoların konu tipine yakın, ama `KONULAR.md`'de olmayan bir konu seç. Gündelik/kişisel konuları tercih et. Bilgi içeren videolarda doğruluğundan emin olmadığın bilgiyi kullanma; gerekirse web'de doğrula.

## 2. Senaryo yaz
20–35 sn, 4–5 sahne. İlk cümle kanca (soru/iddia, ekranda büyük yazıyla). Aykut'un diva ağzıyla ("ayol", "şekerim", "kızım"), dramatik kişisel tepkiler. Kapanış: "...Bunu [kişi tipi] arkadaşına gönder, öptüm!" ya da "...Yorumlara yaz, öptüm!". Sayıları yazıyla yaz.

## 3. Seslendir
Her sahne için ayrı Speko `audio.synthesize`:
`{"text": ..., "intent": {"language": "tr"}, "voice": "91e91d74-8eb4-43cd-97d3-7466c21db00d", "speed": 1.1, "constraints": {"allowedProviders": {"tts": ["cartesia"]}}}`
Dönen wav dosyalarını `audio/<id>_s0.wav` … olarak kopyala.

## 4. Görselleri yaz
`videos.py` kalıbıyla kökte yeni dosya (örn. `gun_2026-11-27_11.py`): `from engine import *`, sahne başına görsel fonksiyonu (`big_title`, `badge`, `chip`, `sticker`, `draw_emoji`, kendi çizimlerin), `Scene(wav, altyazı_öbekleri, görsel, expr=...)`. Altyazı öbekleri 2–5 kelime, vurgu `*kelime*`. İçerik alanı y=260–960, altyazı ~1010, Aykut sol altta. Kanca sahnesinde başlık 0,1 sn'de görünür olsun.

## 5. Önizle, kontrol et, geliştir
`python3 <dosya> <id> preview` → `out/<id>_sheet.jpg` dosyasını Read ile aç; çakışma, taşma, yazım hatası varsa düzelt. Her videoda en az bir yeni görsel fikir dene (yeni animasyon, yeni çizim, yeni geçiş) ve işe yarayanı `engine.py`'ye yardımcı fonksiyon olarak ekle.

## 6. Render
`python3 <dosya> <id> render` → `out/<id>.mp4`. ffprobe ile süre 20–60 sn ve ses akışı kontrolü.

## 7. Yayınla
`media/<tarih>/<slot>_<kısa-ad>.mp4` olarak kopyala; senaryo dosyası, `engine.py` değişiklikleri ve md güncellemeleriyle commit + push (`main`).

## 8. Paylaş
Windsor `execute_action`: connector `instagram`, account `17841480889670167`, action `create_video_post`, params:
`{"video_url": "https://raw.githubusercontent.com/uzumakishounen-lab/aykutdiva-depo/main/media/<tarih>/<dosya>.mp4", "caption": ..., "share_to_feed": true, "thumb_offset": <başlığın tam göründüğü ms, genelde 1200–1800>}`
Açıklama kalıbı:
```
<Merak cümlesi / iddia> <emoji>
<1 cümle ek bilgi ya da Aykut esprisi>

👉 Bunu <belirli kişi tipi> arkadaşına gönder.
Öptüm 💋 Daha fazlası için takip et.

#<konu> #<konu> #ilginçbilgiler #keşfet
```

## 9. Tohum yorum
Paylaşımdan hemen sonra Windsor `execute_action` action `create_comment`, params `{"media_id": <yeni id>, "message": "<izleyiciye kişisel soru> Dürüst ol şekerim 👇"}`.

## 10. Kaydet
`KONULAR.md`'ye tarih, slot, format, konu, media id ekle; commit + push.

## Sınırlar
- Başkasının videosunu, müziğini, karakterini kullanma; her şey özgün üretim.
- Gerçek kişileri, siyasi/dini tartışmaları, şiddet ve müstehcenliği konu alma. "Bunu dene" meydan okumaları zararsız olmalı (acı, risk, tehlike yok).
- Mizah Aykut'un diva tavrından gelir; hiçbir grupla alay etme.
- Paylaşım başarısız olursa bir kez yeniden dene; yine olmazsa hatayı raporla.
