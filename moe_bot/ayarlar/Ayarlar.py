import dataclasses
from typing import Iterable


from moe_bot.temel_siniflar import Gorsel, Kare
from moe_bot.types import Any


# TODO : TarayiciAyarlari isimli siniflar namedTuple'a cevrilecek


@dataclasses.dataclass
class CokluOrnekTarayiciAyarlari:
    isim: str
    gorsel_yollari: list[Gorsel]
    eminlik: float
    konum: Kare | None
    gri_tarama: bool


@dataclasses.dataclass
class PyAutoTarayiciAyarlari:
    isim: str
    gorsel_yolu: Gorsel
    eminlik: float
    konum: Kare | None
    gri_tarama: bool


@dataclasses.dataclass
class CascadeTarayiciAyarlari:
    isim: str


class PyAutoCokluOrnekTarayiciAyarlari(CokluOrnekTarayiciAyarlari):
    pass


@dataclasses.dataclass
class ModAyarlari:
    bosta_bekleme_suresi: float
    bekleme_suresi: float
    tarama_bekleme_suresi: float
    pyautogui_tarayici: dict[str, PyAutoTarayiciAyarlari]
    coklu_ornek_tarayicilar: dict[str, CokluOrnekTarayiciAyarlari]
    cascade_tarayicilar: dict[str, CascadeTarayiciAyarlari]
    okunucak_dosyalar: dict[str, str] | None  # gorseller disindaki dosyalar
    ekstra_ayarlar: dict[str, Any] | None
    tiklama_kisitlamalari: Iterable[dict[str, int]]
