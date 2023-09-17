from ayarlar import Ayarlar


AYAR = Ayarlar()
AYAR.ayarla(dil="tr", mod="moe_gatherer", ekran_boyutu=(1920, 1080))
print(AYAR.mod.gorseller)
