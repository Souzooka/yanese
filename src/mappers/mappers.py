from __future__ import annotations

from typing import TYPE_CHECKING

from src.mappers.M000_NROM import NROM
from src.mappers.Mapper import Mapper

if TYPE_CHECKING:
    from src.Cartridge import Cartridge
    from src.cpu.CPU import CPU

__mappers = {
    0: NROM,
}


def create_mapper(cpu: CPU, ppu, cartridge: Cartridge) -> Mapper:
    mapper_id = cartridge.header.mapper_id
    if mapper_id not in __mappers:
        raise TypeError(f"Unknown mapper ID {hex(mapper_id)}")
    return __mappers[mapper_id](cpu, ppu, cartridge)
