from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from src.util import byte

if TYPE_CHECKING:
    from src.cpu.CPU import CPU

# https://www.nesdev.org/wiki/CPU_addressing_modes

# TEMPORARY
class UnsupportedAddressing(RuntimeError):
    pass


class _AddressingModes:
    # Container for logic for resolving instruction arguments

    @staticmethod
    def unsupported(cpu: CPU, input: int, page_cross_penalty: bool) -> None:
        # TODO: Log error here
        # Try to avoid raising here, probably should be handled explicitly by CPU
        raise UnsupportedAddressing("Unsupported addressing mode")
        return None

    """
    IMPLICIT
    EX: INC
    """

    @staticmethod
    def IMPLICIT_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return 0

    @staticmethod
    def IMPLICIT_value(cpu: CPU, value: int, page_cross_penalty: bool) -> int:
        return 0

    """
    IMMEDIATE
    EX: LDA #10
    """

    IMMEDIATE_address = unsupported

    @staticmethod
    def IMMEDIATE_value(cpu: CPU, value: int, page_cross_penalty: bool) -> int:
        return value

    """
    ABSOLUTE
    EX: JMP $1234
    """

    @staticmethod
    def ABSOLUTE_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return address

    @staticmethod
    def ABSOLUTE_value(cpu: CPU, value: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.ABSOLUTE_address(cpu, value, page_cross_penalty))

    """
    ZERO_PAGE
    EX: LDA $10
    """

    @staticmethod
    def ZERO_PAGE_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return address

    @staticmethod
    def ZERO_PAGE_value(cpu: CPU, value: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.ZERO_PAGE_address(cpu, value, page_cross_penalty))

    """
    RELATIVE
    EX: BNE *+4
    """

    @staticmethod
    def RELATIVE_address(cpu: CPU, offset: int, page_cross_penalty: bool) -> int:
        # The CPU attempts an 8-bit addition of the address and offset
        # If a carry occurs, another cycle occurs in which that carry is
        # added to the upper 8-bit of the new 16-bit address.
        # (In the case of relative addressing instructions, this penalty
        # actually only occurs in the event of a successful branch, which
        # we will check for later and clear if needed in the interpreter)
        old_address = cpu.pc.get_value()
        new_address = byte.to_u16(old_address + byte.to_s8(offset))
        if page_cross_penalty and byte.high_byte_of(old_address) != byte.high_byte_of(new_address):
            cpu.extra_cycles += 1

        return new_address

    RELATIVE_value = unsupported

    """
    INDIRECT
    EX: JMP ($0214) -> jumps to 16-bit address stored at $0214
    """

    @staticmethod
    def INDIRECT_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        # Unlike relative addressing, the CPU never adds the carry if a page cross
        # occurs. This means that JMP ($30FF) will fetch the low byte from $30FF
        # and the high byte from $3000. No page cross penalties! Though we still
        # have to handle the wraparound behavior.
        # http://www.6502.org/tutorials/6502opcodes.html#JMP
        lo = cpu.memory.read(address)
        hi = cpu.memory.read(byte.build_u16(byte.low_byte_of(address + 1), byte.high_byte_of(address)))
        return byte.build_u16(lo, hi)

    INDIRECT_value = unsupported

    """
    INDEXED_ZERO_PAGE_X
    EX: STY $10,X -> Y is stored at $10+X
    """

    @staticmethod
    def INDEXED_ZERO_PAGE_X_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        # Note that the address wraps around to the zero page, e.g. 0xFF + 0x80 is 0x7F, not 0x17F
        # (We also never have a page cross penalty as such)
        return byte.to_u8(address + cpu.x.get_value())

    @staticmethod
    def INDEXED_ZERO_PAGE_X_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDEXED_ZERO_PAGE_X_address(cpu, address, page_cross_penalty))

    """
    INDEXED_ZERO_PAGE_Y
    EX: STX $10,Y -> X is stored at $10+Y
    """

    @staticmethod
    def INDEXED_ZERO_PAGE_Y_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        # Note that the address wraps around to the zero page, e.g. 0xFF + 0x80 is 0x7F, not 0x17F
        # (We also never have a page cross penalty as such)
        return byte.to_u8(address + cpu.y.get_value())

    @staticmethod
    def INDEXED_ZERO_PAGE_Y_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDEXED_ZERO_PAGE_Y_address(cpu, address, page_cross_penalty))

    """
    INDEXED_ABSOLUTE_X
    EX: STY $1000,X -> Y is stored at $1000+X
    """

    @staticmethod
    def INDEXED_ABSOLUTE_X_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        old_address = address
        new_address = byte.to_u16(address + cpu.x.get_value())
        if page_cross_penalty and byte.high_byte_of(old_address) != byte.high_byte_of(new_address):
            cpu.extra_cycles += 1
        return new_address

    @staticmethod
    def INDEXED_ABSOLUTE_X_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDEXED_ABSOLUTE_X_address(cpu, address, page_cross_penalty))

    """
    INDEXED_ABSOLUTE_Y
    EX: STX $1000,Y -> X is stored at $1000+Y
    """

    @staticmethod
    def INDEXED_ABSOLUTE_Y_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        old_address = address
        new_address = byte.to_u16(address + cpu.y.get_value())
        if page_cross_penalty and byte.high_byte_of(old_address) != byte.high_byte_of(new_address):
            cpu.extra_cycles += 1
        return new_address

    @staticmethod
    def INDEXED_ABSOLUTE_Y_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDEXED_ABSOLUTE_Y_address(cpu, address, page_cross_penalty))

    """
    INDEXED_INDIRECT
    EX: LDA ($40,X) -> read 16-bit address from $40 + X (address) -> read 8-bit value from address (value)
    """

    @staticmethod
    def INDEXED_INDIRECT_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        # Zero page wraparound occurs here
        address += cpu.x.get_value()
        lo = cpu.memory.read(byte.to_u8(address))
        hi = cpu.memory.read(byte.to_u8(address + 1))
        return byte.build_u16(lo, hi)

    @staticmethod
    def INDEXED_INDIRECT_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDEXED_INDIRECT_address(cpu, address, page_cross_penalty))

    """
    INDIRECT_INDEXED
    EX: LDA ($40),Y -> A is loaded from (the 16-bit address at $40 + Y)
    """

    @staticmethod
    def INDIRECT_INDEXED_address(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        # Zero page wraparound occurs here
        lo = cpu.memory.read(address)
        hi = cpu.memory.read(byte.to_u8(address + 1))
        base_address = byte.build_u16(lo, hi)
        final_address = base_address + cpu.y.get_value()

        # If a 16-bit addition is required to resolve the indirection then we take a cycle penalty
        if page_cross_penalty and byte.high_byte_of(base_address) != byte.high_byte_of(final_address):
            cpu.extra_cycles += 1
        return final_address

    @staticmethod
    def INDIRECT_INDEXED_value(cpu: CPU, address: int, page_cross_penalty: bool) -> int:
        return cpu.memory.read(_AddressingModes.INDIRECT_INDEXED_address(cpu, address, page_cross_penalty))


class AddressingMode:
    __slots__ = ["input_size", "get_address", "get_value", "page_cross_penalty"]

    IMPLICIT = 0
    IMMEDIATE = 1
    ABSOLUTE = 2
    ZERO_PAGE = 3
    RELATIVE = 4
    INDIRECT = 5
    INDEXED_ZERO_PAGE_X = 6
    INDEXED_ZERO_PAGE_Y = 7
    INDEXED_ABSOLUTE_X = 8
    INDEXED_ABSOLUTE_Y = 9
    INDEXED_INDIRECT = 10
    INDIRECT_INDEXED = 11

    def __init__(
        self,
        input_size: int,
        get_address: Callable[[CPU, int, bool], int | None],
        get_value: Callable[[CPU, int, bool], int | None],
    ) -> None:
        self.input_size = input_size
        self.get_address = get_address
        self.get_value = get_value


addressing_modes = {
    AddressingMode.IMPLICIT: AddressingMode(
        input_size=0, get_address=_AddressingModes.IMPLICIT_address, get_value=_AddressingModes.IMPLICIT_value
    ),
    AddressingMode.IMMEDIATE: AddressingMode(
        input_size=1, get_address=_AddressingModes.IMMEDIATE_address, get_value=_AddressingModes.IMMEDIATE_value
    ),
    AddressingMode.ABSOLUTE: AddressingMode(
        input_size=2, get_address=_AddressingModes.ABSOLUTE_address, get_value=_AddressingModes.ABSOLUTE_value
    ),
    AddressingMode.ZERO_PAGE: AddressingMode(
        input_size=1, get_address=_AddressingModes.ZERO_PAGE_address, get_value=_AddressingModes.ZERO_PAGE_value
    ),
    AddressingMode.RELATIVE: AddressingMode(
        input_size=1, get_address=_AddressingModes.RELATIVE_address, get_value=_AddressingModes.RELATIVE_value
    ),
    AddressingMode.INDIRECT: AddressingMode(
        input_size=2, get_address=_AddressingModes.INDIRECT_address, get_value=_AddressingModes.INDIRECT_value
    ),
    AddressingMode.INDEXED_ZERO_PAGE_X: AddressingMode(
        input_size=1,
        get_address=_AddressingModes.INDEXED_ZERO_PAGE_X_address,
        get_value=_AddressingModes.INDEXED_ZERO_PAGE_X_value,
    ),
    AddressingMode.INDEXED_ZERO_PAGE_Y: AddressingMode(
        input_size=1,
        get_address=_AddressingModes.INDEXED_ZERO_PAGE_Y_address,
        get_value=_AddressingModes.INDEXED_ZERO_PAGE_Y_value,
    ),
    AddressingMode.INDEXED_ABSOLUTE_X: AddressingMode(
        input_size=2,
        get_address=_AddressingModes.INDEXED_ABSOLUTE_X_address,
        get_value=_AddressingModes.INDEXED_ABSOLUTE_X_value,
    ),
    AddressingMode.INDEXED_ABSOLUTE_Y: AddressingMode(
        input_size=2,
        get_address=_AddressingModes.INDEXED_ABSOLUTE_Y_address,
        get_value=_AddressingModes.INDEXED_ABSOLUTE_Y_value,
    ),
    AddressingMode.INDEXED_INDIRECT: AddressingMode(
        input_size=1,
        get_address=_AddressingModes.INDEXED_INDIRECT_address,
        get_value=_AddressingModes.INDEXED_INDIRECT_value,
    ),
    AddressingMode.INDIRECT_INDEXED: AddressingMode(
        input_size=1,
        get_address=_AddressingModes.INDIRECT_INDEXED_address,
        get_value=_AddressingModes.INDIRECT_INDEXED_value,
    ),
}
