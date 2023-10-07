import enum


class ModSinyal(enum.IntEnum):
    DevamEt = 0
    Bekle = 1
    Sonlandir = 2
    MesajUlasmadi = 3
    MesajUlasti = 4
    FailSafe = 5


class EkranBoyutEnum(enum.Enum):
    _1366 = (1366, 768)
    _1920 = (1920, 1080)
    _3840 = (3840, 2160)


class DilEnum(enum.StrEnum):
    TR = "tr"
    EN = "en"
