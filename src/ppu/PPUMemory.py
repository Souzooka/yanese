from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.util.mirroring_modes import MirroringMode, mirroring_modes

if TYPE_CHECKING:
    from src.Cartridge import Cartridge
    from src.mappers.Mapper import Mapper


class PPUMemory:
    def __init__(self) -> None:
        self.__vram = bytearray(0x1000)
        self.__cartridge: Optional[Cartridge] = None
        self.__mapper: Optional[Mapper] = None
        self.__mirror_id = MirroringMode.HORIZONTAL

    def on_load(self, cartridge: Cartridge, mapper: Mapper) -> None:
        self.__cartridge = cartridge
        self.__mapper = mapper
        self.set_name_table_mirroring(cartridge.header.mirroring_mode)

    def set_name_table_mirroring(self, mirror_id: int) -> None:
        # If the cart's mirroring is FOUR_SCREEN,
        # prefer this value.
        if self.__cartridge.header.mirroring_mode == MirroringMode.FOUR_SCREEN:
            mirror_id = MirroringMode.FOUR_SCREEN
        self.__mirror_id = mirror_id

    def read(self, address: int) -> int | None:
        value = None

        if 0x0000 <= address <= 0x1FFF:
            # Pattern tables 0 and 1 (mapper)
            # These are the actual tile data
            # https://www.nesdev.org/wiki/PPU_pattern_tables
            if self.__mapper is not None:
                value = self.__mapper.ppu_read(address)

        if 0x2000 <= address <= 0x2FFF:
            # Name tables 0 to 3 (VRAM + mirror)
            # These contain the IDs of each of the
            # 32x30 tiles on screen, along with
            # an attribute table which controls which
            # palette is used by erach 16x16 area
            # of the screen.
            # https://www.nesdev.org/wiki/PPU_nametables
            # https://www.nesdev.org/wiki/PPU_attribute_tables
            bank = mirroring_modes[self.__mirror_id][address & 0xFC00]
            address = bank + (address & 0x3FF)
            value = self.__vram[address]

        if 0x3000 <= address <= 0x3EFF:
            # Mirrors of $2000-$2EFF
            return self.read(address - 0x1000)

        # TODO: Palette RAM/mirrors

        # TODO: Handle PPU open bus
        return value if value else 0

    def write(self, address: int, value: int) -> None:
        if 0x0000 <= address <= 0x1FFF:
            # Pattern tables 0 and 1 (mapper)
            if self.__mapper is not None:
                self.__mapper.ppu_write(address, value)

        if 0x2000 <= address <= 0x2FFF:
            # Name tables 0 to 3 (VRAM + mirror)
            bank = mirroring_modes[self.__mirror_id][address & 0xFC00]
            address = bank + (address & 0x3FF)
            self.__vram[address] = value

        if 0x3000 <= address <= 0x3EFF:
            # Mirrors of $2000-$2EFF
            return self.write(address - 0x1000, value)

        # TODO: Palette RAM + mirrors
