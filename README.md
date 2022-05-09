# Description
A program that calculates distance in pixels between two laser lines on image and converts it into millimetres using referenced object size.
The program is used to perform accurate height measurements of produced bricks with help of trigonometry.

# How it works
To make it work you need to calibrate two lasers (preferably green). One that is directed straightforward to a surface and one that is directed at 45 degree angle to the surface. Both of them must perfectly overlap each other during calibration process. If you put an object on the surface under the laser lines then the distance between these laser lines is the real height the object.
Then you will have to take a picture of these laser lines from above. The program will calculate then the distance between them if you pass correct distance per pixel value and show distances on image if you want.
