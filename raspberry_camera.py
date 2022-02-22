from sys import platform
import picamera
from subprocess import call
import os
class RaspberryCamera:
    def __init__(self, resolution=(1920, 1080), frame_rate=30, recording_time=5, mp4_video_name='video.mp4'):
        if platform == "win32" or platform == "darwin":
            raise OSNotSupportedError("Only Linux systems are supported (especially Raspberry Pi 3 or 4)")
        self.resolution = resolution
        self.frame_rate = frame_rate
        self.recording_time = recording_time
        self.h264_video_name = 'video.h264'
        self.mp4_video_name = mp4_video_name

    def start_recording(self):
        self._delete_old_h264_video_if_exists()

        print("Recording video...")
        with picamera.PiCamera() as camera:
            camera.resolution = self.resolution
            camera.framerate = self.frame_rate
            camera.start_recording(self.h264_video_name)
            camera.wait_recording(self.recording_time)
            camera.stop_recording()

        command = f"MP4Box -add {self.h264_video_name}:fps={self.frame_rate} -new {self.mp4_video_name}"
        print(f"Video successfully recorded. Converting into '.mp4' format with {self.frame_rate}FPS using command:"
              f"{command}")

        call([command], shell=True)
        print("Video converted.")

    def _delete_old_h264_video_if_exists(self):
        if os.path.exists(self.h264_video_name):
            os.remove(self.h264_video_name)


class OSNotSupportedError(Exception):
    pass


class NoPiCameraLibraryError(Exception):
    pass


class EmptyFrameError(Exception):
    pass

# class CameraNotFoundError(Exception):
#     pass
