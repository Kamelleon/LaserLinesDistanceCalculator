import cv2
from numpy import array


class ImageManipulator:
    def __init__(self, frame):
        self.MASK_NAMES = ["green", "white"]
        self.frame = frame
        self.lower_green_mask = array([36,0,0])
        # # self.lower_green_mask = array([10, 80, 70])# W RAZIE POTRZEBY ZMIENIAĆ TYLKO LOWER MASK (WSZYSTKIE 3 WARTOŚCI)
        # # self.lower_green_mask = array([5, 20, 110])
        # # self.lower_green_mask = array([0, 20, 110]),
        self.upper_green_mask = array([86,255,255])

        # self.sensitivity = 190
        # self.lower_green_mask = array([0, 0, 255 - self.sensitivity])
        # self.upper_green_mask = array([255, self.sensitivity, 255])

    def preprocess_frame(self, min_threshold_for_edge_detection=10,max_threshold_for_edge_detection=1000, get_masked_frame=True):

        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        masked_frame = self.apply_mask(self.frame)
        cv2.imwrite("preprocessed_frame.jpg",masked_frame)
        edged_frame = self.get_edged_frame(masked_frame, min_threshold=min_threshold_for_edge_detection,max_threshold=max_threshold_for_edge_detection)
        cv2.imwrite("edged_frame.jpg",edged_frame)
        if get_masked_frame:
            return masked_frame, edged_frame
        return edged_frame


    def apply_mask(self, frame):
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_mask = self.lower_green_mask
        upper_mask = self.upper_green_mask

        # # White mask
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

frame = cv2.imread("Frame_50.jpg")
image_manipulator = ImageManipulator(frame)
masked, edged = image_manipulator.preprocess_frame()
cv2.imwrite("masked.jpg",masked)
cv2.imwrite("edged.jpg",edged)