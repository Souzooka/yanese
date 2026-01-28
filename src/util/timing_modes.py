from enum import IntEnum, unique


@unique
class TimingMode(IntEnum):
    RP2C02 = 0  # NTSC
    RP2C07 = 1  # PAL
    MULTI_REGION = 2
    UA6538 = 3  # Dendy
