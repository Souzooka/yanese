def build_u8(lo: int, hi: int) -> int:
    """
    Builds a u8 value given a lo and hi component
    """
    return lo | (hi << 4)


def build_u16(lo: int, hi: int) -> int:
    """
    Builds a u16 value given a lo and hi component.
    """
    return lo | (hi << 8)


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


def to_s8(value: int) -> int:
    """
    Converts a number to its signed 8-bit equivalent.
    """
    value &= 0xFF
    return value if value < 0x80 else 0 - (0x100 - value)


def to_u8(value: int) -> int:
    """
    Converts a number to its unsigned 8-bit equivalent.
    """
    return value & 0xFF


def to_u16(value: int) -> int:
    """
    Converts a number to its unsigned 16-bit equivalent.
    """
    return value & 0xFFFF


def low_byte_of(value: int) -> int:
    """
    Returns the lower byte of an unsigned 16-bit value.
    """
    return value & 0xFF


def high_byte_of(value: int) -> int:
    """
    Returns the high byte of an unsigned 16-bit value.
    """
    return (value >> 8) & 0xFF
