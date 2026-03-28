import sys
from unittest.mock import MagicMock

# Mock cv2 and numpy before importing simulator
mock_cv2 = MagicMock()
mock_cv2.CAP_PROP_FRAME_WIDTH = 3
mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
mock_cv2.CAP_PROP_FPS = 5
mock_cv2.FONT_HERSHEY_SIMPLEX = 0

sys.modules["cv2"] = mock_cv2
sys.modules["numpy"] = MagicMock()

from meerk40t_camera_simulator.simulator import MockCapture

def test_mock_capture_fps_clamping():
    """
    Test that MockCapture.set clamps FPS to 1.0 if a value <= 0 is provided.
    """
    cap = MockCapture()

    # Test negative FPS
    success = cap.set(mock_cv2.CAP_PROP_FPS, -5.0)
    assert success is True
    assert cap.fps == 1.0

    # Test zero FPS
    success = cap.set(mock_cv2.CAP_PROP_FPS, 0.0)
    assert success is True
    assert cap.fps == 1.0

    # Test positive FPS
    success = cap.set(mock_cv2.CAP_PROP_FPS, 30.0)
    assert success is True
    assert cap.fps == 30.0

def test_mock_capture_get_fps():
    """
    Test that MockCapture.get returns the correct FPS.
    """
    cap = MockCapture()
    cap.fps = 24.0
    assert cap.get(mock_cv2.CAP_PROP_FPS) == 24.0
