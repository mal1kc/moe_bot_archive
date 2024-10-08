from __future__ import annotations

from enum import IntEnum, StrEnum, auto
from functools import lru_cache
from logging import getLogger

import requests

from .hatalar import BaglantiHatasi, Hata
from .sifremele import hazirlanmis_sifre_olustur_pass_hash
from .temel_siniflar import Diller, KullaniciGirisVerisi

LOGGER = getLogger(__name__)

SUNUCU_BASE_URL = "http://37.247.101.246:8080"  # sunucu adresi

URL_ONEKI = SUNUCU_BASE_URL + "/api/v1/user"  # user api endpoint

SUNUCU_OTURUM_SURESI = 30  # sunucu oturum süresi (saniye)


class SunucuIslemSonucu(IntEnum):
    BASARILI = auto()
    BASARISIZ = auto()
    HATALI = auto()
    BILINMEYEN_HATA = auto()
    BAGLANTI_HATASI = auto()
    GIRIS_BILGISI_HATALI = auto()
    PAKET_BULUNAMADI = auto()
    MAKSIMUM_GIRIS_HATASI = auto()
    KULLANICI_BULUNAMADI = auto()


class GirisYapmaSonucu(StrEnum):
    BASARILI = "login_success"
    BASARISIZ = "login_failed"
    GIRIS_BILGISI_HATALI = "user_cred_not_found"
    PAKET_BULUNAMADI = "package_not_found"
    MAKSIMUM_GIRIS_HATASI = "max_online_user"
    KULLANICI_BULUNAMADI = "user_not_found"


class KullaniciBilgileriSonucu(StrEnum):
    BASARILI = "user_info_success"
    GIRIS_BILGISI_HATALI = "user_cred_not_found"


class _URLS:
    _instance = None
    __slots__ = ["ULogin", "UInfo", "Main"]
    u_login: str
    up_info: str
    main: str

    def __init__(self, ULogin: str, UInfo: str) -> None:
        if isinstance(_URLS._instance, _URLS):
            raise Hata("_URLS sınıfından birden fazla instance oluşturulamaz.")
        self.ULogin = ULogin
        self.UInfo = UInfo
        self.Main = SUNUCU_BASE_URL + "/"


API_ENDPOINTS = _URLS(ULogin=URL_ONEKI + "/login", UInfo=URL_ONEKI + "/info")


class SunucuIslem:
    __slots__ = ["kullanici_giris_verisi", "kullanici_verisi", "_urls", "_req_session"]

    def __init__(self, kullanici_giris_verisi: KullaniciGirisVerisi) -> None:
        self._urls = API_ENDPOINTS
        self.kullanici_giris_verisi = kullanici_giris_verisi
        self.kullanici_giris_verisi = (
            kullanici_giris_verisi.name,
            hazirlanmis_sifre_olustur_pass_hash(kullanici_giris_verisi.password_hash),
        )
        self._req_session = requests.Session()
        if self._sunucu_acik_mi() != SunucuIslemSonucu.BASARILI:
            raise BaglantiHatasi(Diller.lokalizasyon("server_connection_error", "ERROR"))
        self.kullanici_verisi = None

    def _sunucu_acik_mi(self) -> SunucuIslemSonucu:
        try:
            resp = self._req_session.get(url=self._urls.Main)
            if resp.status_code == 200:
                return SunucuIslemSonucu.BASARILI if resp.json()["status"] == "OK" else SunucuIslemSonucu.HATALI
            return SunucuIslemSonucu.HATALI
        except Exception as exc:
            LOGGER.exception("Sunucuya erişilemiyor. exception -> %s" % str(exc))
            return SunucuIslemSonucu.BAGLANTI_HATASI

    def _giris_yapmayi_dene(self) -> SunucuIslemSonucu:
        try:
            LOGGER.debug(f"kullanici_giris_verisi: {self.kullanici_giris_verisi}")
            LOGGER.debug(f"url : {self._urls.ULogin}")
            resp = self._req_session.post(url=self._urls.ULogin, auth=self.kullanici_giris_verisi)
            resp_json = resp.json()
            LOGGER.debug(f"resp_json: {resp_json}")
            if resp.status_code == 200:
                if resp_json["status"] == "success" and resp_json["message"] == "login_success":
                    return SunucuIslemSonucu.BASARILI
                return SunucuIslemSonucu.BILINMEYEN_HATA
            if resp_json["status"] == "error" and resp_json["message"] == GirisYapmaSonucu.PAKET_BULUNAMADI:
                return SunucuIslemSonucu.PAKET_BULUNAMADI
            if resp_json["status"] == "error" and resp_json["message"] == GirisYapmaSonucu.MAKSIMUM_GIRIS_HATASI:
                return SunucuIslemSonucu.MAKSIMUM_GIRIS_HATASI
            if resp_json["status"] == "error" and resp_json["message"] == GirisYapmaSonucu.KULLANICI_BULUNAMADI:
                return SunucuIslemSonucu.KULLANICI_BULUNAMADI
            if resp_json["status"] == "error" and resp_json["message"] == GirisYapmaSonucu.GIRIS_BILGISI_HATALI:
                return SunucuIslemSonucu.GIRIS_BILGISI_HATALI
            if resp_json["status"] == "error" and resp_json["message"] == GirisYapmaSonucu.BASARISIZ:
                return SunucuIslemSonucu.BASARISIZ
            return SunucuIslemSonucu.HATALI
        except Exception:
            return SunucuIslemSonucu.BAGLANTI_HATASI

    @lru_cache(maxsize=1)
    def _kullanici_bilgilerini_al(self) -> SunucuIslemSonucu:
        try:
            LOGGER.debug(f"kullanici_verisi: {self.kullanici_verisi}")
            LOGGER.debug(f"url : {self._urls.UInfo}")
            resp = self._req_session.get(url=self._urls.UInfo, auth=self.kullanici_giris_verisi)
            resp_json = resp.json()
            LOGGER.debug(f"resp_json: {resp_json}")
            if resp.status_code == 200:
                if resp_json["status"] == "success" and resp_json["message"] == KullaniciBilgileriSonucu.BASARILI:
                    self.kullanici_verisi = resp_json["user"]
                    return SunucuIslemSonucu.BASARILI
                return SunucuIslemSonucu.BILINMEYEN_HATA
            if resp_json["status"] == "error" and resp_json["message"] == KullaniciBilgileriSonucu.GIRIS_BILGISI_HATALI:
                return SunucuIslemSonucu.GIRIS_BILGISI_HATALI
            return SunucuIslemSonucu.HATALI
        except Exception:
            return SunucuIslemSonucu.BAGLANTI_HATASI

    def giris_yenile(self) -> SunucuIslemSonucu:
        return self.giris_yap()

    def giris_yap(self) -> SunucuIslemSonucu:
        sonuc = self._giris_yapmayi_dene()
        if sonuc == SunucuIslemSonucu.BASARILI:
            sonuc = self._kullanici_bilgilerini_al()
        return sonuc
