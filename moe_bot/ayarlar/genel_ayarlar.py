import os


BASE_PATH = os.path.dirname(os.path.dirname(__file__))

UYUMA_SURESI = 1
GUNLUK_KLASOR = os.path.join(BASE_PATH, "gunlukler")
DOSYA_YOLLARI = tuple(os.path.join(BASE_PATH, dosya_yolu) for dosya_yolu in ("coordinates/regions.xlsx", "imgs"))
