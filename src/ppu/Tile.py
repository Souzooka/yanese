from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ppu.PPU import PPU


class Tile:
    def __init__(self, ppu: PPU, pattern_table_id: int, tile_id: int, y: int) -> None:
        table_address = pattern_table_id * 0x1000
        low_plane_address = table_address + tile_id * 0x10
        high_plane_address = low_plane_address + 8
        self.__low_row = ppu.memory.read(low_plane_address + y)
        self.__high_row = ppu.memory.read(high_plane_address + y)

    def get_color_index(self, x: int) -> int:
        bit = 7 - x
        low_bit = int((self.__low_row & (1 << bit)) != 0)
        high_bit = int((self.__high_row & (1 << bit)) != 0)
        return (high_bit << 1) | low_bit
