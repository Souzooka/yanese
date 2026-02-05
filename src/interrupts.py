class Interrupt:
    BRK = 0
    IRQ = 1
    NMI = 2
    RESET = 3

    def __init__(self, _id: int, vector: int, b_flag: bool) -> None:
        self.id = _id
        self.vector = vector
        self.b_flag = b_flag


interrupts = {
    # Software interrupt (via BRK instruction)
    Interrupt.BRK: Interrupt(Interrupt.BRK, vector=0xFFFE, b_flag=True),
    # Maskable interrupt request (usually triggered via cartridge)
    Interrupt.IRQ: Interrupt(Interrupt.IRQ, vector=0xFFFE, b_flag=False),
    # Non-maskable interrupt (triggered via PPU during VBlank)
    Interrupt.NMI: Interrupt(Interrupt.NMI, vector=0xFFFA, b_flag=False),
    # Reset (triggered upon power on or reset)
    Interrupt.RESET: Interrupt(Interrupt.RESET, vector=0xFFFC, b_flag=False),
}
