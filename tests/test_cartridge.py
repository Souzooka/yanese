from src.Cartridge import Cartridge
from src.util.mirroring_modes import MirroringMode


class TestCartridge:
    MAGIC = bytes([0x4E, 0x45, 0x53, 0x1A])

    def test_valid_cartridge(self):
        header = bytes(list(TestCartridge.MAGIC) + [0] * 12)
        cartridge = Cartridge(header)

        assert cartridge.is_valid(), "Cartridge should be valid when passed valid header."

    def test_invalid_cartridge(self):
        header = bytes([0, 1, 2, 3] + [0] * 12)
        cartridge = Cartridge(header)

        assert not cartridge.is_valid(), "Cartridge should be invalid when passed invalid header."

        header = bytes([0xAA, 0x92, 0x12, 0x11] + [0] * 12)
        cartridge = Cartridge(header)

        assert not cartridge.is_valid(), "Cartridge should be invalid when passed invalid header."

        header = bytes(list(reversed(TestCartridge.MAGIC)) + [0] * 12)
        cartridge = Cartridge(header)

        assert not cartridge.is_valid(), "Cartridge should be invalid when passed invalid header."

    def test_ines_header(self):
        data = bytearray([0x4E, 0x45, 0x53, 0x1A] + [0] * 12)

        data[4] = 0x20  # 32 PRG-ROM pages
        data[5] = 0x20  # 32 CHR-ROM pages
        data[6] = 0b01001111  # FOUR_SCREEN (redundant bit0), has PRG-RAM, has 512-byte padding, mapper 4
        data[7] = 0x0
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.INES
        assert header.prg_rom_pages == 0x20
        assert header.chr_rom_pages == 0x20
        assert not header.uses_chr_ram
        assert header.has_prg_ram
        assert header.prg_ram_size == 0x2000
        assert header.chr_ram_size == 0x2000
        assert header.has_512_byte_padding
        assert header.mirroring_mode == MirroringMode.FOUR_SCREEN
        assert header.mapper_id == 4

        data[4] = 0  # 0 PRG-ROM pages
        data[5] = 0  # 0 CHR-ROM pages
        data[6] = 0b10000000  # HORIZONTAL, no PRG-RAM, no 512 byte padding
        data[7] = 0b11000000  # 0b11001000 = mapper 200
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.INES
        assert header.prg_rom_pages == 0x0
        assert header.chr_rom_pages == 0x0
        assert header.uses_chr_ram
        assert not header.has_prg_ram
        assert header.prg_ram_size == 0x2000
        assert header.chr_ram_size == 0x2000
        assert not header.has_512_byte_padding
        assert header.mirroring_mode == MirroringMode.HORIZONTAL
        assert header.mapper_id == 200

        data[4] = 0x40  # 64 PRG-ROM pages
        data[5] = 0x80  # 128 CHR-ROM pages
        data[6] = 0b00000101  # VERTICAL, no PRG-RAM, 512 byte padding
        data[7] = 0b00000000  # mapper 0
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.INES
        assert header.prg_rom_pages == 0x40
        assert header.chr_rom_pages == 0x80
        assert not header.uses_chr_ram
        assert not header.has_prg_ram
        assert header.prg_ram_size == 0x2000
        assert header.chr_ram_size == 0x2000
        assert header.has_512_byte_padding
        assert header.mirroring_mode == MirroringMode.VERTICAL
        assert header.mapper_id == 0

    def test_nes2_header(self):
        # TODO
        pass
