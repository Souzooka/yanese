from enum import IntEnum, unique


@unique
class ConsoleType(IntEnum):
    NES = 0
    VS = 1
    PLAYCHOICE = 2
    EXTENDED = 3
