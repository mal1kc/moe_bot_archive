import dataclasses

from moe_bot.temel_siniflar import GorselYolu, Kare
from moe_bot.types import Any


@dataclasses.dataclass
class ModAyarlari:
    bosta_bekleme_suresi: float
    bekleme_suresi: float
    tarama_bekleme_suresi: float
    # TODO : Tarayici tipleri -> template matching, pyautogui, cascadeclasssifier
    tarayicilar: dict[str, tuple[GorselYolu, float, Kare | None]]
    coklu_tarayicilar: dict[str, tuple[GorselYolu, tuple[float], Kare | None]] | None
    okunucak_dosyalar: dict[str, str] | None  # gorseller disindaki dosyalar
    ekstra_ayarlar: dict[str, Any] | None
