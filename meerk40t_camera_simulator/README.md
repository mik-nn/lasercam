# Meerk40t Camera Simulator

This is a standalone Python package that acts as a camera simulator extension for [Meerk40t](https://github.com/meerk40t/meerk40t). It mocks OpenCV's `cv2.VideoCapture` class to generate synthetic video frames containing a bouncing ball and text overlay.

This is useful for testing camera-related features (like Marker Alignment or Print & Cut workflows) in Meerk40t without requiring a physical camera device attached to your machine.

## Installation

You can install this extension locally in editable mode. Ensure you are using the same Python environment that Meerk40t is installed in.

```bash
cd meerk40t_camera_simulator
python3 -m pip install -e .
```

## Usage

Once installed, the `meerk40t.extension` entry point will be automatically discovered when Meerk40t launches.

To use the simulator, open the Meerk40t console and run the following commands:

```bash
# Ensure you are interacting with a camera context (e.g., camera 0)
camera

# Start the simulator, injecting the MockCapture into the current camera
simulator
```

If you open the camera window in the GUI, or start the MJPEG server via the console, you will now see the synthetic bouncing ball video feed instead of a real camera feed.
