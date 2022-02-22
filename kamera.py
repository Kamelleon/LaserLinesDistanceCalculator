import picamera
from subprocess import call
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1080)
    camera.framerate = 30
    camera.start_recording('video.h264')
    camera.wait_recording(5)
    camera.stop_recording()

print("We are going to convert the video.")
# Define the command we want to execute.
command = "MP4Box -add video.h264:fps=30 -new widejooo.mp4"
# Execute our command
call([command], shell=True)
# Video converted.
print("Video converted.")

import cv2
vidcap = cv2.VideoCapture('widejo.mp4')
success,image = vidcap.read()
count = 0
while success:   # save frame as JPEG file
    if count == 100:
        cv2.imwrite("framehaha.jpg", image)
    success,image = vidcap.read()
    print('Read a new frame: ', success)
    count += 1