import os

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

UYUMA_SURESI = 2
GUNLUK_KLASOR = os.path.join(BASE_PATH, "gunluk")
ENGEL_KONTROL_SURESI = 2  # Saniye

DOSYA_YOLLARI = ["cooordinnates/regions.xlsx", os.path.join(BASE_PATH, "imgs")]
