import time
import traceback
from sys import platform
from numpy import ndarray


class RaspberryCamera:
    def __init__(self, resolution=(1920, 1080), frame_rate=30, warmup_time=2):
        if platform == "win32" or platform == "darwin":
            raise OSNotSupportedError("Only Linux systems are supported (especially Raspberry Pi 3 or 4)")
        self.resolution = resolution
        self.frame_rate = frame_rate
        self.warmup_time = warmup_time
        self.is_camera_available = False
        self.are_settings_applied = False
        self.camera = None
        self.pi_rgb_array = None
        self.check_camera_availability()
        self.apply_settings_for_camera()

    def check_camera_availability(self):
        try:
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            print("[+] PiCamera library has been found.")
            self.camera = PiCamera()
            self.pi_rgb_array = PiRGBArray
            self.is_camera_available = True
            print("[+] Successfully connected to a camera")
            return
        except ImportError:
            raise NoPiCameraLibraryError(
                "PiCamera library is not installed. Install it using 'pip3 install picamera[array]' command")
        except:
            print("[-] Another error connected with camera occured:")
            print(traceback.print_exc())
            exit(1)

    def apply_settings_for_camera(self):
        self.camera.resolution = self.resolution
        self.camera.framerate = self.frame_rate
        self.raw_capture = self.pi_rgb_array(self.camera, size=self.resolution)
        self.are_settings_applied = True
        print("[~] Warming up camera...")
        time.sleep(self.warmup_time)
        print("[i] Camera READY")

    def get_frame(self):
        for frame in self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True):
            frame_is_array = isinstance(frame.array, ndarray)
            frame_is_not_empty = frame.array.size > 0
            if frame_is_array and frame_is_not_empty:
                yield frame
            else:
                print("[-] Frame is empty or frame is not numpy array (image-like object)")

            self.raw_capture.truncate(0)


class OSNotSupportedError(Exception):
    pass


class NoPiCameraLibraryError(Exception):
    pass


class EmptyFrameError(Exception):
    pass

# class CameraNotFoundError(Exception):
#     pass
