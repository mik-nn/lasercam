import cv2
import numpy as np
import time

class MockCapture:
    """
    A mock class replacing cv2.VideoCapture.
    Generates synthetic frames with a bouncing ball or text.
    """
    def __init__(self, width=640, height=480):
        self.is_opened = True
        self.frame_count = 0
        self.width = width
        self.height = height
        self.ball_pos = [self.width // 2, self.height // 2]
        self.ball_vel = [5, 5]
        self.last_frame_time = time.time()
        self.fps = 10.0 # Simulator FPS

    def isOpened(self):
        return self.is_opened

    def read(self):
        if not self.is_opened:
            return False, None

        # Enforce simulator FPS
        now = time.time()
        time_to_wait = (1.0 / self.fps) - (now - self.last_frame_time)
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        self.last_frame_time = time.time()

        # Create a synthetic image (dark gray background)
        img = np.full((self.height, self.width, 3), 50, dtype=np.uint8)

        # Update ball position
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        # Bounce off walls
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= self.width:
            self.ball_vel[0] = -self.ball_vel[0]
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.height:
            self.ball_vel[1] = -self.ball_vel[1]

        # Draw a bounding rectangle
        cv2.rectangle(img, (10, 10), (self.width - 10, self.height - 10), (255, 255, 255), 2)

        # Draw the bouncing ball
        cv2.circle(img, tuple(self.ball_pos), 20, (0, 0, 255), -1)

        # Draw some text
        cv2.putText(img, f"Meerk40t Camera Simulator", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(img, f"Frame: {self.frame_count}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        self.frame_count += 1
        return True, img

    def release(self):
        self.is_opened = False

    def get(self, propId):
        if propId == cv2.CAP_PROP_FRAME_WIDTH:
            return float(self.width)
        elif propId == cv2.CAP_PROP_FRAME_HEIGHT:
            return float(self.height)
        elif propId == cv2.CAP_PROP_FPS:
            return self.fps
        return 0.0

    def set(self, propId, value):
        if propId == cv2.CAP_PROP_FRAME_WIDTH:
            self.width = int(value)
            return True
        elif propId == cv2.CAP_PROP_FRAME_HEIGHT:
            self.height = int(value)
            return True
        elif propId == cv2.CAP_PROP_FPS:
            if value <= 0:
                value = 1.0
            self.fps = value
            return True
        return False

    def getBackendName(self):
        return "SIMULATOR"


def plugin(kernel, lifecycle=None):
    """
    Meerk40t extension plugin.
    Registers a new console command "camera simulator" which injects the MockCapture into the current camera service.
    """
    if lifecycle == "register":
        @kernel.console_command("simulator", help="Start the camera simulator", input_type="camera", output_type="camera")
        def start_simulator(channel, _, data=None, **kwargs):
            if data is None:
                channel("No camera selected.")
                return None

            # If there's an existing capture, release it
            if data.capture is not None and hasattr(data.capture, "release"):
                data.capture.release()

            channel("Injecting Camera Simulator...")
            data.capture = MockCapture(width=data.width, height=data.height)
            data.is_physical = False
            data.desc = "Camera Simulator"
            data.uri = -1
            channel("Camera Simulator injected.")

            return "camera", data
