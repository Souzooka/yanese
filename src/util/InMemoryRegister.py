from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from src.ppu.PPU import PPU


class InMemoryRegister(ABC):
    def __init__(self):
        super().__init__()

        self._fields: List[Tuple[str, int, int]] = []

        self._value = 0

        self.on_load()

    def on_load(self) -> None:
        """
        Called upon initialization.
        """
        pass

    def on_read(self) -> int:
        """
        Called upon read to this register.
        Overwrite to implement additional side effects.
        """
        return self.get_value()

    def on_write(self, value: int) -> None:
        """
        Called upon write to this register.
        Overwrite to implement additional side effects.
        """
        self.set_value(value)

    def set_value(self, value: int) -> None:
        """
        Sets the value of this register and updates its fields.
        """
        self._value = value
        self.__extract_fields()

    def get_value(self) -> int:
        """
        Returns the u8 value of this register.
        """
        return self._value

    def __extract_field(self, name: str, start_bit: int, size: int = 1) -> None:
        mask = ((1 << size) - 1) << start_bit
        value = (self._value & mask) >> start_bit
        setattr(self, name, value)

    def __extract_fields(self) -> None:
        for name, start_bit, size in self._fields:
            self.__extract_field(name, start_bit, size)

    def add_field(self, name: str, start_bit: int, size: int) -> InMemoryRegister:
        """
        Adds a read-only field to this register.
        These fields represent certain segments of the register value.

        Returns the InMemoryRegister instance so this can be chained.
        """
        self._fields.append((name, start_bit, size))
        self.__extract_field(name, start_bit, size)
        return self

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)

        for field_name, start_bit, size in self._fields:
            if name == field_name:
                value = int(value)
                value &= (1 << size) - 1
                value <<= start_bit

                mask = (~(((1 << size) - 1) << start_bit)) & 0xFF
                value |= self._value & mask
                object.__setattr__(self, "_value", value)
                object.__setattr__(self, name, value)
                return
        return object.__setattr__(self, name, value)


class PPUInMemoryRegister(InMemoryRegister):
    def __init__(self, ppu: PPU) -> None:
        super().__init__()
        self.ppu = ppu
