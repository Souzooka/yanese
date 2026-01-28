def build_u8(lo: int, hi: int) -> int:
    """
    Builds a u8 value given a lo and hi component
    """
    return lo | (hi << 4)


def lower_nibble(value: int) -> int:
    """
    Extracts lower 4 bits from an 8-bit value
    """
    return value & 0xF


def upper_nibble(value: int) -> int:
    """
    Extracts upper 4 bits from an 8-bit value
    """
    return (value >> 4) & 0xF


def get_bit(value: int, position: int) -> int:
    """
    Extracts a bit from an integer.
    """
    return (value >> position) & 1


def get_bits(value: int, start_position: int, size: int) -> int:
    """
    Extracts a series of bits from an integer.
    """
    return (value >> start_position) & ((1 << size) - 1)


def get_flag(value: int, position: int) -> bool:
    """
    Extracts a bit from an integer and returns it as boolean.
    """
    return bool(get_bit(value, position))
