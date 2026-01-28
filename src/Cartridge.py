from __future__ import annotations

from collections.abc import Collection

# Should be the first four bytes of any valid NES ROM
MAGIC = bytes([0x4E, 0x45, 0x53, 0x1A])


class Cartridge:
    __data: Collection

    def __init__(self, data: Collection) -> None:
        self.__data = data

        if not self.is_valid():
            # This isn't an NES ROM, no point in continuing.
            return

    def is_valid(self) -> bool:
        for i in range(len(MAGIC)):
            if self.__data[i] != MAGIC[i]:
                return False
        return True
