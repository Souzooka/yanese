from src.controllers.Controller import Controller


class TestController:
    def test_coupling(self):
        # Test that each controller refers to the other
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)

        assert controller0.other is controller1
        assert controller1.other is controller0

    def test_direct_read_write_buttons(self):
        # Test reading/writing buttons directly works
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)

        buttons = [0, 1, 1, 0, 1, 0, 1, 0]
        for i, button in enumerate(buttons):
            controller0.set_button(i, button)
            controller1.set_button(i, button)
        actual_buttons0 = []
        actual_buttons1 = []
        for i in range(len(buttons)):
            actual_buttons0.append(controller0.get_button(i))
            actual_buttons1.append(controller1.get_button(i))
        assert buttons == actual_buttons0
        assert buttons == actual_buttons1

    def test_machine_read_write_buttons(self):
        # Test reading buttons from register works appropriately (w/ and w/o strobe)
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)

        # Read 8 times (should return each button state)
        buttons = [0, 1, 1, 0, 1, 0, 1, 0]
        for i, button in enumerate(buttons):
            controller0.set_button(i, button)
            controller1.set_button(i, button)
        actual_buttons0 = []
        actual_buttons1 = []
        for i in range(len(buttons)):
            actual_buttons0.append(controller0.on_read())
            actual_buttons1.append(controller1.on_read())
        assert buttons == actual_buttons0
        assert buttons == actual_buttons1

        # After reading 8 times, each subsequent hit should return 1
        # (at least, on official Nintendo controllers)
        for i in range(50):
            assert controller0.on_read() == 1
            assert controller1.on_read() == 1

        # Now a write of 1 and then 0 to controller 0's port should reset both
        # controller's internal register and allow us to read the sequence of buttons again
        controller0.on_write(1)
        controller0.on_write(0)

        # Read 8 times (should return each button state after writing 1 and 0 to controller port)
        buttons = [0, 1, 1, 0, 1, 0, 1, 0]
        for i, button in enumerate(buttons):
            controller0.set_button(i, button)
            controller1.set_button(i, button)
        actual_buttons0 = []
        actual_buttons1 = []
        for i in range(len(buttons)):
            actual_buttons0.append(controller0.on_read())
            actual_buttons1.append(controller1.on_read())
        assert buttons == actual_buttons0
        assert buttons == actual_buttons1

        # After setting strobe on port 0, both controllers should continuously read button A when read
        for i in range(8):
            controller0.set_button(i, 1)
            controller1.set_button(i, 1)

        controller0.on_write(1)
        controller0.set_button(0, 0)
        controller1.set_button(0, 0)

        for i in range(50):
            assert controller0.on_read() == 0
            assert controller1.on_read() == 0

        controller0.set_button(0, 1)
        controller1.set_button(0, 1)

        for i in range(50):
            assert controller0.on_read() == 1
            assert controller1.on_read() == 1

    def test_save_state(self):
        # Test saving/loading savestates
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)

        # Savestates should preserve internal register state
        # Advance 4 buttons and then grab state
        buttons = [0, 1, 1, 0, 1, 0, 1, 0]
        for i, button in enumerate(buttons):
            controller0.set_button(i, button)
        for i in range(4):
            controller0.on_read()
        state = controller0.get_save_state()

        # Now advance the next 4 buttons, then restore state
        # and see if we can read the last 4 buttons again
        for i in range(4):
            controller0.on_read()
        controller0.set_save_state(state)
        actual_buttons = []
        for i in range(4):
            actual_buttons.append(controller0.on_read())

        assert buttons[4:8] == actual_buttons

        # Should also preserve the strobe state
        controller0.set_save_state(state)
        controller0.on_write(1)
        controller0.set_save_state(state)

        actual_buttons = []
        for i in range(4):
            actual_buttons.append(controller0.on_read())

        assert buttons[4:8] == actual_buttons

        # (and the inverse)
        controller0.set_save_state(state)
        controller0.on_write(1)
        state2 = controller0.get_save_state()
        controller0.set_save_state(state)

        actual_buttons = []
        for i in range(4):
            actual_buttons.append(controller0.on_read())

        assert buttons[4:8] == actual_buttons

        controller0.on_write(0)
        controller0.set_save_state(state2)

        actual_buttons = []
        for i in range(4):
            actual_buttons.append(controller0.on_read())

        assert [0] * 4 == actual_buttons
