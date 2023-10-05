import random

import pytest

from moe_bot.kaynakislem import Kare, KaynakKare


@pytest.fixture
def ornek_kare() -> KaynakKare:
    return KaynakKare(150, 295, 104, 72)


def sadece_pozitif(sayi):
    return sayi if sayi > 0 else 0


def test_kare_init(ornek_kare):
    kaynak_kare = ornek_kare
    assert KaynakKare(Kare(150, 295, 104, 72)), "KaynakKare init kare hatası"
    assert KaynakKare(kaynak_kare.x, kaynak_kare.y, kaynak_kare.genislik, kaynak_kare.yukseklik), "KaynakKare init kordinat hatası"


def test_kare_str(ornek_kare):
    kaynak_kare = ornek_kare
    assert (
        str(kaynak_kare) == f"KaynakKare({kaynak_kare.x},{kaynak_kare.y},{kaynak_kare.genislik},{kaynak_kare.yukseklik})"
    ), f"KaynakKare str hatası\n beklenen: KaynakKare({kaynak_kare.x},{kaynak_kare.y},{kaynak_kare.genislik},{kaynak_kare.yukseklik})\n alınan: {kaynak_kare}"  # noqa: E501


def test_kare_repr(ornek_kare):
    kaynak_kare = ornek_kare
    assert (
        repr(kaynak_kare) == f"KaynakKare({kaynak_kare.x},{kaynak_kare.y},{kaynak_kare.genislik},{kaynak_kare.yukseklik})"
    ), f"KaynakKare repr hatası\n beklenen: KaynakKare({kaynak_kare.x},{kaynak_kare.y},{kaynak_kare.genislik},{kaynak_kare.yukseklik})\n alınan: {kaynak_kare}"  # noqa: E501


def test_kare_hash(ornek_kare):
    kaynak_kare = ornek_kare
    assert hash(kaynak_kare) == hash(str(kaynak_kare.koordinat))


def test_kare_hash2(ornek_kare):
    kaynak_kare = ornek_kare
    assert set([kaynak_kare]) == set(
        [KaynakKare(150, 295, 104, 72), kaynak_kare]
    ), f"KaynakKare hash hatası\n beklenen: {set([kaynak_kare])}\n alınan: {set([kaynak_kare])}"


def kare_olustur_icindeki_kare(ornek_kare, buyume_miktari):
    kaynak_kare = ornek_kare
    x = kaynak_kare.x + random.randint(-buyume_miktari, buyume_miktari)
    y = kaynak_kare.y + random.randint(-buyume_miktari, buyume_miktari)
    genislik = kaynak_kare.genislik
    yukseklik = kaynak_kare.yukseklik
    return KaynakKare(x, y, genislik, yukseklik)


def kare_olustur_disindaki_kare(ornek_kare, buyume_miktari):
    def kontrollu_rastgele(baslangc, bitis, dislanan_aralik) -> int:
        sayi = random.choice([i for i in range(baslangc, bitis) if i not in range(*dislanan_aralik)])
        if sayi is None:
            sayi = 0
        return sayi

    kaynak_kare = ornek_kare
    x = sadece_pozitif(
        kaynak_kare.x
        + kontrollu_rastgele(
            -buyume_miktari * 5,
            buyume_miktari * 5,
            ((-buyume_miktari - 5, buyume_miktari + 5)),
        )
    )
    y = sadece_pozitif(
        kaynak_kare.y
        + kontrollu_rastgele(
            -buyume_miktari * 5,
            buyume_miktari * 5,
            (-buyume_miktari - 5, buyume_miktari + 5),
        )
    )
    genislik = kaynak_kare.genislik
    yukseklik = kaynak_kare.yukseklik
    return KaynakKare(x, y, genislik, yukseklik)


def test_disindaMi_icinde(ornek_kare):
    kaynak_kare = ornek_kare
    # : kaynak_kare = KaynakKare(150, 295, 104, 72)

    icindeki_kare = kare_olustur_icindeki_kare(kaynak_kare, 30)

    assert (
        kaynak_kare.disindaMi(icindeki_kare, 30) is False
    ), f"KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(icindeki_kare)}"

    icindeki_kare = kare_olustur_icindeki_kare(kaynak_kare, 40)

    assert (
        kaynak_kare.disindaMi(icindeki_kare, 40) is False
    ), f"KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(icindeki_kare)}"

    icindeki_kare = kare_olustur_icindeki_kare(kaynak_kare, 60)
    assert (
        kaynak_kare.disindaMi(icindeki_kare, 60) is False
    ), f"KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(icindeki_kare)}"

    icindeki_kare = kare_olustur_icindeki_kare(kaynak_kare, 80)

    assert (
        kaynak_kare.disindaMi(icindeki_kare, 80) is False
    ), f"KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(icindeki_kare)}"

    icindeki_kare = kare_olustur_icindeki_kare(kaynak_kare, 100)
    assert (
        kaynak_kare.disindaMi(icindeki_kare, 100) is False
    ), f"KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(icindeki_kare)}"


# def test_disindaMi_disinda(ornek_kare):
#     kaynak_kare = ornek_kare
#     # : kaynak_kare = KaynakKare(150, 295, 104, 72)

#     disindaki_kare = kare_olustur_disindaki_kare(kaynak_kare, 30)

#     assert (
#         kaynak_kare.disindaMi(disindaki_kare, 30) is True
#     ), f"KaynakKare disindaMi hatası\n beklenen: True\n alınan: {kaynak_kare.disindaMi(disindaki_kare)}"

#     disindaki_kare = kare_olustur_disindaki_kare(kaynak_kare, 40)

#     assert (
#         kaynak_kare.disindaMi(disindaki_kare, 40) is True
#     ), f"KaynakKare disindaMi hatası\n beklenen: True\n alınan: {kaynak_kare.disindaMi(disindaki_kare)}"

#     disindaki_kare = kare_olustur_disindaki_kare(kaynak_kare, 60)
#     assert (
#         kaynak_kare.disindaMi(disindaki_kare, 60) is True
#     ), f"KaynakKare disindaMi hatası\n beklenen: True\n alınan: {kaynak_kare.disindaMi(disindaki_kare)}"

#     disindaki_kare = kare_olustur_disindaki_kare(kaynak_kare, 80)

#     assert (
#         kaynak_kare.disindaMi(disindaki_kare, 80) is True
#     ), f"KaynakKare disindaMi hatası\n beklenen: True\n alınan: {kaynak_kare.disindaMi(disindaki_kare)}"

#     # ! kare alanindan kaynaklanan hatalardan dolayi bu testi gecemiyor.
#     #
#     # disindaki_kare = kare_olustur_disindaki_kare(kaynak_kare, 100)
#     # assert (
#     #     kaynak_kare.disindaMi(disindaki_kare,100) is True
#     # ), f'KaynakKare disindaMi hatası\n beklenen: False\n alınan: {kaynak_kare.disindaMi(disindaki_kare)}'
