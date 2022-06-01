# LaserLinesDistanceCalculator
A program that calculates distance in pixels between two laser lines on image and converts it into millimetres using referenced object size.
Referenced object size (in pixels) and referenced object real width can be set directly from main script.

Program is used to calculate height of brick from two green laser lines.

# Accuracy
Accuracy of this method is as accurate as 1mm, sometimes even 0.5mm. It strongly depends on calibration of lasers and camera resolution.

# How it works
Raspberry Pi has built in camera that records a 3-5 second video when cut sensor detects cut. Then program takes interesting frames from recorded video and processes
them by finding green laser lines, middle point and calculating distance between these two from referenced object size

# Preview

- Raw image from camera


![](https://github.com/Kamelleon/LaserLinesDistanceCalculator/blob/raspberry-gpio-video/preview_pictures/Frame_12.jpg)

- Distances on fragment of image after preprocessing


![](https://github.com/Kamelleon/LaserLinesDistanceCalculator/blob/raspberry-gpio-video/preview_pictures/distances_on_image.jpg)
