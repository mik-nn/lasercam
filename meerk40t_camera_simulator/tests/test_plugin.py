import sys
from unittest.mock import MagicMock

import pytest

# Mock missing dependencies
sys.modules["cv2"] = MagicMock()
sys.modules["numpy"] = MagicMock()

from meerk40t_camera_simulator.simulator import MockCapture, plugin


def test_plugin_registers_command():
    kernel = MagicMock()
    # Mock the console_command decorator to just return the original function,
    # or save it to verify it was called.

    commands = {}

    def mock_console_command(name, help, input_type, output_type):
        def decorator(func):
            commands[name] = {
                "func": func,
                "help": help,
                "input_type": input_type,
                "output_type": output_type,
            }
            return func

        return decorator

    kernel.console_command = mock_console_command

    # AICODE-NOTE: Ensure that plugin registers the 'simulator' console command
    # on the kernel when lifecycle is 'register'.
    plugin(kernel, lifecycle="register")

    assert "simulator" in commands
    assert commands["simulator"]["help"] == "Start the camera simulator"
    assert commands["simulator"]["input_type"] == "camera"
    assert commands["simulator"]["output_type"] == "camera"


def test_simulator_command_no_camera():
    kernel = MagicMock()

    commands = {}

    def mock_console_command(name, help, input_type, output_type):
        def decorator(func):
            commands[name] = func
            return func

        return decorator

    kernel.console_command = mock_console_command

    plugin(kernel, lifecycle="register")

    start_simulator = commands["simulator"]

    channel = MagicMock()

    # AICODE-NOTE: When data is None, it should channel 'No camera selected.' and return None
    res = start_simulator(channel, None, data=None)

    channel.assert_called_once_with("No camera selected.")
    assert res is None


def test_simulator_command_injects_capture():
    kernel = MagicMock()

    commands = {}

    def mock_console_command(name, help, input_type, output_type):
        def decorator(func):
            commands[name] = func
            return func

        return decorator

    kernel.console_command = mock_console_command

    plugin(kernel, lifecycle="register")

    start_simulator = commands["simulator"]

    channel = MagicMock()
    data = MagicMock()

    old_capture = MagicMock()
    data.capture = old_capture

    data.width = 1280
    data.height = 720

    # AICODE-NOTE: Inject the simulator into the data object when valid camera data is passed.
    res = start_simulator(channel, None, data=data)

    # It should release the old capture
    old_capture.release.assert_called_once()

    assert res[0] == "camera"
    assert res[1] == data

    # MockCapture should be injected
    assert isinstance(data.capture, MockCapture)
    assert data.is_physical is False
    assert data.desc == "Camera Simulator"
    assert data.uri == -1


def test_simulator_command_injects_capture_without_old_capture():
    kernel = MagicMock()

    commands = {}

    def mock_console_command(name, help, input_type, output_type):
        def decorator(func):
            commands[name] = func
            return func

        return decorator

    kernel.console_command = mock_console_command

    plugin(kernel, lifecycle="register")

    start_simulator = commands["simulator"]

    channel = MagicMock()
    data = MagicMock()

    data.capture = None
    data.width = 1280
    data.height = 720

    # AICODE-NOTE: Inject the simulator into the data object when valid camera data is passed.
    res = start_simulator(channel, None, data=data)

    assert res[0] == "camera"
    assert res[1] == data

    # MockCapture should be injected
    assert isinstance(data.capture, MockCapture)
    assert data.is_physical is False
    assert data.desc == "Camera Simulator"
    assert data.uri == -1
