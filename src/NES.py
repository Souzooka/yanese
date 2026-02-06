from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.Cartridge import Cartridge
from src.controllers.Controller import Controller
from src.cpu.CPU import CPU
from src.CPUMemory import CPUMemory
from src.interrupts import Interrupt
from src.mappers.mappers import create_mapper
from src.ppu.PPU import PPU

if TYPE_CHECKING:
    from io import FileIO


class NES:
    """
    Represents an NES console.
    """

    PPU_CYCLES_PER_CPU_CYCLE = 3.0
    APU_CYCLES_PER_CPU_CYCLE = 0.5

    def __init__(self) -> None:
        self.__cartridge: Optional[Cartridge] = None
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)
        self.__controllers = [controller0, controller1]
        self.__cpu = CPU(CPUMemory())
        self.__ppu = PPU(self.__cpu)

        self.__debt_ppu_cycles = 0.0
        self.__debt_apu_cycles = 0.0

    def load_cartridge(self, cartridge_file: FileIO) -> None:
        self.__cartridge = Cartridge(cartridge_file.read())
        mapper = create_mapper(self, None, self.__cartridge)

        self.__cpu.memory.on_load(ppu=self.__ppu, apu=None, controllers=self.__controllers, mapper=mapper)
        self.__ppu.on_load(self.__cartridge, mapper)

        # Kick the CPU
        self.__cpu.interrupt(Interrupt.RESET)

    def __step(self, on_frame, on_interrupt) -> int:
        cpu_cycles = self.__cpu.step()

        # Calculate how many cycles to run the PPU for
        # based on the amount of CPU cycles we did
        _ppu_cycles = cpu_cycles * NES.PPU_CYCLES_PER_CPU_CYCLE
        self.__debt_ppu_cycles += _ppu_cycles % 1.0
        ppu_cycles = int(_ppu_cycles)
        if self.__debt_ppu_cycles >= 1.0:
            ppu_cycles += int(self.__debt_ppu_cycles)
            self.__debt_ppu_cycles %= 1.0

        for _ in range(ppu_cycles):
            self.__ppu.step(on_frame, on_interrupt)

    def __interrupt_cb(self, interrupt_id: int):
        cycles = self.__cpu.interrupt(interrupt_id)
        self.__debt_ppu_cycles += cycles * NES.PPU_CYCLES_PER_CPU_CYCLE
        self.__debt_apu_cycles += cycles * NES.APU_CYCLES_PER_CPU_CYCLE

    def run(self, on_frame):
        """
        Runs the emulated NES for one frame.
        """
        curr_frame = self.__ppu.frame
        while self.__ppu.frame == curr_frame:
            self.__step(on_frame, self.__interrupt_cb)
