from __future__ import annotations

from typing import TYPE_CHECKING

from src.ppu.Tile import Tile

if TYPE_CHECKING:
    from src.ppu.PPU import PPU


class BackgroundRenderer:
    def __init__(self, ppu: PPU) -> None:
        self.ppu = ppu

    def render_scanline(self) -> None:
        y = self.ppu.scanline

        for i in range(32):
            # TODO: Get name table ID and pattern table ID
            # (these come from the PPU registers)
            name_table_id = 1
            pattern_table_id = 0

            # Calculate the tile index address
            # and retrieve the ID
            pos_offset = i + (32 * (y >> 3))
            name_table_offset = name_table_id * 0x400
            name_table_start = 0x2000
            tile_offset = name_table_start + name_table_offset + pos_offset
            tile_id = self.ppu.memory.read(tile_offset)

            tile = Tile(self.ppu, pattern_table_id, tile_id, y % 8)

            # temp
            palette = [0xFF000000, 0xFF555555, 0xFFAAAAAA, 0xFFFFFFFF]

            for j in range(8):
                color = palette[tile.get_color_index(j)]
                x = i * 8 + j

                self.ppu.plot(x, y, color)
