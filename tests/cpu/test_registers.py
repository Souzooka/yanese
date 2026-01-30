from src.cpu.registers import FlagsRegister, Register8Bit, Register16Bit, RegisterBase


class TestRegisters:
    def test_base(self):
        # Attempting to instantiate the base class should raise a TypeError
        # (the derived Register8Bit or Register16Bit should be used instead)
        try:
            register = RegisterBase()
            assert False, "Attempting to instantiate the base class should raise a TypeError"
        except TypeError:
            pass

    def test_8bit(self):
        # Register should be initialized to a value of 0
        register = Register8Bit()

        assert register.get_value() == 0, "Register should be initialized to a value of 0"

        # Should be able to set and get register value
        register.set_value(10)
        assert register.get_value() == 10, "Should be able to set and get register value"

        # Set values should be masked to an 8-bit size
        register.set_value(0x1FF)

        assert register.get_value() == 0xFF, "Set values should be masked to an 8-bit size"

        # Negative values should be converted to unsigned 8-bit
        register.set_value(-2)

        assert register.get_value() == 0xFE, "Negative values should be converted to unsigned 8-bit"

        # Should be able to increment and decrement the register
        register.set_value(10)
        register.increment()
        assert register.get_value() == 11
        register.increment()
        assert register.get_value() == 12
        register.decrement()
        assert register.get_value() == 11
        register.decrement()
        assert register.get_value() == 10

        # Incrementing the register when it is 0xFF should cause a wraparound to 0x00
        register.set_value(0xFF)
        register.increment()

        assert (
            register.get_value() == 0x00
        ), "Incrementing the register when it is 0xFF should cause a wraparound to 0x00"

        # Decrementing the register when it is 0x00 should cause a wraparound to 0xFF
        register.set_value(0x00)
        register.decrement()

        assert (
            register.get_value() == 0xFF
        ), "Decrementing the register when it is 0x00 should cause a wraparound to 0xFF"

    def test_16bit(self):
        # Register should be initialized to a value of 0
        register = Register16Bit()

        assert register.get_value() == 0, "Register should be initialized to a value of 0"

        # Should be able to set and get register value
        register.set_value(10)
        assert register.get_value() == 10, "Should be able to set and get register value"

        # Set values should be masked to an 16-bit size
        register.set_value(0x1FFFF)

        assert register.get_value() == 0xFFFF, "Set values should be masked to an 16-bit size"

        # Negative values should be converted to unsigned 16-bit
        register.set_value(-2)

        assert register.get_value() == 0xFFFE, "Negative values should be converted to unsigned 16-bit"

        # Should be able to increment and decrement the register
        register.set_value(10)
        register.increment()
        assert register.get_value() == 11
        register.increment()
        assert register.get_value() == 12
        register.decrement()
        assert register.get_value() == 11
        register.decrement()
        assert register.get_value() == 10

        # Incrementing the register when it is 0xFFFF should cause a wraparound to 0x0000
        register.set_value(0xFFFF)
        register.increment()

        assert (
            register.get_value() == 0x0000
        ), "Incrementing the register when it is 0xFFFF should cause a wraparound to 0x0000"

        # Decrementing the register when it is 0x0000 should cause a wraparound to 0xFFFF
        register.set_value(0x0000)
        register.decrement()

        assert (
            register.get_value() == 0xFFFF
        ), "Decrementing the register when it is 0x0000 should cause a wraparound to 0xFFFF"

    def test_flags(self):
        # FlagsRegister should have 6 accessible boolean flag properties
        register = FlagsRegister()

        assert hasattr(register, "c")
        assert hasattr(register, "z")
        assert hasattr(register, "i")
        assert hasattr(register, "d")
        assert hasattr(register, "v")
        assert hasattr(register, "n")
        assert type(register.c) is bool
        assert type(register.z) is bool
        assert type(register.i) is bool
        assert type(register.d) is bool
        assert type(register.v) is bool
        assert type(register.n) is bool

        # These should all be False upon initialization
        register = FlagsRegister()

        assert register.c is False
        assert register.z is False
        assert register.i is False
        assert register.d is False
        assert register.v is False
        assert register.n is False

        # Can properly convert the flags status into a u8
        register = FlagsRegister()

        assert register.to_u8() == 0b00110000

        register.c = True
        assert register.to_u8() == 0b00110001
        register.c = False

        register.z = True
        assert register.to_u8() == 0b00110010
        register.z = False

        register.i = True
        assert register.to_u8() == 0b00110100
        register.i = False

        register.d = True
        assert register.to_u8() == 0b00111000
        register.d = False

        register.v = True
        assert register.to_u8() == 0b01110000
        register.v = False

        register.n = True
        assert register.to_u8() == 0b10110000
        register.n = False

        register.c = True
        register.z = True
        register.i = True
        register.d = True
        register.v = True
        register.n = True
        assert register.to_u8() == 0b11111111

        # Passing the optional b_flag argument to to_u8 determines if bit4 is set
        register = FlagsRegister()

        assert register.to_u8(b_flag=True) == 0b00110000
        assert register.to_u8(b_flag=False) == 0b00100000

        # Can set the register state from an integer via from_u8
        flags = [("c", 0), ("z", 1), ("i", 2), ("d", 3), ("v", 6), ("n", 7)]
        for flag, bit_index in flags:
            register = FlagsRegister()
            num = 1 << bit_index
            register.from_u8(num)

            assert getattr(register, flag) is True
            for other_flag, _ in flags:
                if flag == other_flag:
                    continue

                assert getattr(register, other_flag) is False

        register = FlagsRegister()
        register.from_u8(0b11111111)
        assert register.c is True
        assert register.z is True
        assert register.i is True
        assert register.d is True
        assert register.v is True
        assert register.n is True

        # Calling to_u8 with the result of from_u8 should effectively copy the state to the register
        register1 = FlagsRegister()
        register2 = FlagsRegister()

        register1.c = True
        register1.i = True
        register1.v = True
        register2.from_u8(register1.to_u8())
        assert register2.c is True
        assert register2.z is False
        assert register2.i is True
        assert register2.d is False
        assert register2.v is True
        assert register2.n is False

        register1 = FlagsRegister()
        register2 = FlagsRegister()

        register1.z = True
        register1.d = True
        register1.n = True
        register2.from_u8(register1.to_u8())
        assert register2.c is False
        assert register2.z is True
        assert register2.i is False
        assert register2.d is True
        assert register2.v is False
        assert register2.n is True
