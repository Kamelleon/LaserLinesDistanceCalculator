from raspberry_camera import RaspberryCamera
from image_manipulator import ImageManipulator
from laser_lines_finder import LaserLinesCoordinatesFinder
from distances_calculator import DistancesCalculator
from pickle_distances_saver import PickleDistancesSaver
from gpio_trigger import GPIOTrigger
from time import time, sleep
from cv2 import imwrite


if __name__ == "__main__":

    image_manipulator = ImageManipulator()

    pickle_data_saver = PickleDistancesSaver()

    distances_calculator = DistancesCalculator(66, 115, 80)

    laser_lines_finder = LaserLinesCoordinatesFinder(middle_x_point_between_lines=120)

    rpi_camera = RaspberryCamera(resolution=(1920, 1088),
                                 frame_rate=30,
                                 warmup_time=2)

    gpio_trigger = GPIOTrigger()
    gpio_check_delay = 0.2

    while True:
        if gpio_trigger.check_button_press():
            for frame in rpi_camera.get_frame():
                start = time()

                masked_frame, edged_frame = image_manipulator.preprocess_frame(frame.array)
                # imwrite("raw_frame_from_picamera.jpg", frame.array) # Uncomment to save raw frames that has been shot by camera

                laser_lines_finder.find_coordinates_of_lines_from_edged_frame(edged_frame)

                left_line_right_side_coordinates, \
                right_line_left_side_coordinates = laser_lines_finder.get_side_coordinates_for_left_and_right_lines()

                distances_calculator.image = masked_frame
                distances_list = distances_calculator.calculate_distances_between_laser_lines(
                        left_line_right_side_coordinates,
                        right_line_left_side_coordinates,
                        show_distances_on_image=True)

                # print(len(distances_list))
                pickle_data_saver.save_distances_to_pickle_file(distances_list)
                pickle_data_saver.generate_y_for_distances()
                pickle_data_saver.generate_x_for_distances()
                pickle_data_saver.clear_lists()

                print("LOOP TIME:", time() - start, "sec")

                if not gpio_trigger.check_button_press():
                    rpi_camera.raw_capture.truncate(0)
                    break
        else:
            sleep(gpio_check_delay)
