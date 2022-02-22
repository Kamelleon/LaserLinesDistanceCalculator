from sys import platform
import unittest

import numpy

from main2 import RaspberryCamera
from image_manipulator import ImageManipulator

raspberry_camera = RaspberryCamera()
image_manipulator = ImageManipulator()

class TestLaserLinesDistances(unittest.TestCase):

    def test_camera_availability_check(self):
        is_camera_available = raspberry_camera.is_camera_available
        self.assertTrue(is_camera_available)

    def test_settings_are_correctly_applied(self):
        settings_correctly_applied = raspberry_camera.are_settings_applied
        self.assertTrue(settings_correctly_applied)

    def test_frames_are_numpy_ndarrays(self):
        frame_to_check = None
        for frame in raspberry_camera.start_recording():
            frame_to_check = frame
            break
        self.assertIsInstance(frame_to_check, numpy.ndarray)


if __name__ == "__main__":
    unittest.main()