from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.util.InMemoryRegister import PPUInMemoryRegister

if TYPE_CHECKING:
    from src.ppu.PPU import PPU


class PPUCtrl(PPUInMemoryRegister):
    nmi_enable: int

    def on_load(self):
        self.add_field("nmi_enable", 7, 1)


class PPUStatus(PPUInMemoryRegister):
    vblank_flag: int

    def on_load(self):
        self.add_field("vblank_flag", 7, 1)


class PPUAddr(PPUInMemoryRegister):
    # https://www.nesdev.org/wiki/PPU_registers#PPUADDR_-_VRAM_address_($2006_write)
    __latch: bool
    address: int

    def on_load(self):
        self.__latch = False
        self.address = 0

    def on_write(self, value: int) -> None:
        if not self.__latch:
            # Write the high byte of the address first
            self.address = (self.address & 0x00FF) | (value << 8)
        else:
            # Now the low byte of the address
            self.address = (self.address & 0xFF00) | value
        self.__latch = not self.__latch


class PPUData(PPUInMemoryRegister):
    # https://www.nesdev.org/wiki/PPU_registers#PPUDATA_-_VRAM_data_($2007_read/write)
    __buffer: int

    def on_load(self) -> None:
        self.__buffer = 0

    def on_read(self) -> None:
        # Reading from PPUDATA does not directly return the value at the current VRAM address,
        # but instead returns the contents of an internal read buffer.
        data = self.__buffer
        address = self.ppu.registers.ppuaddr.address

        # Read from the address specified by PPUADDR
        self.__buffer = self.ppu.memory.read(self.ppu.registers.ppuaddr.address)

        # If the address being read from is $3F00-$3FFF
        # we return the read value immediately
        # (see the "Reading palette RAM" section in the above link)
        if 0x3F00 <= address <= 0x3FFF:
            data = self.__buffer

        return data

    def on_write(self, value: int) -> None:
        # Write the value and increment the address of PPUADDR
        self.ppu.memory.write(self.ppu.registers.ppuaddr.address, value)
        self.__increment_address()

    def __increment_address(self) -> None:
        # TODO
        # PPUCTRL has a flag to increment address by 32,
        # not yet implemented
        address = self.ppu.registers.ppuaddr.address
        address += 1
        address &= 0xFFFF
        self.ppu.registers.ppuaddr.address = address


class VideoRegisters:
    def __init__(self, ppu: PPU) -> None:
        self.ppuctrl = PPUCtrl(ppu)
        self.ppustatus = PPUStatus(ppu)
        self.ppudata = PPUData(ppu)
        self.ppuaddr = PPUAddr(ppu)

    def read(self, address: int) -> Optional[int]:
        register = self.__get_register(address)
        if register is not None:
            return register.on_read()

    def write(self, address: int, value: int) -> None:
        register = self.__get_register(address)
        if register is not None:
            register.on_write(value)

    def __get_register(self, address: int) -> Optional[PPUInMemoryRegister]:
        match address:
            case 0x2000:
                return self.ppuctrl
            case 0x2002:
                return self.ppustatus
            case 0x2006:
                return self.ppuaddr
            case 0x2007:
                return self.ppudata
