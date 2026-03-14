import cv2
import numpy as np
import time

# Global shared background for camera and laser simulators
SHARED_BACKGROUND = None
BACKGROUND_WIDTH = 640
BACKGROUND_HEIGHT = 480

def get_shared_background():
    global SHARED_BACKGROUND
    if SHARED_BACKGROUND is None:
        # Create a dark gray background initially
        SHARED_BACKGROUND = np.full((BACKGROUND_HEIGHT, BACKGROUND_WIDTH, 3), 50, dtype=np.uint8)
    return SHARED_BACKGROUND

class MockCapture:
    """
    A mock class replacing cv2.VideoCapture.
    Generates synthetic frames using a shared background.
    """
    def __init__(self, width=640, height=480):
        self.is_opened = True
        self.frame_count = 0
        self.width = width
        self.height = height
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

        # Get the shared background (which might have been modified by the laser simulator)
        bg = get_shared_background()

        # Make a copy so we don't draw frame-specific text permanently onto the shared background
        img = bg.copy()

        # Draw text overlays
        cv2.putText(img, f"Meerk40t Camera & Laser Simulator", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(img, f"Frame: {self.frame_count}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw a crosshair at the center (camera center)
        cx, cy = self.width // 2, self.height // 2
        cv2.line(img, (cx - 20, cy), (cx + 20, cy), (0, 255, 255), 1)
        cv2.line(img, (cx, cy - 20), (cx, cy + 20), (0, 255, 255), 1)

        self.frame_count += 1

        # Resize if requested dimensions differ from background
        if self.width != BACKGROUND_WIDTH or self.height != BACKGROUND_HEIGHT:
            img = cv2.resize(img, (self.width, self.height))

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


import math
from meerk40t.core.units import Length

class MockDriver:
    """
    A fake driver that intercepts spooler commands and draws onto the shared background.
    """
    def __init__(self, kernel, device):
        self.kernel = kernel
        self.device = device
        self.name = "MockSimulatorDriver"
        self._settings = dict()
        self.hold = False
        self.paused = False

        self.native_x = 0
        self.native_y = 0

        self.laser = False
        self.power = 0.0

        # Mapping physical space to the background image
        # Assuming the background image is our bed size
        self.bg_w = BACKGROUND_WIDTH
        self.bg_h = BACKGROUND_HEIGHT

        # Calculate bed dimensions for scaling
        try:
            self.bed_width_units = float(Length(self.device.bedwidth))
            self.bed_height_units = float(Length(self.device.bedheight))
        except (ValueError, AttributeError):
            # Fallback scaling if units fail
            self.bed_width_units = 320.0 * 39.37 # 320mm in meerk40t core units (mil)
            self.bed_height_units = 220.0 * 39.37

    def hold_work(self, priority):
        return self.hold or self.paused

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value

    def status(self):
        state0 = "idle"
        state1 = "idle"
        if self.hold:
            state0 = "hold"
        return (self.native_x, self.native_y), state0, state1

    def laser_off(self, *values):
        self.laser = False

    def laser_on(self, *values):
        self.laser = True

    def geometry(self, geom):
        bg = get_shared_background()

        # In meerk40t, geomstr provides x, y points
        if geom is None:
            return

        for point in geom.as_points():
            if point is None:
                self.laser = False
                continue

            x, y = point.x, point.y

            # Map native units to pixel space
            px_x = int((x / self.bed_width_units) * self.bg_w)
            px_y = int((y / self.bed_height_units) * self.bg_h)

            px_x = max(0, min(self.bg_w - 1, px_x))
            px_y = max(0, min(self.bg_h - 1, px_y))

            if self.laser:
                old_x = int((self.native_x / self.bed_width_units) * self.bg_w)
                old_y = int((self.native_y / self.bed_height_units) * self.bg_h)

                old_x = max(0, min(self.bg_w - 1, old_x))
                old_y = max(0, min(self.bg_h - 1, old_y))

                # Draw black burn mark
                cv2.line(bg, (old_x, old_y), (px_x, px_y), (0, 0, 0), 2)

            self.native_x = x
            self.native_y = y
            self.laser = True # Next segments in a path are typically burns unless interrupted

    def move_abs(self, x, y):
        self._move_or_burn(x, y)

    def move_rel(self, dx, dy):
        self._move_or_burn(self.native_x + dx, self.native_y + dy)

    def _move_or_burn(self, x, y):
        bg = get_shared_background()

        px_x = int((x / self.bed_width_units) * self.bg_w)
        px_y = int((y / self.bed_height_units) * self.bg_h)
        px_x = max(0, min(self.bg_w - 1, px_x))
        px_y = max(0, min(self.bg_h - 1, px_y))

        if self.laser:
            old_x = int((self.native_x / self.bed_width_units) * self.bg_w)
            old_y = int((self.native_y / self.bed_height_units) * self.bg_h)
            old_x = max(0, min(self.bg_w - 1, old_x))
            old_y = max(0, min(self.bg_h - 1, old_y))

            cv2.line(bg, (old_x, old_y), (px_x, px_y), (0, 0, 0), 2)

        self.native_x = x
        self.native_y = y

    def home(self):
        self.native_x = 0
        self.native_y = 0

    def rapid_mode(self):
        pass

    def program_mode(self):
        pass

    def raster_mode(self, *args):
        pass

    def set_speed(self, speed):
        pass

    def set_power(self, power):
        self.power = power

def plugin(kernel, lifecycle=None):
    """
    Meerk40t extension plugin.
    Registers a new console command "camera simulator" which injects the MockCapture into the current camera service.
    And a command "laser_sim" to inject the laser visual simulator into the active device.
    """
    if lifecycle == "register":
        @kernel.console_command("simulator", help="Start the camera and laser simulator", input_type="camera", output_type="camera")
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

        @kernel.console_command("laser_sim", help="Start the laser visual simulator on the current device")
        def start_laser_simulator(channel, _, **kwargs):
            device = kernel.device
            if device is None:
                channel("No device active.")
                return

            channel(f"Injecting Laser Simulator into {device.label}...")
            # We intercept the device's driver.
            # Note: We may need to interact closely with the spooler or driver depending on how meerk40t sends commands.
            # Using our MockDriver.
            device.driver = MockDriver(kernel, device)
            channel("Laser Simulator Driver injected. Jobs sent to the spooler will now burn onto the camera simulator background.")
