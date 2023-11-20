import pytest

from moe_bot.lokalizasyon import en, tr  # noqa: F401
from moe_bot.temel_siniflar import DilEnum, Diller


@pytest.fixture(autouse=True)
def load_diller():
    Diller()


def test_varsayilan_dil():
    assert Diller.aktif_dil_getir() is DilEnum.TR


def test_dil_degistir():
    Diller.aktif_dil_degistir(DilEnum.EN)  # type: ignore
    assert Diller.aktif_dil_getir() is DilEnum.EN
    Diller.aktif_dil_degistir(DilEnum.TR)  # type: ignore
    assert Diller.aktif_dil_getir() is DilEnum.TR


def test_dil_kitapligi():
    assert "GOLD" in Diller.dil_kitapligi(DilEnum.EN)["UI"].values()
    assert "ALTIN" in Diller.dil_kitapligi(DilEnum.TR)["UI"].values()
    assert Diller.dil_kitapligi(DilEnum.EN) == en.to_dict()
    assert Diller.dil_kitapligi(DilEnum.TR) == tr.to_dict()


def test_lazy_loading():
    assert Diller.dil_kitapligi(DilEnum.EN) == en.to_dict()
    assert Diller.dil_kitapligi(DilEnum.TR) == tr.to_dict()
    assert Diller.dil_kitapligi(DilEnum.EN) == en.to_dict()
    assert Diller.dil_kitapligi(DilEnum.TR) == tr.to_dict()


def test_lang_cache_clear():
    Diller.lang_cache_clear()
    assert Diller.dil_kitapligi(DilEnum.EN) == en.to_dict()
    assert Diller.dil_kitapligi(DilEnum.TR) == tr.to_dict()
    Diller.aktif_dil_degistir(DilEnum.EN)
    assert Diller.dil_kitapligi(DilEnum.EN) == en.to_dict()
    Diller.lang_cache_clear()
