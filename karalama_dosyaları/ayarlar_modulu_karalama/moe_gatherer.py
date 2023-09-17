# klasor yapısı
"""
uyglma_dizini/
├─ imgs/
│  ├─ moe_general/
│  │  ├─ en/
│  │  │  ├─ 1920/
│  │  │  │  ├─ img_file.png
│  │  │  ├─ 3840/
│  │  │  │  ├─ img_file.png
│  │  ├─ tr/
│  │  │  ├─ 1920/
│  │  │  │  ├─ img_file.png
│  │  │  ├─ 3840/
│  │  │  │  ├─ img_file.png
│  ├─ moe_gatherer/
│  │  ├─ en/
│  │  │  ├─ 1920/
│  │  │  │  ├─ img_file.png
│  │  │  ├─ 3840/
│  │  │  │  ├─ img_file.png
│  │  ├─ tr/
│  │  │  ├─ 1920/
│  │  │  │  ├─ img_file.png
│  │  │  ├─ 3840/
│  │  │  │  ├─ img_file.png
├─ src/
│  ├─ config/
│  │  ├─ ayarlar.py
│  │  ├─ moe_gatherer.py
│  │  ├─ moe_general.py
│  │  ├─ moe_camp.py
│  ├─ __init__.py
│  ├─ main.py
"""

GORSEL_DIZINI = "moe_gatherer"

GORSELLER = {
    "_1920": {
        "kaynak_odun": ("kaynak_odun*", "0.9"),
        "kaynak_tas": ("kaynak_tas*", "0.9"),
        "kaynak_demir": ("kaynak_demir*", "0.9"),
        "kaynak_yem": ("kaynak_yem*", "0.9"),
    }
}
