from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.Cartridge import Cartridge
from src.controllers.Controller import Controller
from src.cpu.CPU import CPU
from src.CPUMemory import CPUMemory
from src.interrupts import Interrupt
from src.mappers.mappers import create_mapper

if TYPE_CHECKING:
    from io import FileIO


class NES:
    """
    Represents an NES console.
    """

    # TEMP
    CPU_CYCLES_PER_FRAME = 29781

    def __init__(self) -> None:
        self.__cartridge: Optional[Cartridge] = None
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)
        self.__controllers = [controller0, controller1]
        self.__cpu = CPU(CPUMemory())

    def load_cartridge(self, cartridge_file: FileIO) -> None:
        self.__cartridge = Cartridge(cartridge_file.read())
        mapper = create_mapper(self, None, self.__cartridge)

        # Kick the CPU
        self.__cpu.memory.on_load(ppu=None, apu=None, controllers=self.__controllers, mapper=mapper)
        self.__cpu.interrupt(Interrupt.RESET)

    def __step(self) -> int:
        return self.__cpu.step()

    def run(self):
        """
        Runs the emulated NES for one frame.
        """
        cycles = NES.CPU_CYCLES_PER_FRAME
        while cycles > 0:
            cycles -= self.__step()
