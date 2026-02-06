from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.Cartridge import Cartridge
    from src.cpu.CPU import CPU


class Mapper(ABC):
    def __init__(self, cpu: CPU, ppu, cartridge: Cartridge) -> None:
        self._cpu = cpu
        self._ppu = ppu
        self._cartridge = cartridge

        prg = self._cartridge.prg()
        chr = self._cartridge.chr()
        total_prg_pages = len(prg) // self.prg_rom_page_size()
        total_chr_pages = len(chr) // self.chr_rom_page_size()

        self.__prg_pages = [self._get_page(prg, self.prg_rom_page_size(), i) for i in range(total_prg_pages)]
        self.__chr_pages = [self._get_page(chr, self.chr_rom_page_size(), i) for i in range(total_chr_pages)]

        self.on_load()

    def prg_rom_page_size(self) -> int:
        """
        Returns the PRG-ROM page size in bytes.
        """
        if self._cartridge.header.prg_nvram_size is None:
            return 0x4000
        return self._cartridge.header.prg_nvram_size

    def chr_rom_page_size(self) -> int:
        """
        Returns the CHR-ROM page size in bytes.
        """
        if self._cartridge.header.chr_nvram_size is None:
            return 0x2000
        return self._cartridge.header.chr_nvram_size

    @abstractmethod
    def cpu_read(self, address: int) -> int | None:
        """
        Maps a CPU read operation (addresses $4020-$FFFF)
        """
        pass

    @abstractmethod
    def cpu_write(self, address: int, value: int) -> None:
        """
        Maps a CPU write operation (addresses $4020-$FFFF)
        """
        pass

    @abstractmethod
    def ppu_read(self, address: int) -> int | None:
        """
        Maps a PPU read operation (addresses $0000-$1FFF)
        """
        pass

    @abstractmethod
    def ppu_write(self, address: int, value: int) -> None:
        """
        Maps a PPU write operation (addresses $0000-$1FFF)
        """
        pass

    def tick(self):
        pass

    def on_load(self):
        pass

    def _get_page(self, buf: bytes, page_size: int, page: int) -> bytearray:
        offset = page * page_size
        return bytearray(buf[offset : offset + page_size])

    def get_prg_page(self, page: int) -> bytearray:
        return self.__prg_pages[page % len(self.__prg_pages)]

    def get_chr_page(self, page: int) -> bytearray:
        return self.__chr_pages[page % len(self.__chr_pages)]
