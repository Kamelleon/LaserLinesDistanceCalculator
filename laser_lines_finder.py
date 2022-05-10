import numpy as np

class LaserLinesCoordinatesFinder:
    def __init__(self, middle_x_point_between_lines=120):

        super().__init__()
        self.middle_x_point_between_lines = middle_x_point_between_lines

        self.left_line = []
        self.left_line_right_side_coordinates = []

        self.right_line = []
        self.right_line_left_side_coordinates = []


    @staticmethod
    def midpoint(ptA, ptB):
        return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

    def get_side_coordinates_for_left_and_right_lines(self):
        self.left_line_right_side_coordinates = []
        self.right_line_left_side_coordinates = []

        self.get_left_line_right_side_coordinates()
        self.get_right_line_left_side_coordinates()

        self.trim_beginning_of_lines_coordinates()

        self.left_line_right_side_coordinates = self.add_blank_brackets_for_missing_coords(
            self.left_line_right_side_coordinates)

        self.right_line_left_side_coordinates = self.add_blank_brackets_for_missing_coords(
            self.right_line_left_side_coordinates)

        self.left_line_right_side_coordinates = np.array(self.left_line_right_side_coordinates)
        self.right_line_left_side_coordinates = np.array(self.right_line_left_side_coordinates)

        self.left_line = []
        self.right_line = []

        return self.left_line_right_side_coordinates, self.right_line_left_side_coordinates

    def find_coordinates_of_lines_from_edged_frame(self, edged_image):
        indices = np.where(edged_image != [0])
        coordinates_of_edged_image = zip(indices[0], indices[1])  # First value is Y, second X

        for coordinate in coordinates_of_edged_image:
            y_coordinate = coordinate[0]
            x_coordinate = coordinate[1]
            if x_coordinate < self.middle_x_point_between_lines:
                self.left_line.append([y_coordinate, x_coordinate])
            else:
                self.right_line.append([y_coordinate, x_coordinate])

        if len(self.right_line) == 0:
            print("blad")
            # raise NoCoordinatesFoundError(
            #     "No coordinates found for the right line. It may be due to the following reasons:"
            #     "- Miiddle point between two lines is wrongly set"
            #     "- Mask is wrongly set (maybe try with white mask or change values of current mask)"
             #   "- The image doesn't show laser lines. Consider turning on the raw frame saving option to see what camera currently captures.")
        if len(self.left_line) == 0:
            print("blad")
            # raise NoCoordinatesFoundError(
            #     "No coordinates found for the left line. It may be due to the following reasons:"
            #     "- Middle point between two lines is wrongly set"
            #     "- Mask is wrongly set (maybe try with white mask or change values of current mask)"
            #     "- The image doesn't show laser lines. Consider turning on the raw frame saving option to see what camera currently captures.")
        return self.left_line, self.right_line

    def get_left_line_right_side_coordinates(self):
        for index, coordinate in enumerate(self.left_line):
            current_y_coordinate = coordinate[0]
            if index != 0:
                previous_y_coordinate = self.left_line[index - 1][0]
                if current_y_coordinate != previous_y_coordinate:
                    previous_coordinate = self.left_line[index - 1]
                    self.left_line_right_side_coordinates.append(previous_coordinate)
        if len(self.left_line_right_side_coordinates) > 0:
            return self.left_line_right_side_coordinates
        else:
            print("blad")
            # raise NoCoordinatesFoundError(
            #     "No coordinates found for the left line right side coordinates. It may be due to the following reasons:"
            #     "- Middle point between two lines is wrongly set"
            #     "- Mask is wrongly set (maybe try with white mask or change values of current mask)"
            #     "- The image doesn't show laser lines. Consider turning on the raw frame saving option to see what camera currently captures.")

    def get_right_line_left_side_coordinates(self):
        reversed_right_line_coordinates = list(reversed(self.right_line))
        for index, coordinate in enumerate(reversed_right_line_coordinates):
            if index != 0:
                current_y_coordinate = coordinate[0]
                previous_y_coordinate = reversed_right_line_coordinates[index - 1][0]
                if current_y_coordinate < previous_y_coordinate:
                    self.right_line_left_side_coordinates.append(reversed_right_line_coordinates[index - 1])
        self.right_line_left_side_coordinates = list(reversed(self.right_line_left_side_coordinates))

        if len(self.right_line_left_side_coordinates) > 0:
            return self.right_line_left_side_coordinates
        else:
            print("blad")
            # raise NoCoordinatesFoundError(
            #     "No coordinates found for the right line left side coordinates. Check your middle point between two lines."
            #     "- Middle point between two lines is wrongly set"
            #     "- Mask is wrongly set (maybe try with white mask or change values of current mask)"
            #     "- The image doesn't show laser lines. Consider turning on the raw frame saving option to see what camera currently captures.")

    @staticmethod
    def add_blank_brackets_for_missing_coords(line_side_coordinates_list):
        filled_list = line_side_coordinates_list[:]
        accumulator = 0
        for i in range(len(line_side_coordinates_list) - 1):
            if line_side_coordinates_list[i + 1][0] - line_side_coordinates_list[i][0] != 1:
                for z in range(
                        (line_side_coordinates_list[i + 1][0] - line_side_coordinates_list[i][0]) - 1):
                    filled_list.insert((i + 1) + accumulator, [0, 0])
                    accumulator += 1
        return filled_list

    def trim_beginning_of_lines_coordinates(self):
        temp_left = []
        temp_right = []

        first_line_shorter = self.left_line_right_side_coordinates[0][0] < self.right_line_left_side_coordinates[0][0]
        second_line_shorter = self.left_line_right_side_coordinates[0][0] > self.right_line_left_side_coordinates[0][0]

        if first_line_shorter:
            for coordinate in self.left_line_right_side_coordinates:
                y_coordinate = coordinate[0]
                first_y_coordinate_from_right_line = self.right_line_left_side_coordinates[0][0]
                if y_coordinate >= first_y_coordinate_from_right_line:
                    temp_left.append(coordinate)
            temp_right = self.right_line_left_side_coordinates[:]

        elif second_line_shorter:
            for coordinate in self.right_line_left_side_coordinates:
                y_coordinate = coordinate[0]
                first_y_coordinate_from_left_line = self.left_line_right_side_coordinates[0][0]
                if y_coordinate >= first_y_coordinate_from_left_line:
                    temp_right.append(coordinate)
            temp_left = self.left_line_right_side_coordinates[:]
        else:
            pass

        self.left_line_right_side_coordinates = temp_left
        self.right_line_left_side_coordinates = temp_right

        return self.left_line_right_side_coordinates, self.right_line_left_side_coordinates
    #
    # def calculate_sampling_value(self):
    #     self.sampling_distance_value = int(self._pixel_per_metric * self.jump_value_multiplier)
    #     print(f"[i] Distances sampling every {self.sampling_distance_value}mm")
    #     return self.sampling_distance_value
    #
    # def calculate_distances_between_lines(self, left_line_right_side_coordinates, right_line_left_side_coordinates,
    #                                       image_to_draw_distances_on=None):
    #     print(left_line_right_side_coordinates,right_line_left_side_coordinates)
    #     distances_list = []
    #     position_number = 0
    #     for ((self.y_left_line, self.x_left_line), (self.y_right_line, self.x_right_line)) in zip(
    #             left_line_right_side_coordinates,
    #             right_line_left_side_coordinates):
    #         # if position_number % self.sampling_distance_value == 0:
    #         #     position_number += 1
    #             if self.y_left_line == 0 or self.y_right_line == 0:
    #                 continue
    #
    #             self.euclidean_distance_between_two_lines = dist.euclidean(
    #                 (int(self.x_left_line), int(self.y_left_line)),
    #                 (int(self.x_right_line),
    #                  int(self.y_right_line))) * self._pixel_per_metric
    #             distances_list.append(round(self.euclidean_distance_between_two_lines, 2))
    #
    #             (self.mX, self.mY) = self.midpoint((self.x_left_line, self.y_left_line),
    #                                                (self.x_right_line, self.y_right_line))
    #
    #             # print(f"Distance at position {position_number}: {self.euclidean_distance_between_two_lines:.2f}mm")
    #
    #             if image_to_draw_distances_on is not None:
    #                 super().draw_distances(image_to_draw_distances_on,self.x_left_line, self.y_left_line,
    #                                        self.x_right_line, self.x_left_line,
    #                                        self.euclidean_distance_between_two_lines,
    #                                        self.mX, self.mY)
    #     if image_to_draw_distances_on is not None:
    #         imwrite("distances.jpg", image_to_draw_distances_on)
    #     return distances_list
    #
    # def calculate_pixel_per_metric(self):
    #     if self.referenced_object_real_width == 1 and self.referenced_object_pixel_width == 1:
    #         print("[!] Referenced object real width and pixel width has not been set. Default values will be used.")
    #     try:
    #         self._pixel_per_metric = self.referenced_object_real_width / self.referenced_object_pixel_width
    #         print(f"[i] 1px on image is {self._pixel_per_metric:.2f}mm in real")
    #     except ZeroDivisionError:
    #         print("[-] Zero division error detected during calculating pixel per metric value. Consider changing referenced object pixel width to be higher than '0'. Exiting")
    #         sys.exit(1)
    #     return self._pixel_per_metric


class NoCoordinatesFoundError(Exception):
    pass
