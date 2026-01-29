from src.Cartridge import Cartridge
from src.util.console_types import ConsoleType
from src.util.mirroring_modes import MirroringMode
from src.util.timing_modes import TimingMode


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
        data = bytearray(list(TestCartridge.MAGIC) + [0] * 12)

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
        assert header.has_trainer_data
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
        assert not header.has_trainer_data
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
        assert header.has_trainer_data
        assert header.mirroring_mode == MirroringMode.VERTICAL
        assert header.mapper_id == 0

    def test_nes2_header(self):
        # for byte 7, bit 2 being set and bit 3 being clear indicates NES2 format (data[7] & 0xC == 0x8)
        BLANK_NES2_HEADER = bytearray(list(TestCartridge.MAGIC) + [0] * 3 + [0x8] + [0] * 8)

        # Near blank valid NES2 header
        data = bytearray(BLANK_NES2_HEADER)
        data[15] = 1  # Expects standard NES controller
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.NES2
        assert header.default_expansion_device == 1

        # maximum power!!
        data = bytearray(BLANK_NES2_HEADER)
        data[4:15] = [0xFF] * 12
        data[7] = 0xFB
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.NES2
        assert header.prg_rom_pages == 0xFFF
        assert header.chr_rom_pages == 0xFFF
        assert not header.uses_chr_ram
        assert header.has_prg_ram
        assert header.prg_ram_size == 64 << 0xF
        assert header.chr_ram_size == 64 << 0xF
        assert header.has_trainer_data
        assert header.mirroring_mode == MirroringMode.FOUR_SCREEN
        assert header.mapper_id == 0xFFF
        assert header.console_type == ConsoleType.EXTENDED
        assert header.sub_mapper_id == 0xF
        assert header.prg_nvram_size == 64 << 0xF
        assert header.chr_nvram_size == 64 << 0xF
        assert header.timing_mode == TimingMode.UA6538
        assert header.vs_ppu_type is None
        assert header.vs_hardware_type is None
        assert header.extended_console_type == 0xF
        assert header.misc_roms_present == 0x3
        # NOTE: NESDEV says only 6 bits used here, but also specifies devices up to 0x4F.
        assert header.default_expansion_device == 0x3F

        # Above w/ VS. system console set
        data = bytearray(BLANK_NES2_HEADER)
        data[4:15] = [0xFF] * 12
        data[7] = 0xF9
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.NES2
        assert header.prg_rom_pages == 0xFFF
        assert header.chr_rom_pages == 0xFFF
        assert not header.uses_chr_ram
        assert header.has_prg_ram
        assert header.prg_ram_size == 64 << 0xF
        assert header.chr_ram_size == 64 << 0xF
        assert header.has_trainer_data
        assert header.mirroring_mode == MirroringMode.FOUR_SCREEN
        assert header.mapper_id == 0xFFF
        assert header.console_type == ConsoleType.VS
        assert header.sub_mapper_id == 0xF
        assert header.prg_nvram_size == 64 << 0xF
        assert header.chr_nvram_size == 64 << 0xF
        assert header.timing_mode == TimingMode.UA6538
        assert header.vs_hardware_type == 0xF
        assert header.vs_ppu_type == 0xF
        assert header.extended_console_type is None
        assert header.misc_roms_present == 0x3
        # NOTE: NESDEV says only 6 bits used here, but also specifies devices up to 0x4F.
        assert header.default_expansion_device == 0x3F

        # INES format sets properly sets INES variables/ignores NES2 even if bytes 7-15 are fully utilized
        data = bytes(list(TestCartridge.MAGIC) + [0xFF] * 12)
        cartridge = Cartridge(data)
        header = cartridge.header
        assert header.format == Cartridge.Format.INES
        assert header.prg_rom_pages == 0xFF
        assert header.chr_rom_pages == 0xFF
        assert not header.uses_chr_ram
        assert header.has_prg_ram
        assert header.prg_ram_size == 0x2000
        assert header.chr_ram_size == 0x2000
        assert header.has_trainer_data
        assert header.mirroring_mode == MirroringMode.FOUR_SCREEN
        assert header.mapper_id == 0xFF
        assert header.console_type == ConsoleType.NES
        assert header.sub_mapper_id is None
        assert header.prg_nvram_size is None
        assert header.chr_nvram_size is None
        assert header.timing_mode == TimingMode.RP2C02
        assert header.vs_hardware_type is None
        assert header.vs_ppu_type is None
        assert header.extended_console_type is None
        assert header.misc_roms_present is None
        assert header.default_expansion_device is None

    def test_save_state(self):
        # Unlike most components, Cartridge shouldn't be modified upon loading savestate
        # Instead, the cartridge state should just be used to help verify that
        # a correct savestate is being used

        data = bytes(list(TestCartridge.MAGIC) + list(range(0, 256)))
        cartridge = Cartridge(data)

        # Should actually have the savestate function
        assert hasattr(cartridge, "get_save_state")
        assert callable(cartridge.get_save_state)

        # No set_save_state (don't call this one accidentally)
        assert not hasattr(cartridge, "set_save_state")

        # And return a dictionary with a checksum key
        state = cartridge.get_save_state()
        assert "checksum" in state

        # Actual checksum value is an implementation detail and may/may not change
        # It should, of course, match the value provided by the Cartridge.checksum function
        assert state["checksum"] == cartridge.checksum()
