import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock cv2 and numpy before importing simulator
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from meerk40t_camera_simulator.simulator import MockCapture

class TestMockCapture(unittest.TestCase):
    def test_read_when_closed(self):
        capture = MockCapture()
        capture.release()  # Sets self.is_opened = False

        ret, frame = capture.read()

        self.assertFalse(ret)
        self.assertIsNone(frame)

    @patch('meerk40t_camera_simulator.simulator.time.time')
    @patch('meerk40t_camera_simulator.simulator.time.sleep')
    def test_read_fps_enforcement_sleeps(self, mock_sleep, mock_time):
        capture = MockCapture()
        capture.fps = 10.0

        capture.last_frame_time = 100.0

        # 1st call: now = time.time()
        # 2nd call: self.last_frame_time = time.time()
        mock_time.side_effect = [100.05, 100.15]

        ret, frame = capture.read()

        self.assertTrue(ret)
        mock_sleep.assert_called_once()
        self.assertAlmostEqual(mock_sleep.call_args[0][0], 0.05)
        self.assertEqual(capture.last_frame_time, 100.15)

    @patch('meerk40t_camera_simulator.simulator.time.time')
    @patch('meerk40t_camera_simulator.simulator.time.sleep')
    def test_read_fps_enforcement_no_sleep(self, mock_sleep, mock_time):
        capture = MockCapture()
        capture.fps = 10.0
        capture.last_frame_time = 100.0

        mock_time.side_effect = [100.2, 100.2]

        ret, frame = capture.read()

        self.assertTrue(ret)
        mock_sleep.assert_not_called()
        self.assertEqual(capture.last_frame_time, 100.2)

    def test_read_when_opened(self):
        capture = MockCapture()
        initial_frame_count = capture.frame_count

        ret, frame = capture.read()

        self.assertTrue(ret)
        self.assertIsNotNone(frame)
        self.assertEqual(capture.frame_count, initial_frame_count + 1)

if __name__ == '__main__':
    unittest.main()
