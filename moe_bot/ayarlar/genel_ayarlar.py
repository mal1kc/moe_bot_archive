import logging
import os
import pathlib
import tempfile

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

UYUMA_SURESI = 1
GUNLUK_KLASOR = os.path.join(BASE_PATH, "gunlukler")
GUNLUK_SEVIYESI = logging.DEBUG
DOSYA_YOLLARI = tuple(os.path.join(BASE_PATH, dosya_yolu) for dosya_yolu in ("coordinates/regions.xlsx", "imgs"))

TEMP_DIR = pathlib.Path(tempfile.gettempdir()) / "Moe_auto_bot"
