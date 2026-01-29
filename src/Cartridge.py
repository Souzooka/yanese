from __future__ import annotations

from collections.abc import Collection
from enum import IntEnum, auto, unique
from typing import Optional

import util.byte as byte
from util.console_types import ConsoleType
from util.mirroring_modes import MirroringMode
from util.timing_modes import TimingMode

# Should be the first four bytes of any valid NES ROM
MAGIC = bytes([0x4E, 0x45, 0x53, 0x1A])


class Cartridge:
    @unique
    class Format(IntEnum):
        INVALID = auto()
        INES = auto()
        NES2 = auto()

    class Header:
        def __init__(self, data: Collection) -> None:
            # https://www.nesdev.org/wiki/INES#iNES_file_format - INES
            # https://www.nesdev.org/wiki/NES_2.0#Header - NES2
            self.__magic = data[0:4]

            # Determine ROM format (NOTE: NES2 is backwards compatible to INES, the simpler format)
            self.format: Optional[Cartridge.Format] = None
            self.format = Cartridge.Format.INES if self.is_valid() else Cartridge.Format.INVALID

            if self.format == Cartridge.Format.INES and data[7] & 0xC == 0x8:
                self.format = Cartridge.Format.NES2

            # INES stuff
            self.prg_rom_pages = data[4]
            self.chr_rom_pages = data[5]
            self.uses_chr_ram = self.chr_rom_pages == 0
            self.has_prg_ram = byte.get_flag(data[6], 1)
            self.prg_ram_size = 0x2000  # 8 KB by default
            self.chr_ram_size = 0x2000  # 8 KB by default
            # This is the "trainer" data which seems to go unused today
            self.has_trainer_data = byte.get_flag(data[6], 2)
            self.mirroring_mode = MirroringMode.VERTICAL if byte.get_flag(data[6], 0) else MirroringMode.HORIZONTAL
            self.mirroring_mode = MirroringMode.FOUR_SCREEN if byte.get_flag(data[6], 3) else self.mirroring_mode
            self.mapper_id = byte.build_u8(byte.upper_nibble(data[6]), byte.upper_nibble(data[7]))

            # NES2 stuff
            nes2 = self.format == Cartridge.Format.NES2
            self.console_type = ConsoleType(byte.get_bits(data[7], 0, 2)) if nes2 else ConsoleType.NES
            self.mapper_id = self.mapper_id | (byte.lower_nibble(data[8]) << 8) if nes2 else self.mapper_id
            self.sub_mapper_id = byte.upper_nibble(data[8]) if nes2 else None
            self.prg_rom_pages = self.prg_rom_pages | (byte.lower_nibble(data[9]) << 8) if nes2 else self.prg_rom_pages
            self.chr_rom_pages = self.chr_rom_pages | (byte.upper_nibble(data[9]) << 8) if nes2 else self.chr_rom_pages
            self.prg_nvram_size = 0 if nes2 else None
            self.chr_nvram_size = 0 if nes2 else None
            if nes2:
                prg_ram_shift = byte.lower_nibble(data[10])
                prg_nvram_shift = byte.upper_nibble(data[10])
                chr_ram_shift = byte.lower_nibble(data[11])
                chr_nvram_shift = byte.upper_nibble(data[11])

                if prg_ram_shift != 0:
                    self.prg_ram_size = 64 << prg_ram_shift
                if prg_nvram_shift != 0:
                    self.prg_nvram_size = 64 << prg_nvram_shift
                if chr_ram_shift != 0:
                    self.chr_ram_size = 64 << chr_ram_shift
                if chr_nvram_shift != 0:
                    self.chr_nvram_size = 64 << chr_nvram_shift
            self.timing_mode = TimingMode(byte.get_bits(data[12], 0, 2)) if nes2 else TimingMode.RP2C02

            self.vs_ppu_type = None
            self.vs_hardware_type = None
            if self.console_type == ConsoleType.VS:
                self.vs_ppu_type = byte.lower_nibble(data[13])
                self.vs_hardware_type = byte.upper_nibble(data[13])

            self.extended_console_type = None
            if self.console_type == ConsoleType.EXTENDED:
                self.extended_console_type = byte.lower_nibble(data[13])

            self.misc_roms_present = byte.get_bits(data[14], 0, 2) if nes2 else None
            self.default_expansion_device = byte.get_bits(data[15], 0, 6) if nes2 else None

        def is_valid(self) -> bool:
            if self.format is not None and self.format != Cartridge.Format.INVALID:
                return True

            for i in range(len(MAGIC)):
                if self.__magic[i] != MAGIC[i]:
                    return False
            return True

    def __init__(self, data: Collection) -> None:
        self.__data = data
        self.header = Cartridge.Header(data)

    def is_valid(self) -> bool:
        return self.header.is_valid()
