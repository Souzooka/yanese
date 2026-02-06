from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from src.util import byte

if TYPE_CHECKING:
    from src.controllers.ControllerBase import ControllerBase
    from src.mappers.Mapper import Mapper


class CPUMemory:
    """
    Handles the main system memory accessible by the CPU.
    https://www.nesdev.org/wiki/CPU_memory_map
    """

    __slots__ = ["__ppu", "__apu", "__controllers", "__mapper", "__wram", "__open_bus_value"]

    __controllers: Optional[List[ControllerBase]]
    __mapper: Optional[Mapper]

    def __init__(self):
        self.__ppu = None
        self.__apu = None
        self.__controllers = None
        self.__mapper = None

        # The NES has 0x800 bytes of working RAM, and can access addresses from
        # $0000 to $FFFF. These are either this RAM, mirrors of RAM, privileged registers
        # (or mirrors of such), and on-board ROM.
        self.__wram = bytearray(0x800)

        # The last read value from the bus, returned upon read if attempting to read from
        # a non-mapped address
        self.__open_bus_value = 0

    def on_load(self, ppu=None, apu=None, controllers: Optional[List[ControllerBase]] = None, mapper=None):
        self.__ppu = ppu
        self.__apu = apu
        self.__controllers = controllers
        self.__mapper = mapper

    def read(self, address: int) -> int:
        value = self.get_open_bus_value()

        if 0x0000 <= address <= 0x1FFF:
            # $0000-$0800 is WRAM; every 0x800 bytes following up to $1FFF
            # is mirrored/repeated.
            address &= 0x7FF
            value = self.__wram[address]

        elif address == 0x4016 or address == 0x4017:
            # $4016 = controller port 0
            # $4017 = controller port 1
            controller_value = 0
            if self.__controllers is not None:
                controller_value = self.__controllers[address - 0x4016].on_read()
            # A controller read only affects bits 0-4,
            # So we need to mask bits 5-7 of the open bus in
            value &= 0b11100000
            controller_value &= 0b00011111
            value = value | controller_value

        elif 0x4020 <= address <= 0xFFFF:
            # $4020-$FFFF maps to the cartridge board, which can pretty much do whatever it wants
            if self.__mapper is not None:
                # NOTE: The mapper's cpu_read function may return None if the program reads from an unmapped
                # address; this is handled at the bottom of the function where we return the open bus value
                # (which is just the last read value from the CPU bus)
                value = self.__mapper.cpu_read(address)

        # Test for open bus, i.e. we read from nowhere actually mapped.
        # https://www.nesdev.org/wiki/Open_bus_behavior
        if value is None:
            # TODO: Probably want to log this behavior later.
            value = self.get_open_bus_value()
        else:
            self.set_open_bus_value(value)
        return byte.to_u8(value)

    def read16(self, address: int) -> int:
        return self.read(address) | (self.read(address + 1) << 8)

    def write(self, address: int, value: int) -> None:
        value = byte.to_u8(value)

        if 0x0000 <= address <= 0x1FFF:
            # $0000-$07FF is WRAM; every 0x800 bytes following up to $1FFF
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
                return self.__mapper.cpu_write(address, value)

        # If we get down here (after mapping everything)
        # something has gone seriously wrong
        return

    def write16(self, address: int, value: int) -> None:
        lo = value & 0xFF
        hi = (value >> 8) & 0xFF
        self.write(address, lo)
        self.write(address + 1, hi)

    def get_open_bus_value(self) -> int:
        return self.__open_bus_value

    def set_open_bus_value(self, value: int) -> None:
        self.__open_bus_value = value

    def __invalid_save_state(self, msg: str = "") -> None:
        raise TypeError("Invalid save state" + f": {msg}" if msg else "")

    def __validate_save_state(self, state: Dict[Any, str]) -> Tuple[bool, str]:
        wram = state["wram"]
        open_bus_value = state["open_bus"]

        if type(wram) is not list:
            return False, ""
        if not all(type(v) is int for v in wram):
            return False, ""
        if len(wram) != len(self.__wram):
            return False, ""
        if type(open_bus_value) is not int or open_bus_value != byte.to_u8(open_bus_value):
            return False, ""
        return True, ""

    def get_save_state(self) -> Dict[Any, str]:
        return {
            # Need to make sure to take a copy here, otherwise
            # future writes to CPUMemory will mutate this savestate
            "wram": list(self.__wram),
            "open_bus": self.__open_bus_value,
        }

    def set_save_state(self, state: Dict[Any, str]) -> None:
        valid, msg = self.__validate_save_state(state)
        if not valid:
            self.__invalid_save_state(msg)

        self.__wram = bytearray(state["wram"])
        self.__open_bus_value = state["open_bus"]
