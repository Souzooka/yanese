from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.controllers.ControllerBase import ControllerBase

ALLOW_OPEN_BUS = False


class CPUMemory:
    """
    Handles the main system memory accessible by the CPU.
    https://www.nesdev.org/wiki/CPU_memory_map
    """

    __controllers: Optional[List[ControllerBase]]

    def __init__(self):
        self.__ppu = None
        self.__apu = None
        self.__controllers = None
        self.__mapper = None

        # The NES has 0x800 bytes of working RAM, and can access addresses from
        # $0000 to $FFFF. These are either this RAM, mirrors of RAM, privileged registers
        # (or mirrors of such), and on-board ROM.
        self.__wram = bytearray(0x800)

    def on_load(self, ppu=None, apu=None, controllers: Optional[List[ControllerBase]] = None, mapper=None):
        self.__ppu = ppu
        self.__apu = apu
        self.__controllers = controllers
        self.__mapper = mapper

    def on_read(self, address: int) -> Optional[int]:
        if 0x0000 <= address <= 0x1FFF:
            # $0000-$0800 is WRAM; every 0x800 bytes following up to $1FFF
            # is mirrored/repeated.
            address &= 0x7FF
            return self.__wram[address]

        if address == 0x4016:
            # $4016 = controller port 0
            if self.__controllers is not None:
                return self.__controllers[0].on_read()

        if address == 0x4017:
            # $4017 = controller port 1
            if self.__controllers is not None:
                return self.__controllers[1].on_read()

        if 0x4020 <= address <= 0xFFFF:
            # $4020-$FFFF maps to the cartridge board, which can pretty much do whatever it wants
            if self.__mapper is not None:
                # We allow the mapper to return None if attempting to read
                # unmapped addresses. This causes a behavior which a few games
                # rely on (but we'll probably boldly ignore and pretend it doesn't exist)
                # https://www.nesdev.org/wiki/Open_bus_behavior
                value = self.__mapper.on_read(address)
                if value is None:
                    # probably want to log this somewhere when that's implemented
                    if not ALLOW_OPEN_BUS:
                        value = 0
                return value

        # If we get down here (after mapping everything)
        # something has gone seriously wrong
        return 0

    def on_write(self, address: int, value: int) -> None:
        if 0x0000 <= address <= 0x1FFF:
            # $0000-$0800 is WRAM; every 0x800 bytes following up to $1FFF
            # is mirrored/repeated.
            address &= 0x7FF
            self.__wram[address] = value
            return

        if address == 0x4016:
            # $4016 = controller port 0
            if self.__controllers[0] is not None:
                return self.__controllers[0].on_write(value)

        if address == 0x4017:
            # $4017 = APU frame counter
            pass

        if 0x4020 <= address <= 0xFFFF:
            # $4020-$FFFF maps to the cartridge board, which can pretty much do whatever it wants
            if self.__mapper is not None:
                return self.__mapper.on_write(address, value)

        # If we get down here (after mapping everything)
        # something has gone seriously wrong
        return

    def get_save_state(self) -> Dict[Any, str]:
        return {
            # Need to make sure to take a copy here, otherwise
            # future writes to CPUMemory will mutate this savestate
            "wram": list(self.__wram)
        }

    def set_save_state(self, state: Dict[Any, str]):
        self.__wram = state["wram"]
