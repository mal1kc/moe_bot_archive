## düzeltildi

- _1920 ve _1366 bölge değişmiyor ++
    -> eğer ekranda bul ikonunu bulamazsa bölgeyi değişemiyor
        buda sonsuz boş ekranda bul ikonu taramasına neden oluyor
- x ile kapatmada tam kapanmıyor
- kaynak tipine ait 1 tane kaynak bulduğunda taramayı sonlandırıyor (çözüldü)
- arayuz checkbox tiki kaldırılsada aktif kalıyor
- kaynak tiklama bozuldu (şüphelenilen bolum => kisitli_bolgeler) (çözüldü -> kistli_bolgeri tespiti düzeltildi )
- başlangıçta konsol ekranı (bilgilendirme kısayol tuşları) (exe ye çevirildiğindde çalışcakmı)
- engeltarayici - devre dışı bırakıldı ( düzenlenecek | yeterince stabil değil )
    - s , d
    - baglanti kesilmesi
        - tekrar deneye basıp moe logosnun kaybolmasını beklicek
    - baska cihaz baglandı
        - kendini kapatsin ****
    - yukleme ekranına gelirse moe logosnun kaybolmasını beklicek
- kaynağa ait svy görsellerini kullanabiliyor
    > odun svy * için -> `o_svy_*.png`
    - eğer bulamazsa svy_*.png kullanıyor
## eklendi

- 1920 ve 1366 için resimler eklencek min 3'er tane
- Koordinat değiştirme ( bul )
- tarama_bölgesi, tıklama_sabiti oranlama
- başlatma bitirme tuşarı
- ana islem sinifi
- basit log
- - bölge kısıtlamaları
    - eğer seferlerin arkasındaysa;
        1 - seferler açıksa
        2 - x: 250 < x < 1150
            "z" bas, kaynak tıkla
    - y > 1630 ise tıklama yapma (ölü bölge)
    - x > 3600 ise tıklama yapma (ölü bölge)
- çözünürlük bazli templateler
- çözünürlük bazli bölgeler
- arayüz , yapıldı birleştirilcek
- tarama sefer doıluysa yapılmasın ( önce sefer tarama)
- testler yeniden yazılacak ve düzenlenecek (yapıldı)

- kullanılacak modul secim arayüzü (yapıldı)
- sunucu entegrasyonu (yapıldı)
- temel sunucu bağlantısı (yapıldı)
- login arayüzü (yapıldı)

## eklendi - test edilecek


## FIXME Sorunlar

- tüm çözünürlüklerde de daha çok test and foto optimizasyonu +
- confidence değerlerinin hepsi ayarlardan alınmıyor

## TODO eksikler

- cprofile ile performans testi yapılacak ve pympler ile memory testi yapılacak
    + minimum 10 sefer
- ayarlar modul secildiğinde yüklenicek (ayarlar modulu) (%50) (karalamada)
- daha moduler özellikler (feauture)
    - moe_gatherer (sonradan modulerleştirilecek)
    - moe_advantures (sonra)
    - moe_camp (sonra)
    - moe_raid (sonra)

## olsa güzel olur

- günlükçü ->  init ve tanımlamalarda günlükçünün kulannımı farklı olucak
- siniflari tiplerine göre dosyalara konulabilir
- pynput controller --> rlock oluşturduğundan (rlock pickle edilemiyor) kaldırılmıştı
- daha anlaşılabilir hale getirilecek
- arayüzde resim yok (resim gözükmüyor)
