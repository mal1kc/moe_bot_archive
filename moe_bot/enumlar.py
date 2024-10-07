import enum


class IslemSinyal(enum.IntEnum):
    DEVAM_ET = 0
    BEKLE = 1
    SONLANDIR = 2
    MESAJ_ULASMADI = 3
    MESAJ_ULASTI = 4
    FAILSAFE = 5
    FAILSAFE_SONLANDIR = 6


class EkranBoyutEnum(enum.Enum):
    _1366 = (1366, 768)
    _1920 = (1920, 1080)
    _3840 = (3840, 2160)


class DilEnum(enum.StrEnum):
    TR = "tr"
    EN = "en"


class SelectibleModEnum(enum.Enum):
    moe_gatherer = enum.auto()
    # moe_raid = auto()
    # moe_camp = auto()
    # moe_arena = auto()


class GUIPagesEnum(enum.Enum):
    LOGIN = enum.auto()
    MOD_SELECT = enum.auto()
    MOE_GATHERER = enum.auto()


class ModEnum(enum.Enum):
    MOE_GATHERER = enum.auto()
    # MOE_RAID = auto()
    # MOE_CAMP = auto()
    # MOE_ARENA = auto()
