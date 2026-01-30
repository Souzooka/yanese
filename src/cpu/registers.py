from abc import ABC, abstractmethod


class RegisterBase(ABC):
    __slots__ = ["_value"]

    def __init__(self) -> None:
        self._value = 0

    def get_value(self) -> int:
        return self._value

    @abstractmethod
    def set_value(self, value: int) -> None:
        pass

    def increment(self) -> None:
        self.set_value(self.get_value() + 1)

    def decrement(self) -> None:
        self.set_value(self.get_value() - 1)


class Register8Bit(RegisterBase):
    def set_value(self, value: int) -> None:
        self._value = value & 0xFF


class Register16Bit(RegisterBase):
    def set_value(self, value: int) -> None:
        self._value = value & 0xFFFF


class FlagsRegister:
    """
    Represents the status register on the 6502 CPU.
    https://www.nesdev.org/wiki/Status_flags
    """

    __slots__ = ["c", "z", "i", "d", "v", "n"]

    def __init__(self) -> None:
        # bit0 (Carry Flag)
        self.c = False
        # bit1 (Zero/Equal Flag)
        self.z = False
        # bit2 (Interrupt Flag)
        self.i = False
        # bit3 (Decimal Flag -- no effect on NES)
        self.d = False
        # bit4 is B flag
        # (this is essentially set by the type of interrupt which pushes this value to stack)
        # https://www.nesdev.org/wiki/Status_flags#The_B_flag
        # bit5 is always 1
        # bit6 (Overflow Flag)
        self.v = False
        # bit7 (Negative Flag)
        self.n = False

    def to_u8(self, b_flag: bool = True) -> int:
        return (
            (int(self.c) << 0)
            | (int(self.z) << 1)
            | (int(self.i) << 2)
            | (int(self.d) << 3)
            | (int(b_flag) << 4)
            | (1 << 5)
            | (int(self.v) << 6)
            | (int(self.n) << 7)
        )

    def from_u8(self, value: int) -> None:
        self.c = bool(value & (1 << 0))
        self.z = bool(value & (1 << 1))
        self.i = bool(value & (1 << 2))
        self.d = bool(value & (1 << 3))
        self.v = bool(value & (1 << 6))
        self.n = bool(value & (1 << 7))
