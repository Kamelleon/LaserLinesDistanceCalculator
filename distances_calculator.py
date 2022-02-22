import cv2
from scipy.spatial import distance as dist

class DistancesCalculator:
    def __init__(self, referenced_object_real_width, referenced_object_pixel_width, distance_sampling_multiplier):
        self.image = None

        self.referenced_object_real_width = referenced_object_real_width
        self.referenced_object_pixel_width = referenced_object_pixel_width
        self.distance_sampling_multiplier = distance_sampling_multiplier

        self.text_color = (255, 0, 0)
        self.font_size = 0.55
        self.line_color = (255, 0, 0)
        self.line_thickness = 2
        self.circle_color = (255, 0, 0)
        self.circle_size = 2
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self._pixel_per_metric = 1

        self.euclidean_distance_between_two_lines = 0
        self.mX, self.mY = 0, 0
        self.xA, self.xB, self.yA, self.yB = 0, 0, 0, 0
        self.distance_sampling_value = 10
        self.distances_list = []

        self.is_pixel_per_metric_calculated = False

        self.calculate_pixel_per_metric()
        self.calculate_distance_sampling_value()

    def calculate_pixel_per_metric(self):
        if self.referenced_object_pixel_width == 0:
            raise ReferencedObjectPixelWidthError(
                "Referenced object pixel width has not been set OR should not be 0")
        if self.referenced_object_real_width == 0:
            raise ReferencedObjectRealWidthError(
                "Referenced object real width has not been set OR should not be 0")
        self._pixel_per_metric = self.referenced_object_real_width / self.referenced_object_pixel_width
        print(f"[i] 1px on image is {self._pixel_per_metric:.2f}mm in real")
        self.is_pixel_per_metric_calculated = True
        return self._pixel_per_metric

    def calculate_distance_sampling_value(self):
        # if self.distance_sampling_value > len(left_line_right_side_coordinates) or self.distance_sampling_value > len(
        #         right_line_left_side_coordinates):
        #     raise SamplingValueError(
        #         f"Sampling value ({self.distance_sampling_value}) is too big for the length of lines "
        #         f"(left line length: {len(left_line_right_side_coordinates)},"
        #         f" right line length: {len(right_line_left_side_coordinates)})."
        #         f" Consider changing it to lower values.")
        if not self.is_pixel_per_metric_calculated:
            raise SamplingValueError("You should calculate pixel per metric value firstly before calculating sampling value")
        self.distance_sampling_value = int(self._pixel_per_metric * self.distance_sampling_multiplier)
        print(f"[i] Sampling distances every: {self.distance_sampling_value} points")
        return self.distance_sampling_value

    @staticmethod
    def midpoint(ptA, ptB):
        return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

    def draw_distances(self):
        cv2.circle(self.image, (int(self.xA), int(self.yA)), self.circle_size, self.circle_color, -1)
        cv2.circle(self.image, (int(self.xB), int(self.yB)), self.circle_size, self.circle_color, -1)
        cv2.line(self.image, (int(self.xA), int(self.yA)), (int(self.xB), int(self.yB)),
                 self.line_color, self.line_thickness)
        cv2.putText(self.image, "{:.2f}mm".format(self.euclidean_distance_between_two_lines),
                    (int(self.mX - 40), int(self.mY - 10)),
                    self.font, self.font_size, self.text_color, 2)

    def calculate_distances_between_laser_lines(self,
                                                left_line_right_side_coordinates,
                                                right_line_left_side_coordinates,
                                                show_distances_on_image=True):
        if show_distances_on_image and self.image is None:
            raise NoImageSetError("No image has been found, but you wanted to show distances on image.")

        distance_sampling_position = 0
        distances_list = []
        for ((self.yA, self.xA), (self.yB, self.xB)) in zip(left_line_right_side_coordinates,
                                                            right_line_left_side_coordinates):
            distance_sampling_position += 1
            if distance_sampling_position % self.distance_sampling_value == 0:
                # if self.yA == 0 or self.yB == 0:
                #     continue

                self.euclidean_distance_between_two_lines = dist.euclidean((int(self.xA), int(self.yA)),
                                                                           (int(self.xB),
                                                                            int(self.yB))) * self._pixel_per_metric
                distances_list.append(round(self.euclidean_distance_between_two_lines, 2))

                print(f"Distance at point {distance_sampling_position}: {self.euclidean_distance_between_two_lines:.2f}mm")

                (self.mX, self.mY) = self.midpoint((self.xA, self.yA), (self.xB, self.yB))

                if show_distances_on_image:
                    self.draw_distances()

        if show_distances_on_image:
            cv2.imwrite("distances_on_image.jpg", self.image)

        return distances_list


class NoImageSetError(Exception):
    pass


class ReferencedObjectRealWidthError(Exception):
    pass


class ReferencedObjectPixelWidthError(Exception):
    pass


class SamplingValueError(Exception):
    pass