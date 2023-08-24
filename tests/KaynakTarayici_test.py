from pathlib import Path
from random import choice

import cv2
import pytest

from moe_gatherer.kaynakislem import KaynakTarayici, KaynakTipi

# KaynakTarayici için testler


@pytest.fixture
def ornek_kaynak_tarayici() -> KaynakTarayici:
    """
    rastgele kaynak tipi kullanılarak ornek bir KaynakTarayici nesnesi olusturur
    """
    return KaynakTarayici(choice(list(KaynakTipi)))


def test_ornek_dler(ornek_kaynak_tarayici):
    """
    ornek_dler'deki dosyalarin varligini ve dosya olup olmadigini kontrol eder -> Path.exists() ve Path.is_file() ile
    """

    kaynak_tarayici: KaynakTarayici = ornek_kaynak_tarayici  # type: ignore
    ornek_dler = [Path(ornek_d) for ornek_d in kaynak_tarayici.ornek_dler]
    for ornek_dy in ornek_dler:
        assert ornek_dy.exists(), f"ornek dosya yolu {ornek_dy} yok"
        assert ornek_dy.is_file(), f"ornek dosya yolu {ornek_dy} dosya degil"


def test_ornek_gorselmi(ornek_kaynak_tarayici):
    """
    ornek_dler'deki dosyalarin gorsel olup olmadigini kontrol eder -> cv2.imread() ile
    """

    def _ornek_gorselmi(ornek_dy: str) -> bool:
        try:
            if cv2.imread(ornek_dy) is None:
                return False
            return True
        except Exception:
            return False

    kaynak_tarayici: KaynakTarayici = ornek_kaynak_tarayici  # type: ignore
    for ornek_dy in kaynak_tarayici.ornek_dler:
        assert _ornek_gorselmi(ornek_dy), f"ornek dosya yolu {ornek_dy} gorsel degil"
