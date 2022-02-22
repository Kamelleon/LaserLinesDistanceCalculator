import cv2
from numpy import array


class ImageManipulator:
    def __init__(self):
        self.MASK_NAMES = ["green", "white"]

        self.lower_green_mask = array([20, 30, 100]) # W RAZIE POTRZEBY ZMIENIAĆ TYLKO LOWER MASK (WSZYSTKIE 3 WARTOŚCI)
        self.upper_green_mask = array([110, 255, 255])

        self.sensitivity = 110
        self.lower_white_mask = array([0, 0, 255 - self.sensitivity])
        self.upper_white_mask = array([255, self.sensitivity, 255])

    def preprocess_frame(self, frame, min_threshold_for_edge_detection=10,max_threshold_for_edge_detection=700, get_masked_frame=True):
        frame = frame[560:783, 40:1670]
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        masked_frame = self.apply_mask(frame)
        edged_frame = self.get_edged_frame(masked_frame, min_threshold=min_threshold_for_edge_detection,max_threshold=max_threshold_for_edge_detection)
        if get_masked_frame:
            return masked_frame, edged_frame
        return edged_frame


    def apply_mask(self, frame):
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_mask = self.lower_green_mask
        upper_mask = self.upper_green_mask

        # White mask
        # lower_mask = self.lower_white_mask
        # upper_mask = self.upper_white_mask

        mask = cv2.inRange(image_hsv, lower_mask, upper_mask)
        mask = cv2.bitwise_and(frame, frame, mask=mask)

        frame = frame.copy()
        frame[mask == 0] = 0 # Colour all image except mask on black
        return frame

    def get_edged_frame(self, frame, min_threshold,max_threshold):
        edged = cv2.Canny(frame, min_threshold, max_threshold)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        return edged
