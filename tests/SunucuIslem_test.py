import logging

import pytest
import requests

from moe_bot.sifremele import hazirlanmis_sifre_olustur, sifre_hash_olustur
from moe_bot.sunucu_islemleri import _URLS, SunucuIslem, SunucuIslemSonucu
from moe_bot.temel_siniflar import KullaniciGirisVerisi

LOCAL_SUNUCU_ADRESI = "http://127.0.0.1:5000"
LOGGER = logging.getLogger(__name__)

# IMPORTANT \ SUNUCUYU ACMAYI UNUTMA \
# IMPORTANT \ Bunlari eklemeyi unutma test için sonra sil


@pytest.fixture()
def test_kullanici_paketsiz_sifreli():
    return "test_user_without_package", hazirlanmis_sifre_olustur("test_user_without_package")


@pytest.fixture()
def test_kullanici_paketsiz():
    return "test_user_without_package", sifre_hash_olustur("test_user_without_package")


@pytest.fixture()
def test_kullanici_paketli():
    return "test_user_with_package", sifre_hash_olustur("test_user_with_package")


# IMPORTANT \ SUNUCUYU SİLMEYİ UNUTMA \


def test_sunucu_acik_mi():
    LOGGER.info("Sunucu acik mi")
    response = requests.get(LOCAL_SUNUCU_ADRESI)
    assert response.status_code == 200, "Sunucu acik degil"
    LOGGER.info(response.json())


def test_login_enpoint_exists():
    LOGGER.info("test_login_enpoint_exists")
    response = requests.get(LOCAL_SUNUCU_ADRESI + "/api/v1/user/login")
    assert response.status_code == 401  # unauthorized
    LOGGER.info(response.json())


@pytest.fixture()
def login_user_auth_data(test_kullanici_paketsiz_sifreli):
    return (test_kullanici_paketsiz_sifreli[0], test_kullanici_paketsiz_sifreli[1])


def test_login_endpoint_login(login_user_auth_data):
    LOGGER.info("test_login_endpoint_login")
    LOGGER.debug(f"login_user_auth_data: {login_user_auth_data},url : {LOCAL_SUNUCU_ADRESI + '/api/v1/user/login'}")
    response = requests.post(LOCAL_SUNUCU_ADRESI + "/api/v1/user/login", auth=login_user_auth_data)
    # package_not_found
    assert response.status_code == 404, response.json()
    LOGGER.info(response.json())


def test_user_info_endpoint_cred_not_found():
    LOGGER.info("test_user_info_endpoint_cred_not_found")
    response = requests.get(LOCAL_SUNUCU_ADRESI + "/api/v1/user/info")
    assert response.status_code == 404, (response.status_code, response.json())
    assert response.json()["message"] == "user_cred_not_found", response.json()
    LOGGER.info(response.json())


def test_user_info_endpoint_authorized(login_user_auth_data):
    LOGGER.info("test_user_info_endpoint_authorized")
    LOGGER.debug(f"login_user_auth_data: {login_user_auth_data},url : {LOCAL_SUNUCU_ADRESI + '/api/v1/user/info'}")
    response = requests.get(LOCAL_SUNUCU_ADRESI + "/api/v1/user/info", auth=login_user_auth_data)
    assert response.status_code == 200, (response.status_code, response.json())
    assert response.json()["message"] == "user_info_success", response.json()
    LOGGER.info(response.json())


def test_giris_yap_paketsiz_kullanici(
    test_kullanici_paketsiz,
):
    LOGGER.info("test_giris_yap_paketsiz_kullanici")
    kullanici_giris_verisi = KullaniciGirisVerisi(
        *test_kullanici_paketsiz,
    )
    sunucu_islem = SunucuIslem(
        kullanici_giris_verisi=kullanici_giris_verisi,
    )
    SunucuIslem._urls = _URLS(
        ULogin=LOCAL_SUNUCU_ADRESI + "/api/v1/user/login",
        UInfo=LOCAL_SUNUCU_ADRESI + "/api/v1/user/info",
    )
    sonuc = sunucu_islem.giris_yap()
    assert sonuc == SunucuIslemSonucu.PAKET_BULUNAMADI, sonuc


def test_giris_yap_paketli_kullanici(
    test_kullanici_paketli,
):
    LOGGER.info("test_giris_yap_paketli_kullanici")
    kullanici_giris_verisi = KullaniciGirisVerisi(
        *test_kullanici_paketli,
    )
    sunucu_islem = SunucuIslem(
        kullanici_giris_verisi=kullanici_giris_verisi,
    )
    SunucuIslem._urls = _URLS(
        ULogin=LOCAL_SUNUCU_ADRESI + "/api/v1/user/login",
        UInfo=LOCAL_SUNUCU_ADRESI + "/api/v1/user/info",
    )
    sonuc = sunucu_islem.giris_yap()
    assert sonuc == SunucuIslemSonucu.BASARILI, sonuc


def test_kullanici_bilgisi_paketli_kullanici(
    test_kullanici_paketli,
):
    LOGGER.info("test_kullanici_bilgisi_paketli_kullanici")
    kullanici_giris_verisi = KullaniciGirisVerisi(
        *test_kullanici_paketli,
    )
    sunucu_islem = SunucuIslem(
        kullanici_giris_verisi=kullanici_giris_verisi,
    )
    SunucuIslem._urls = _URLS(
        ULogin=LOCAL_SUNUCU_ADRESI + "/api/v1/user/login",
        UInfo=LOCAL_SUNUCU_ADRESI + "/api/v1/user/info",
    )
    sonuc = sunucu_islem._kullanici_bilgilerini_al()
    assert sonuc == SunucuIslemSonucu.BASARILI, sonuc
    assert sunucu_islem.kullanici_verisi["name"] == test_kullanici_paketli[0], sunucu_islem.kullanici_verisi  # type: ignore
