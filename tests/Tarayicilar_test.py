import pyscreeze

from moe_bot.tarayicilar import Kare, PyAutoTarayici
from moe_bot.temel_siniflar import GelismisKare

# write test that screenshot some part of screen and check with tarayici to if it finds it


def test_pyauto_tarayici():
    screen_shot = pyscreeze.screenshot(region=(0, 0, 100, 100))
    tarayici = PyAutoTarayici(
        gorsel_d=screen_shot,
        eminlik=0.8,
        konum=Kare(0, 0, 100, 100),
        gri_tarama=False,
        isim="test_tarayici",
    )
    tarama_sonucu = tarayici.ekranTara()
    assert tarama_sonucu is not None
    assert not GelismisKare(0, 0, 100, 100).disindaMi(tarama_sonucu)
