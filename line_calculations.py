import copy
import line_calculations_errors
import numpy as np




class LaserLinesCalculator:
    def __init__(self):
        self.left_line = []
        self.left_line_right_side_coordinates = []
        self.right_line = []
        self.right_line_left_side_coordinates = []

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

    def find_coordinates_of_lines_from_edged_image(self, edged_image, middle_x_point_between_lines):
        indices = np.where(edged_image != [0])
        # indices = copy.deepcopy(edged_image)
        # indices = []
        # for i in edged_image:
        #     if any(i) != [0]:
        #         indices.append(i)
        # indices[edged_image!=[0]] = indices
        coordinates_of_edged_image = zip(indices[0], indices[1])  # First value is Y, second X
        for coordinate in coordinates_of_edged_image:
            y_coordinate = coordinate[0]
            x_coordinate = coordinate[1]
            if x_coordinate < middle_x_point_between_lines:
                self.left_line.append([y_coordinate, x_coordinate])
            else:
                self.right_line.append([y_coordinate, x_coordinate])

        return self.left_line, self.right_line

    def get_left_line_right_side_coordinates(self):
        for index, coordinate in enumerate(self.left_line):
            current_y_coordinate = coordinate[0]
            if index != 0:
                previous_y_coordinate = self.left_line[index - 1][0]
                if current_y_coordinate != previous_y_coordinate:
                    previous_coordinate = self.left_line[index - 1]
                    self.left_line_right_side_coordinates.append(previous_coordinate)
        if len(self.left_line_right_side_coordinates)>0:
            return self.left_line_right_side_coordinates
        else:
            raise line_calculations_errors.NoCoordinatesFoundError("No coordinates found for the left line. Check your middle point between two lines.")

    def get_right_line_left_side_coordinates(self):
        reversed_right_line_coordinates = list(reversed(self.right_line))
        for index, coordinate in enumerate(reversed_right_line_coordinates):
            if index != 0:
                current_y_coordinate = coordinate[0]
                previous_y_coordinate = reversed_right_line_coordinates[index - 1][0]
                if current_y_coordinate < previous_y_coordinate:
                    self.right_line_left_side_coordinates.append(reversed_right_line_coordinates[index - 1])
        self.right_line_left_side_coordinates = list(reversed(self.right_line_left_side_coordinates))
        if len(self.right_line_left_side_coordinates)>0:
            return self.right_line_left_side_coordinates
        else:
            raise line_calculations_errors.NoCoordinatesFoundError("No coordinates found for the right line. Check your middle point between two lines.d")

    @staticmethod
    def add_blank_brackets_for_missing_coords(line_side_coordinates_list):
        filled_list = copy.deepcopy(line_side_coordinates_list)
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