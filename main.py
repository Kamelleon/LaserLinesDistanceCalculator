import copy
import cv2
import numpy as np
from scipy.spatial import distance as dist


class HelperFunctions:
    @staticmethod
    def midpoint(ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    @staticmethod
    def generate_colors(shorter_line):
        colors = []
        for i in range(len(shorter_line)):
            colors.append((255, 0, 0))
        return colors

class ImageManager:
    def __init__(self,image_name,hsv_image=False):
        self.image_name = image_name
        self.hsv_image = hsv_image

        self.image = None
        self.image_hsv = None
        self.colors = []
        self.referenced_object_pixel_width = 1
        self.referenced_object_real_width = 1
        self.pixel_per_metric = 1

    def _load_image(self):
        self.image = cv2.imread(self.image_name)
        cv2.imshow("Source image",self.image)

    def get_processed_image(self):
        self._load_image()
        self.image_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        # sensitivity = 70
        # lower_green = np.array([0, 0, 255-sensitivity])
        # upper_green = np.array([255, sensitivity, 255])  # white mask
        # lower_green = np.array([40, 40, 40])
        # upper_green = np.array([110, 255, 255]) # green mask

        lower_green = np.array([40, 135,40])
        upper_green = np.array([110, 255,255]) # turkusowa

        # lower_green = np.array([110, 50, 50])
        # upper_green = np.array([130, 255, 255]) # blue mask

        # lower_red = np.array([62, 62, 90])
        # upper_red = np.array([255, 255, 255]) # red mask

        mask1 = cv2.inRange(self.image_hsv, lower_green, upper_green)

        mask = cv2.bitwise_and(self.image,self.image,mask=mask1)

        self.image = self.image.copy()
        self.image[
            np.where(
                mask == 0)] = 0  # RED IMAGE
        if self.hsv_image:
            self.image = self.image_hsv.copy()
            self.image[np.where(mask == 0)] = 0
        return self.image

    def get_image(self):
        self._load_image()
        return self.image

    def set_referenced_object_pixel_width(self, referenced_object_pixel_width):
        self.referenced_object_pixel_width = referenced_object_pixel_width

    def set_referenced_object_real_width_in_millimetres(self,referenced_object_real_width):
        self.referenced_object_real_width = referenced_object_real_width

    def calculate_pixel_per_metric(self):
        self.pixel_per_metric = self.referenced_object_real_width/self.referenced_object_pixel_width

    def get_edged_image_with_min_and_max_threshold(self, image, minimum_threshold, maximum_threshold):
        edged = cv2.Canny(image, minimum_threshold, maximum_threshold)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        return edged

    # def get_referenced_object(self, edged_img):
    #     cnts = cv2.findContours(edged_img.copy(), cv2.RETR_EXTERNAL,
    #                             cv2.CHAIN_APPROX_SIMPLE)
    #     cnts = imutils.grab_contours(cnts)
    #
    #     (cnts, _) = contours.sort_contours(cnts)
    #
    #     refObj = None
    #
    #     for c in cnts:
    #         # if the contour is not sufficiently large, ignore it
    #         if cv2.contourArea(c) < 200:
    #             continue
    #         # compute the rotated bounding box of the contour
    #         box = cv2.minAreaRect(c)
    #         box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    #         box = np.array(box, dtype="int")
    #         # order the points in the contour such that they appear
    #         # in top-left, top-right, bottom-right, and bottom-left
    #         # order, then draw the outline of the rotated bounding
    #         # box
    #         box = perspective.order_points(box)
    #         # compute the center of the bounding box
    #         cX = np.average(box[:, 0])
    #         cY = np.average(box[:, 1])
    #
    #         # if this is the first contour we are examining (i.e.,
    #         # the left-most contour), we presume this is the
    #         # reference object
    #         if refObj is None:
    #             # unpack the ordered bounding box, then compute the
    #             # midpoint between the top-left and top-right points,
    #             # followed by the midpoint between the top-right and
    #             # bottom-right
    #             (tl, tr, br, bl) = box
    #             (tlblX, tlblY) = HelperFunctions.midpoint(tl, bl)
    #             (trbrX, trbrY) = HelperFunctions.midpoint(tr, br)
    #             # compute the Euclidean distance between the midpoints,
    #             # then construct the reference object
    #             D = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
    #             refObj = (box, (cX, cY),
    #                       D / 2)
    #             continue
    #     return refObj

    def show_distances(self, img, first_line_right_side_coordinates,second_line_left_side_coordinates,colors):
        orig = img.copy()
        for ((yA, xA), (yB, xB), color) in zip(first_line_right_side_coordinates, second_line_left_side_coordinates,
                                               colors):
            if yA == 0 or yB == 0:
                continue
            cv2.circle(orig, (int(xA), int(yA)), 2, color, -1)
            cv2.circle(orig, (int(xB), int(yB)), 2, color, -1)
            cv2.line(orig, (int(xA), int(yA)), (int(xB), int(yB)),
                     color, 1)
            # compute the Euclidean distance between the coordinates,
            # and then convert the distance in pixels to distance in
            # units
            D = dist.euclidean((int(xA), int(yA)), (int(xB), int(yB))) * self.pixel_per_metric
            (mX, mY) = HelperFunctions.midpoint((xA, yA), (xB, yB))
            cv2.putText(orig, "{:.2f}mm".format(D), (int(mX - 40), int(mY - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            cv2.imshow("Distance between laser lines", orig)

            cv2.waitKey(0)
            orig = img.copy()


class LineCalculations:
    def __init__(self, edged_image):
        self.edged_image = edged_image
        self.first_line = []
        self.second_line = []
        self.coordinates_of_edged_image = None
        self.middle_point_between_lines = 0

    def set_middle_point_between_lines(self, middle_point_between_two_lines):
        self.middle_point_between_lines = middle_point_between_two_lines

    def find_coordinates_of_lines(self):
        indices = np.where(edged_img != [0])
        self.coordinates_of_edged_image = zip(indices[0], indices[1])  # First value is Y, second X
        for i in self.coordinates_of_edged_image:
            if i[1] < self.middle_point_between_lines:
                self.first_line.append([i[0], i[1]])
            else:
                self.second_line.append([i[0], i[1]])

        return self.first_line, self.second_line

    def find_x_middle_point_of_line(self, line):
        sum_of_x_points_in_line = 0
        for i in line:
            sum_of_x_points_in_line += i[1]
        x_middle_point_of_line = sum_of_x_points_in_line // len(line)
        return x_middle_point_of_line

    def get_side_coordinates_for_first_line(self, middle_point_of_first_line):
        first_line_right_side_coordinates = []
        for i in self.first_line:
            if i[1] > middle_point_of_first_line:
                first_line_right_side_coordinates.append([i[0], i[1]])
        return first_line_right_side_coordinates

    def get_side_coordinates_for_second_line(self, middle_point_of_second_line, first_line_right_side_coordinates):
        second_line_left_side_coordinates = []
        for i in self.second_line:
            if i[1] < middle_point_of_second_line and i[1] > self.middle_point_between_lines:
                if i[0] >= first_line_right_side_coordinates[0][0]:  # Take only coordinates that have this same or greater value of y
                    second_line_left_side_coordinates.append([i[0], i[1]])
        return second_line_left_side_coordinates

    def delete_repeating_y_coordinates(self, side_coordinates):
        side_coordinates_without_repeated_y = []
        used_numbers = []
        count = 0
        for sub in side_coordinates:
            side_coordinates_without_repeated_y.append([])
            if sub[0] not in used_numbers:
                side_coordinates_without_repeated_y[count].append(sub[0])
                side_coordinates_without_repeated_y[count].append(sub[1])
                used_numbers.append(sub[0])
            count += 1
        side_coordinates_without_repeated_y = [x for x in side_coordinates_without_repeated_y if x != []]  # Delete empty lists from 2D matrix
        return side_coordinates_without_repeated_y

    def add_blank_brackets_for_missing_coords(self, line_side_coordinates_list):
        filled_list = copy.deepcopy(line_side_coordinates_list)
        accumulator = 0
        for i in range(len(line_side_coordinates_list) - 1):
            if line_side_coordinates_list[i + 1][0] - line_side_coordinates_list[i][0] != 1:
                for z in range(
                        (line_side_coordinates_list[i + 1][0] - line_side_coordinates_list[i][0]) - 1):
                    filled_list.insert((i + 1) + accumulator, [0, 0])
                    accumulator += 1
        return filled_list


if __name__ == "__main__":
    # "First line" - shorter line (should be on the left side of an image)
    # "Second line" - longer line (should be on the right side of an image)

    image_manager = ImageManager("wojtek.jpg")

    image_manager.set_referenced_object_real_width_in_millimetres(58)
    image_manager.set_referenced_object_pixel_width(209)
    image_manager.calculate_pixel_per_metric()

    img = image_manager.get_processed_image()
    edged_img = image_manager.get_edged_image_with_min_and_max_threshold(img, 100, 300)

    cv2.imshow("Edged image",edged_img)
    cv2.waitKey(0)

    # referenced_object = image_manager.get_referenced_object(edged_img)

    line_calculator = LineCalculations(edged_img)
    line_calculator.set_middle_point_between_lines(180)

    first_line, second_line = line_calculator.find_coordinates_of_lines()

    first_line_middle_point = line_calculator.find_x_middle_point_of_line(first_line)
    second_line_middle_point = line_calculator.find_x_middle_point_of_line(second_line)

    first_line_right_side_coordinates = line_calculator.get_side_coordinates_for_first_line(first_line_middle_point)
    second_line_left_side_coordinates = line_calculator.get_side_coordinates_for_second_line(second_line_middle_point, first_line_right_side_coordinates)

    first_line_right_side_coordinates = line_calculator.delete_repeating_y_coordinates(first_line_right_side_coordinates)
    second_line_left_side_coordinates = line_calculator.delete_repeating_y_coordinates(second_line_left_side_coordinates)

    # Cut the length of second line (longer) to be this same as first line (shorter)
    second_line_left_side_coordinates = second_line_left_side_coordinates[:len(first_line_right_side_coordinates)]

    first_line_right_side_coordinates = line_calculator.add_blank_brackets_for_missing_coords(first_line_right_side_coordinates)
    second_line_left_side_coordinates = line_calculator.add_blank_brackets_for_missing_coords(second_line_left_side_coordinates)

    colors = HelperFunctions.generate_colors(first_line_right_side_coordinates)

    first_line_right_side_coordinates = np.array(first_line_right_side_coordinates)
    second_line_left_side_coordinates = np.array(second_line_left_side_coordinates)

    image_manager.show_distances(img,first_line_right_side_coordinates,second_line_left_side_coordinates,colors)
