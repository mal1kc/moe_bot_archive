from moe_gatherer import anahtar_olustur, AnahtarKaynagiDXdiag, SystemInfo


def main():
    # -> bu cihazin anahtari
    oto_uretilmis_anahtar = anahtar_olustur()
    # -> baska cihazin anahtari
    anahtar_kaynagi = AnahtarKaynagiDXdiag()
    print(AnahtarKaynagiDXdiag.get_sys_info(anahtar_kaynagi._dxdiag))
    sys_info = SystemInfo(
        machine_name="DESKTOP-RK0QR39",
        operating_system="Windows 10 Pro 64-bit",
        system_manufacturer="ASUSTeK COMPUTER INC.",
        system_model="GL553VD",
        firmware_type="BIOS",
        bios="BIOS aasdaqvwqe12",
        processor="Intel(R) ",
        # machine_name="CASPER_NIRVANA",
        # operating_system="Windows 10 Home Single Language 64-bit",
        # system_manufacturer="Casper Bilgisayar Sistemleri A.S",
        # system_model="Casper Nirvana Notebook",
        # bios="Phoenix BIOS SC-T v2.1",
        # firmware_type="BIOS",
        # processor="Intel(R) Core(TM) i5-4200M",
    )  # benim pc bilgilerim

    sys_info_2 = SystemInfo(
        machine_name="DESKTOP-RIQLJRQ",
        operating_system="Windows 10 Pro 64-bit",
        system_manufacturer="ASUSTeK COMPUTER INC.",
        system_model="GL553VD",
        firmware_type="BIOS",
        bios="BIOS",
        processor="Intel(R)",
    )
    elle_girilen_degerlerden_uretilmis_anahtar = anahtar_kaynagi.anahtar_olustur(sys_info=sys_info)
    elle_girilen_degerlerden_uretilmis_anahtar2 = anahtar_kaynagi.anahtar_olustur(sys_info=sys_info_2)

    print("-" * 50)
    print(f"{oto_uretilmis_anahtar=}")
    print("-" * 50)
    print(f"{elle_girilen_degerlerden_uretilmis_anahtar=}")
    print("-" * 50)
    print(f"{oto_uretilmis_anahtar == elle_girilen_degerlerden_uretilmis_anahtar=}")
    print(f"{elle_girilen_degerlerden_uretilmis_anahtar2=}")
    print(f"{elle_girilen_degerlerden_uretilmis_anahtar2 == elle_girilen_degerlerden_uretilmis_anahtar=}")

    # 5766956de3bbee63fff3f6090b15c173beb16b83bc251890b35003d8a28dc8ecac390dde5429d242bd9f7659ae275a420ca71be763fb3de170fa21dc3f7a3f73_nfo # noqa: E501
    # gibi adı olan dosyayı sil paylaşma ; *_nfo dosyasını sil
    # kopyalansada işe yaramaz çunku adı kullanıcı adının + islemci adinin hashlenmiş hali (sha512)
    # dxdiag çıktısını yavaş veriyor diye şifrelediğim dxdiag çıktısı o
    # ilk oluşturma baya yavaş oluyor dxdiag çıktısı almak için


if __name__ == "__main__":
    main()
