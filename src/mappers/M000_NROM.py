from src.mappers.Mapper import Mapper


class NROM(Mapper):
    def cpu_read(self, address: int) -> int | None:
        if 0x4020 <= address <= 0x5FFF:
            # Unused
            return None
        elif 0x6000 <= address <= 0x7FFF:
            # CPU $6000-$7FFF: Unbanked PRG-RAM, mirrored as necessary to fill entire 8 KiB window,
            # write protectable with an external switch. (Family BASIC only)
            size = self._cartridge.header.prg_ram_size
            if size != 0:
                return self.__prg_ram[(address - 0x6000) % size]
        elif 0x8000 <= address <= 0xBFFF:
            # CPU $8000-$BFFF: First 16 KB of PRG-ROM
            return self.get_prg_page(0)[(address - 0x8000) % self.prg_rom_page_size()]
        elif 0xC000 <= address <= 0xFFFF:
            # CPU $C000-$FFFF: Last 16 KB of PRG-ROM (or mirror of $8000-$BFFF)
            return self.get_prg_page(1)[(address - 0xC000) % self.prg_rom_page_size()]

    def cpu_write(self, address: int, value: int) -> None:
        if 0x6000 <= address <= 0x7FFF:
            # CPU $6000-$7FFF: Unbanked PRG-RAM, mirrored as necessary to fill entire 8 KiB window,
            # write protectable with an external switch. (Family BASIC only)
            size = self._cartridge.header.prg_ram_size
            if size != 0:
                self.__prg_ram[(address - 0x6000) % size] = value

    def ppu_read(self, address: int) -> int | None:
        return self.get_chr_page(0)[address]

    def ppu_write(self, address: int, value: int) -> int:
        if not self._cartridge.header.uses_chr_ram:
            # Only CHR-RAM is writeable
            return

        # PPU $0000-$1FFF: 8 KB of CHR-RAM
        self.get_chr_page(0)[address] = value

    def on_load(self):
        # For Family BASIC
        self.__prg_ram = bytearray(0x2000)
