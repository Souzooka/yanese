from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import numpy as np

from src.interrupts import Interrupt
from src.ppu.BackgroundRenderer import BackgroundRenderer
from src.ppu.PPUMemory import PPUMemory
from src.ppu.VideoRegisters import VideoRegisters

if TYPE_CHECKING:
    from src.Cartridge import Cartridge
    from src.cpu.CPU import CPU
    from src.mappers.Mapper import Mapper

H = 256
V = 240
H_BLANK = 85
V_BLANK = 21


class PPU:
    def __init__(self, cpu: CPU) -> None:
        self.cpu = cpu

        self.cycle = 0
        self.scanline = -1
        self.frame = 0

        self.frame_buffer = np.ndarray((256, 240), dtype=np.uint32)

        self.memory = PPUMemory()

        self.mapper: Optional[Mapper] = None

        self.registers = VideoRegisters(self)

        self.background_renderer = BackgroundRenderer(self)

    def on_load(self, cartridge: Cartridge, mapper: Mapper) -> None:
        self.mapper = mapper
        self.memory.on_load(cartridge, mapper)

    def plot(self, x: int, y: int, color: int) -> None:
        """
        Plots a pixel into the frame buffer.
        """
        self.frame_buffer[x][y] = color

    def step(self, on_frame: Callable[[np.ndarray], None], on_interrupt: Callable[[int], None]) -> None:
        if self.scanline == -1:
            self.__pre_line()
        elif self.scanline < V:
            self.__visible_line()
        elif self.scanline == V + 1:
            self.__vblank_line(on_interrupt)

        self.cycle += 1
        if self.cycle >= H + H_BLANK:
            # Line is done; new line
            self.cycle = 0
            self.scanline += 1

            if self.scanline >= V + V_BLANK:
                # Frame is done; new frame
                self.scanline = -1
                self.frame += 1
                on_frame(self.frame_buffer)

    def __pre_line(self) -> None:
        if self.cycle == 1:
            self.registers.ppustatus.vblank_flag = 0

    def __visible_line(self) -> None:
        if self.cycle == 0:
            # Draw the entire scanline at once
            self.background_renderer.render_scanline()

    def __vblank_line(self, on_interrupt: Callable[[int], None]) -> None:
        if self.cycle == 1:
            self.registers.ppustatus.vblank_flag = 1

            if self.registers.ppuctrl.nmi_enable == 1:
                on_interrupt(Interrupt.NMI)
