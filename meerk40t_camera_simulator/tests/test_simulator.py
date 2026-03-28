import sys
from unittest.mock import MagicMock

# Mock dependencies before importing the module under test
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from meerk40t_camera_simulator.simulator import MockCapture

def test_mock_capture_init_default():
    """
    Test MockCapture initialization with default values.
    """
    cap = MockCapture()
    assert cap.is_opened is True
    assert cap.frame_count == 0
    assert cap.width == 640
    assert cap.height == 480
    assert cap.ball_pos == [320, 240]
    assert cap.ball_vel == [5, 5]
    assert cap.fps == 10.0

def test_mock_capture_init_custom():
    """
    Test MockCapture initialization with custom values.
    """
    width = 800
    height = 600
    cap = MockCapture(width=width, height=height)
    assert cap.is_opened is True
    assert cap.frame_count == 0
    assert cap.width == width
    assert cap.height == height
    assert cap.ball_pos == [400, 300]
    assert cap.ball_vel == [5, 5]
    assert cap.fps == 10.0
