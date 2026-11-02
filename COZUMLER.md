# Çözümler — osym

> **Zor kazanılmış çözümler defteri.** Bir sorunu çözdükten sonra buraya yazılıp
> yazılmayacağının testi: *"Aynı sorun 3 ay sonra karşıma çıksa, çözümü yeniden
> bulmam ne kadar sürerdi?"*
>
> **Yazma:** tipo, eksik import, unutulmuş `await`, bilinen framework hatası — tek
> aramayla çıkan şeyler. Bunlar gürültüdür ve defteri okunmaz hale getirir.
>
> **Yaz:** standart dışı bir yöntem uygulandıysa · bariz çözümün neden işe yaramadığı ·
> bir aracın belgelenmemiş davranışı · bu projeye ya da ekosisteme özgü bir tuzak ·
> geri alınması pahalı bir karar.

## 02.11.2026 — GitHub, cron'u olan iş akışını 60 gün hareketsizlikten sonra tümden kapatıyor

**Belirti:** GitHub 26.10.2026'da *"osym iş akışı kapatıldı, gerekiyorsa yeniden aç"* bildirimi
gönderdi. `gh workflow list --all` → *veri ve model doğrulama*: `disabled_inactivity`. Depoda
bozulan bir şey yoktu; son commit 20.08.2026.

**Kök neden:** GitHub, **public** bir depoda `schedule:` tetiği olan iş akışını 60 gün commit
hareketsizliğinden sonra otomatik devre dışı bırakır. Kapanan şey yalnız cron **değil, iş
akışının tamamıdır** — `push` ve `pull_request` tetikleri de koşmaz. Yani "cron zaten
gereksizdi, önemsiz" demek yanlış sonuç verir: bir sonraki YKS'de veriyi güncellemek için
push yapıldığında doğrulama CI'ı **sessizce hiç koşmayacaktı**. Bu projede CI'ın asıl işi
`git diff --exit-code -- data/` ile üretimin belirlenimci olduğunu kanıtlamak; koşmazsa elle
düzenlenmiş ya da bozuk bir JSON fark edilmeden canlıya gider.

**Çözüm:** `schedule:` bloğu `.github/workflows/ci.yml`'den kaldırıldı (ek yerleştirme dönemi
kapandı, veri bir sonraki YKS'ye kadar sabit), iş akışı elle yeniden açıldı:

```bash
gh workflow enable 337978194      # ya da: gh workflow enable ci.yml
gh workflow list --all            # state artık "active" olmalı
```

Cron'u olmayan bir iş akışı hareketsizlikten **hiç** kapanmaz; push tetiği bir yıl sonra da
çalışır durumda kalır. Cron geri eklenecekse bu girdinin okunması gerekir.

**Neden bariz olan işe yaramadı:**
- *"Bildirimi yok say, siteyi etkilemiyor"* — doğru ama eksik. Site Vercel'de duruyor, CI ile
  ilgisi yok; kaybedilen şey bir sonraki veri güncellemesinin güvenlik ağıdır.
- *"`gh workflow enable` yeter"* — cron yerinde kalırsa 60 gün sonra aynı bildirim, aynı
  kapanma. Hareketsizlik beklenen durum olduğu için kalıcı çözüm cron'u kaldırmaktır.
- *"Durum `exit 0` / yeşil CI ile anlaşılır"* — anlaşılmaz: kapalı iş akışı hata vermez,
  hiç koşmaz. Tek güvenilir ölçüm `gh workflow list --all` çıktısındaki `state` alanıdır.

<!-- Yeni girişler EN ÜSTE eklenir (en yeni önce). Biçim:

## GG.AA.YYYY — <sorun tek cümlede>

**Belirti:** Ne görüldü — hata mesajı, yanlış çıktı ya da sessiz başarısızlık.
**Kök neden:** Belirtinin kendisi değil, altındaki gerçek sebep.
**Çözüm:** Ne yapıldı — `dosya:satır`, komut, ayar.
**Neden bariz olan işe yaramadı:** Denenip elenen yollar. Bu kısım defterin asıl değeridir;
boş bırakılırsa giriş büyük ölçüde anlamsızlaşır.

-->
