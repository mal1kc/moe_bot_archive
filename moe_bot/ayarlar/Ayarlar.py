import dataclasses
from moe_bot.types import Any, GorselEminlik
from moe_bot.temel_siniflar import Kare, GorselYolu


@dataclasses.dataclass
class ModAyarlari:
    bosta_bekleme_suresi: float
    bekleme_suresi: float
    tarama_bekleme_suresi: float
    tarayicilar: dict[str, tuple[GorselYolu, GorselEminlik, Kare | None]]
    coklu_tarayicilar: dict[str, tuple[GorselYolu, tuple[GorselEminlik], Kare | None]] | None
    okunucak_dosyalar: dict[str, str] | None  # gorseller disindaki dosyalar
    ekstra_ayarlar: dict[str, Any] | None
