from src.controllers.Controller import Controller
from src.cpu.CPU import CPU
from src.CPUMemory import CPUMemory


class TestCPUMemory:
    # Tests for the CPU memory bus

    def test_wram(self):
        # When initializing CPUMemory, $0000-$07FF
        # (and the mirrors at $0800-$1FFF) should be read
        # as a value of 0
        memory = CPUMemory()

        # Main WRAM
        for i in range(0, 0x800):
            assert memory.read(i) == 0x00

        # Mirrors
        for i in range(0x800, 0x2000):
            assert memory.read(i) == 0x00

        # WRAM + mirrors should return back values written to main WRAM region or mirrors
        memory = CPUMemory()

        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x800, 0x1000):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x1000, 0x1800):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x1800, 0x2000):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

    def test_controllers(self):
        # Can read from $4016 and $4017 to poll controller status, and
        # write to $4016 to affect controllers
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)
        memory = CPUMemory()
        memory.on_load(controllers=[controller0, controller1])

        # Hijack the controller on_read and on_write functions to check if they're called
        on_read0_called = False
        on_read1_called = False
        on_write0_called = False
        on_read0 = controller0.on_read
        on_read1 = controller1.on_read
        on_write0 = controller0.on_write

        def read0(*args, **kwargs):
            nonlocal on_read0_called
            on_read0_called = True
            return on_read0(*args, **kwargs)

        def read1(*args, **kwargs):
            nonlocal on_read1_called
            on_read1_called = True
            return on_read1(*args, **kwargs)

        def write0(*args, **kwargs):
            nonlocal on_write0_called
            on_write0_called = True
            return on_write0(*args, **kwargs)

        controller0.on_read = read0
        controller1.on_read = read1
        controller0.on_write = write0

        # Now check the controllers are properly accessed via the CPU memory bus
        memory.read(0x4016)
        assert on_read0_called, "CPU memory bus read ($4016) should read JOY0"
        memory.read(0x4017)
        assert on_read1_called, "CPU memory bus read ($4017) should read JOY1"
        memory.write(0x4016, 1)
        assert on_read0_called, "CPU memory bus write ($4016) should write JOY0"

    def test_read_write16(self):
        # read16/write16 helpers
        memory = CPUMemory()

        # A write of 0x201 to 0x0 should store 0x1 in $0 and 0x2 in $1
        memory.write16(0, 0x201)
        assert memory.read(0) == 0x1
        assert memory.read(1) == 0x2

        # And of course a call to read16 at 0 should return 0x201
        assert memory.read16(0) == 0x201

    def test_save_state(self):
        # Should preserve WRAM here

        # If a state is taken for a new instance of memory, all of WRAM should be 0
        # after restoring the state even after setting memory
        memory = CPUMemory()
        state = memory.get_save_state()
        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)

        memory.set_save_state(state)

        for i in range(0, 0x800):
            assert memory.read(i) == 0x00

        # And the other way around too
        memory = CPUMemory()
        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)
        state = memory.get_save_state()

        for i in range(0, 0x800):
            memory.write(i, 0)

        memory.set_save_state(state)

        for i in range(0, 0x800):
            assert memory.read(i) == i & 0xFF

    def test_invalid_save_state(self):
        # Should raise TypeError if the inputs in the savestate are malformed
        memory = CPUMemory()

        def catch_type_error(memory: CPUMemory, state):
            try:
                memory.set_save_state(state)
                assert False, "CPUMemory accepted malformed savestate"
            except TypeError:
                pass

        # WRAM not a list
        state = memory.get_save_state()
        state["wram"] = "hello world"
        catch_type_error(memory, state)

        # WRAM not a list of integers
        state = memory.get_save_state()
        state["wram"] = list(0.0 for i in range(len(state["wram"])))
        catch_type_error(memory, state)
        state = memory.get_save_state()
        state["wram"][0] = [[[[[1]]]]]
        catch_type_error(memory, state)

        # Open bus not an integer in range 0..FF
        state = memory.get_save_state()
        state["open_bus"] = 0.0
        catch_type_error(memory, state)
        state["open_bus"] = "hi"
        catch_type_error(memory, state)
        state["open_bus"] = -1
        catch_type_error(memory, state)
        state["open_bus"] = 0x100
        catch_type_error(memory, state)


class TestOpenBus:
    def test_open_bus(self):
        # Open bus is a phenomenon where a program reads from a non-mapped address.
        # In this case, the value read from the bus is simply the last read value.
        memory = CPUMemory()

        # Simple test case from https://www.nesdev.org/wiki/Open_bus_behavior
        # NOTE: This relies on the __mapper None check, which may change later.
        memory.write(4, 0xFA)
        memory.write(5, 0x73)

        lo = memory.read(4)
        hi = memory.read(5)
        address = lo | (hi << 8)
        assert memory.read(address) == 0x73

        # read16 should also read the high byte last for proper open bus implementation
        address = memory.read16(4)
        assert memory.read(address) == 0x73

    def test_controllers(self):
        # Controller reads mask in bits 5..7 of the open bus value, since
        # only bits 0..4 are populated in the data bus.
        # This usually means that a read from a controller port
        # actually returns 0x40 or 0x41, depending on if the button is active
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)
        memory = CPUMemory()
        memory.on_load(controllers=[controller0, controller1])
        for i in range(0, 8):
            controller0.set_button(i, 1)

        memory.write(4, 0x16)
        memory.write(5, 0x40)

        address = memory.read16(4)
        assert memory.read(address) == 0x41

    def test_save_state(self):
        # Should preserve the open bus state
        memory = CPUMemory()
        memory.write(4, 0xFA)
        memory.write(5, 0x73)

        lo = memory.read(4)
        hi = memory.read(5)
        address = lo | (hi << 8)
        state = memory.get_save_state()
        memory = CPUMemory()
        memory.set_save_state(state)
        assert memory.read(address) == 0x73
