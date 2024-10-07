import pyscreeze

from moe_bot.tarayicilar import Kare, PyAutoTarayici, SiraliPyAutoTarayici
from moe_bot.temel_siniflar import GelismisKare, IsimliDizi

# write test that screenshot some part of screen and check with tarayici to if it finds it


def test_pyauto_tarayici():
    screen_shot = pyscreeze.screenshot(region=(0, 0, 100, 100))
    tarayici = PyAutoTarayici(
        isim="test_tarayici",
        gorsel_yollari=(screen_shot,),
        eminlikler=(0.8,),
        konum=Kare(0, 0, 100, 100),
        gri_tarama=False,
    )
    tarama_sonucu = tarayici.ekranTara()
    assert tarama_sonucu is not None
    assert not GelismisKare(0, 0, 100, 100).disindaMi(tarama_sonucu)


def test_pyauto_tarayici_gri_tarama():
    screen_shot = pyscreeze.screenshot(region=(0, 0, 100, 100))
    tarayici = PyAutoTarayici(
        isim="test_tarayici",
        gorsel_yollari=(screen_shot,),
        eminlikler=(0.8,),
        konum=Kare(0, 0, 100, 100),
        gri_tarama=True,
    )
    tarama_sonucu = tarayici.ekranTara()
    assert tarama_sonucu is not None
    assert not GelismisKare(0, 0, 100, 100).disindaMi(tarama_sonucu)


def test_sirali_pyauto_tarayici():
    screen_shot = pyscreeze.screenshot(region=(0, 0, 100, 100))
    gorsel_yollari_idizi = IsimliDizi(isim="ekran_g", dizi=(screen_shot,))

    tarayici = SiraliPyAutoTarayici(
        isimli_gorsel_yollari=gorsel_yollari_idizi, isim="test_pyautoSiraliTarayici", bolge=None, eminlik=0.8, gri_tarama=False
    )
    tarama_sonucu = tarayici.ekranTara()

    assert tarama_sonucu is not None
    assert not GelismisKare(0, 0, 100, 100).disindaMi(tarama_sonucu[1])
    assert tarama_sonucu[0] == "ekran_g"
