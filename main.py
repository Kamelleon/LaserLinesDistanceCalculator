import traceback
from video_reader import VideoReader
from raspberry_camera import RaspberryCamera
from image_manipulator import ImageManipulator
from laser_lines_finder import LaserLinesCoordinatesFinder
from distances_calculator import DistancesCalculator
from pickle_distances_saver import PickleDistancesSaver
from gpio_trigger import GPIOTrigger
from time import time, sleep



def image_processor(image, number_of_scan, pickle_distances_saver):
    masked_frame, edged_frame = image_manipulator.preprocess_frame(image, get_masked_frame=True)

    laser_lines_finder.find_coordinates_of_lines_from_edged_frame(edged_frame)

    left_line_right_side_coordinates, \
    right_line_left_side_coordinates = laser_lines_finder.get_side_coordinates_for_left_and_right_lines()

    distances_calculator.image = masked_frame
    distances_calculator.number_of_scan = number_of_scan
    distances_list = distances_calculator.calculate_distances_between_laser_lines(
        left_line_right_side_coordinates,
        right_line_left_side_coordinates,
        show_distances_on_image=True)

    pickle_distances_saver.number_of_scan = number_of_scan
    pickle_distances_saver.append_data_for_colors(distances_list)
    pickle_distances_saver.append_data_for_y()
    pickle_distances_saver.append_data_for_x()
    # pickle_data_saver.clear_lists()


if __name__ == "__main__":

    image_manipulator = ImageManipulator()

    pickle_data_saver = PickleDistancesSaver()

    distances_calculator = DistancesCalculator(referenced_object_real_width=66,
                                               referenced_object_pixel_width=117.2,
                                               distance_sampling_multiplier=90)

    laser_lines_finder = LaserLinesCoordinatesFinder(middle_x_point_between_lines=103)

    rpi_camera = RaspberryCamera(resolution=(1920, 1088),
                                 frame_rate=30,
                                 recording_time=5,
                                 mp4_video_name='video.mp4')

    mp4_video_reader = VideoReader(video_name=rpi_camera.mp4_video_name,
                                   frames_to_process=[90,91,92,93,94,95,96,97,98,99,100],
                                   save_frames_to_process_to_file=True)

    gpio_trigger = GPIOTrigger()
    trigger_check_delay = 0.2
    lasers_disabled = False

    while True:
        with open("status.txt", "r") as f:
            status = f.readline()
            print(status)
        if str(status) == "disabled":
            print("disabled")
            if not lasers_disabled:
                lasers_disabled = True
            else:
                sleep(0.5)
        else:
            lasers_disabled = False
            try:
                rpi_camera.start_recording()
                start = time()
                mp4_video_reader.read_frames_from_video_and_process_them(image_processor)
                print("FULL LOOP TIME:", time() - start, "sec")
            except KeyboardInterrupt:
                break
            except:
                print(traceback.print_exc())
        # else:
        #     sleep(trigger_check_delay)
