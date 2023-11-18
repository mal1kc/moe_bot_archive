## düzeltildi

- d(durma) 'durumunda cpu kullanımı %10 - %20 değerlerine çıkıyor ( çalışma sırasında %1-%2 ) (çözüldü)
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
- arayuz: beni hatirla (exe ye çevirildiğindde çalışcakmı)

## FIXME Sorunlar

- tüm çözünürlüklerde de daha çok test and foto optimizasyonu +

## TODO eksikler

- oturum yenileme hatası alınırsa ne yapılacak?
    + geçici çözüm olarak k.hata fırlatılacak ve program kapatılacak
- durma durumunda giriş yenileme yapılacak mı?
    + geçici çözüm olarak hiçbir şey yapılmayacak

- çoklu dil desteği
  - görsellerde dil desteği
    + dile bağımlı görseller dile ait `imgs` alt klasörüne konulacak
    + dile bağımlı olmayan görseller `imgs` ' in altına no_lang klasörüne konulacak
    + eğer dil bağımlı ise `sabitler.TaramaSabitleri.GORSEL_YL_DIL_BEYANLARI` anahtar sözlüğüne True olarak eklenecek
    + olması beklenen dosya yapısı
    ```
    ├─ imgs/
    │  ├─ en/
	│  │  ├─ _1920/
	│  │  │  ├─ img_file.png
	│  │  ├─ _3840/
	│  │  │  ├─ img_file.png
	│  │  ├─ _1366/
	│  │  │  ├─ img_file.png
	│  ├─ tr/
	│  │  ├─ _1920/
	│  │  │  ├─ img_file.png
	│  │  ├─ _3840/
	│  │  │  ├─ img_file.png
    │  │  ├─ _1366/
    │  │  │  ├─ img_file.png
	│  ├─ no_lang/
	│  │  ├─ _1920/
	│  │  │  ├─ no_lang_img_file.png
	│  │  ├─ _3840/
    │  │  │  ├─ no_lang_img_file.png
    │  │  ├─ _1366/
    │  │  │  ├─ no_lang_img_file.png
    ```
