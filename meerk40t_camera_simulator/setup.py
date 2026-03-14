from setuptools import setup, find_packages

setup(
    name='meerk40t_camera_simulator',
    version='0.1.0',
    description='A camera simulator extension for meerk40t',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python-headless',
    ],
    entry_points={
        "meerk40t.extension": ["camera_simulator = meerk40t_camera_simulator.simulator:plugin"]
    }
)
