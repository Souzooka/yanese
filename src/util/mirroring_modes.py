from enum import IntEnum, auto, unique


@unique
class MirroringMode(IntEnum):
    VERTICAL = auto()
    HORIZONTAL = auto()
    FOUR_SCREEN = auto()
    ONE_SCREEN_LOWER_BANK = auto()
    ONE_SCREEN_UPPER_BANK = auto()


# Indicates, for a particular read/write to a 1KB region of
# PPU memory, which nametable/region is associated with that region.
mirroring_modes = {
    # 0 0
    # 1 1
    MirroringMode.HORIZONTAL: {0x2000: 0x000, 0x2400: 0x000, 0x2800: 0x400, 0x2C00: 0x400},
    # 0 1
    # 0 1
    MirroringMode.VERTICAL: {0x2000: 0x000, 0x2400: 0x400, 0x2800: 0x000, 0x2C00: 0x400},
    # 0 0
    # 0 0
    MirroringMode.ONE_SCREEN_LOWER_BANK: {0x2000: 0x000, 0x2400: 0x000, 0x2800: 0x000, 0x2C00: 0x000},
    # 1 1
    # 1 1
    MirroringMode.ONE_SCREEN_UPPER_BANK: {0x2000: 0x400, 0x2400: 0x400, 0x2800: 0x400, 0x2C00: 0x400},
    # 0 1
    # 2 3
    MirroringMode.FOUR_SCREEN: {0x2000: 0x000, 0x2400: 0x400, 0x2800: 0x800, 0x2C00: 0xC00},
}
