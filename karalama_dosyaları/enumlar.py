import enum


class ModSinyal(enum.IntEnum):
    DevamEt = 0
    Bekle = 1
    Sonlandir = 2
    MesajUlasmadi = 3
    MesajUlasti = 4
    FailSafe = 5
    Menudeyim = 6


class DilEnum(enum.StrEnum):
    TR = enum.auto()
    EN = enum.auto()
