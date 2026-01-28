from enum import IntEnum, auto, unique


@unique
class MirroringMode(IntEnum):
    VERTICAL = auto()
    HORIZONTAL = auto()
    FOUR_SCREEN = auto()
