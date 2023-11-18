import hashlib

encoding = "utf-8"

SIFRELEME_SIFRESI = "owko2c0m2130x*o123k".encode(encoding)


def sifre_baharati_olustur(password: str) -> str:
    return hashlib.sha256(password.encode(encoding)).hexdigest()


def basit_sifreleme(data: bytes | str, password: str | bytes = SIFRELEME_SIFRESI) -> bytes:
    if isinstance(password, str):
        password = password.encode("utf-8")
    elif not isinstance(password, bytes):
        raise TypeError("password must be str or bytes")
    if isinstance(data, str):
        data = data.encode("utf-8")
    elif not isinstance(data, bytes):
        raise TypeError("data must be str or bytes")

    sifrelenmis = bytearray()
    for i, b in enumerate(data):
        sifrelenmis.append(b ^ password[i % len(password)])
    return bytes(sifrelenmis)


def sifre_hash_olustur(password: str) -> str:
    return hashlib.sha256((password + sifre_baharati_olustur(password)).encode(encoding)).hexdigest()


def hazirlanmis_sifre_olustur(password: str) -> str:
    return basit_sifreleme(sifre_hash_olustur(password).encode(encoding), SIFRELEME_SIFRESI).hex()


def hazirlanmis_sifre_olustur_pass_hash(password_hash: str) -> str:
    """
    password_hash: sifre_hash_olustur ile olusturulmus sifre hashi
    """
    return basit_sifreleme(password_hash.encode(encoding), SIFRELEME_SIFRESI).hex()
