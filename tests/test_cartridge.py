from src.Cartridge import Cartridge


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
