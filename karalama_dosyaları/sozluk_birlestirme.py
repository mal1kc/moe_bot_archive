sozluk1 = {
    "_3840": {
        "FOOD": 0.55,
        "WOOD": 0.55,
        "STONE": 0.55,
        "IRON": 0.55,
        "SILVER": 0.55,
        "GOLD": 0.55,
    },
    "_1920": {
        "WOOD": 0.7,
        "FOOD": 0.7,
        "STONE": 0.7,
        "IRON": 0.7,
        "SILVER": 0.7,
        "GOLD": 0.7,
    },
    "_1366": {
        "WOOD": 0.7,
        "FOOD": 0.7,
        "STONE": 0.7,
        "IRON": 0.7,
        "SILVER": 0.7,
        "GOLD": 0.7,
    },
}
sozluk2 = {
    "_3840": {
        "bul": 0.7,
        "buyutec": 0.7,
        "isgal_1": 0.7,
        "isgal_2": 0.7,
        "isgal_duzen_logo": 0.7,
        "isgal_not": 0.7,
    },
    "_1920": {
        "bul": 0.7,
        "buyutec": 0.7,
        "isgal_1": 0.7,
        "isgal_2": 0.7,
        "isgal_duzen_logo": 0.7,
        "isgal_not": 0.7,
    },
    "_1366": {
        "bul": 0.7,
        "buyutec": 0.7,
        "isgal_1": 0.7,
        "isgal_2": 0.7,
        "isgal_duzen_logo": 0.7,
        "isgal_not": 0.7,
    },
}


def sozlukBirlestir(sozluk1: dict, sozluk2: dict):
    """
    iki sözlüğü birleştirir
    """
    sonuc = dict()
    if sozluk1.keys() == sozluk2.keys():
        for k, v in sozluk1.items():
            ic_sonuc = dict()
            if type(v) is dict:
                ic_sonuc = sozlukBirlestir(sozluk1[k], sozluk2[k])
            sonuc[k] = ic_sonuc
        return sonuc
    else:
        sonuc = {**sozluk1, **sozluk2}
    return sonuc

    # return {**sozluk1, **sozluk2}


print(sozlukBirlestir(sozluk1, sozluk2))
