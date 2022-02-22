import cv2
from pickle_distances_saver import PickleDistancesSaver

class VideoReader:
    def __init__(self, video_name=None, frames_to_process=None, save_frames_to_process_to_file=False):
        self.video_name = video_name
        self.frames_to_process = frames_to_process
        self.save_frames_to_process_to_file = save_frames_to_process_to_file
        self.pickle_distances_saver = PickleDistancesSaver()

    def read_frames_from_video_and_process_them(self, process_function):
        video = cv2.VideoCapture(self.video_name)
        is_successfully, image = video.read()
        current_frame_number = 0
        number_of_scan = 0
        self.pickle_distances_saver.clear_lists()
        while is_successfully:
            is_successfully, image = video.read()
            if current_frame_number in self.frames_to_process:
                number_of_scan += 1
                print(f'Processing frame number: {current_frame_number}')
                if self.save_frames_to_process_to_file:
                    cv2.imwrite(f"Frame_{current_frame_number}.jpg", image)
                process_function(image, number_of_scan, self.pickle_distances_saver)
            current_frame_number += 1
