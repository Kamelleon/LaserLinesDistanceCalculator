import cv2
from numpy import array, where
from scipy.spatial import distance as dist
from line_calculations import LaserLinesCalculator
import line_calculations_errors
import _pickle as cpickle
from sys import platform, exit
import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


class ImageManager:
    def __init__(self, save_frames_from_picamera_to_file=False, rotate_source_image=False):
        self.save_frames_from_picamera_to_file = save_frames_from_picamera_to_file
        self.rotate_source_image = rotate_source_image
        self.image = None
        self.image_hsv = None
        self.colors = []

    def _load_image(self):
        self.image = cv2.imread(self.image_name)
        if self.image is None:
            raise line_calculations_errors.SourceImageNotFoundError(f"No image named: '{self.image_name}' found.")
        if self.rotate_image:
            self.image = cv2.rotate(self.image, cv2.ROTATE_180)

        # cv2.imshow("dd",self.image)
        # cv2.waitKey(0)

    def mask_image(self, image):
        self.image = image
        if platform == "linux" or platform == "linux2":
            self.image = self.image[560:783, 40:1670]
        if self.rotate_source_image:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        if self.save_frames_from_picamera_to_file:
            cv2.imwrite("PiCameraImage.jpg", self.image)
            # cv2.imwrite("PiCameraImage.jpg",self.image)

        # self._load_image()
        self.image_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        #
        # sensitivity = 110
        # lower_mask = array([0, 0, 255 - sensitivity])
        # upper_mask = array([255, sensitivity, 255])  # white mask
        # #
        lower_mask = array([20, 30, 100])  # W RAZIE POTRZEBY ZMIENIAĆ TYLKO LOWER MASK (WSZYSTKIE 3 WARTOŚCI)
        upper_mask = array([110, 255, 255])  # green mask
        # lower_mask = array([40, 135,40])
        # upper_mask = array([110, 255,255]) # turquoise mask

        # lower_mask = np.array([110, 50, 50])
        # upper_mask = np.array([130, 255, 255]) # blue mask

        # lower_mask = np.array([62, 62, 90])
        # upper_mask = np.array([255, 255, 255]) # red mask

        mask1 = cv2.inRange(self.image_hsv, lower_mask, upper_mask)

        mask = cv2.bitwise_and(self.image, self.image, mask=mask1)

        self.image = self.image.copy()
        self.image[mask == 0] = 0  # RED IMAGE
        return self.image

    def get_image(self):
        self._load_image()
        return self.image

    def get_edged_image_from_masked_image(self, image, minimum_threshold=100, maximum_threshold=700):
        edged = cv2.Canny(image, minimum_threshold, maximum_threshold)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        return edged


class DistancesPresenter:
    def __init__(self):
        self.image = None
        self._referenced_object_pixel_width = 0
        self._referenced_object_real_width = 0
        self._pixel_per_metric = 1
        self.text_color = (255, 0, 0)
        self.font_size = 0.55
        self.line_color = (255, 0, 0)
        self.line_thickness = 2
        self.circle_color = (255, 0, 0)
        self.circle_size = 2
        self.orig = None
        self.euclidean_distance_between_two_lines = 0
        self.mX, self.mY = 0, 0
        self.xA, self.xB, self.yA, self.yB = 0, 0, 0, 0
        self.jump_value = 10
        self.distances_list = []

    @property
    def referenced_object_pixel_width(self):
        return self._referenced_object_pixel_width

    @referenced_object_pixel_width.setter
    def referenced_object_pixel_width(self, referenced_object_pixel_width):
        print(f"Referenced object pixel width is now set to: {referenced_object_pixel_width}px")
        self._referenced_object_pixel_width = referenced_object_pixel_width

    @property
    def referenced_object_real_width(self):
        return self._referenced_object_real_width

    @referenced_object_real_width.setter
    def referenced_object_real_width(self, referenced_object_real_width):
        print(f"Referenced object real width is now set to: {referenced_object_real_width}mm")
        self._referenced_object_real_width = referenced_object_real_width

    def calculate_pixel_per_metric(self):
        if self._referenced_object_pixel_width == 0:
            raise line_calculations_errors.ReferencedObjectPixelWidthError(
                "Referenced object pixel width has not been set")
        if self._referenced_object_real_width == 0:
            raise line_calculations_errors.ReferencedObjectRealWidthError(
                "Referenced object real width has not been set")
        self._pixel_per_metric = self._referenced_object_real_width / self._referenced_object_pixel_width
        return self._pixel_per_metric

    def calculate_jump_value(self):
        self.jump_value = int(self._pixel_per_metric * 30)
        return self.jump_value

    @staticmethod
    def midpoint(ptA, ptB):
        return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

    def draw_distances(self):
        cv2.circle(self.orig, (int(self.xA), int(self.yA)), self.circle_size, self.circle_color, -1)
        cv2.circle(self.orig, (int(self.xB), int(self.yB)), self.circle_size, self.circle_color, -1)
        cv2.line(self.orig, (int(self.xA), int(self.yA)), (int(self.xB), int(self.yB)),
                 self.line_color, self.line_thickness)
        cv2.putText(self.orig, "{:.2f}mm".format(self.euclidean_distance_between_two_lines),
                    (int(self.mX - 40), int(self.mY - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, self.font_size, self.text_color, 2)
        # cv2.imshow("Edged image", edged_image) # If you want to see also edged image
        cv2.imshow("Distance", self.orig)

        cv2.waitKey(0)
        self.orig = self.image.copy()

    def calculate_distances_between_laser_lines(self,
                                                left_line_right_side_coordinates,
                                                right_line_left_side_coordinates,
                                                show_distances_on_image=True):
        if self.jump_value > len(left_line_right_side_coordinates) or self.jump_value > len(
                right_line_left_side_coordinates):
            raise line_calculations_errors.JumpValueError(
                f"Jump value ({self.jump_value}) is too big for the length of lines "
                f"(left line length: {len(left_line_right_side_coordinates)},"
                f" right line length: {len(right_line_left_side_coordinates)})."
                f" Consider changing it to lower values.")
        self.calculate_pixel_per_metric()
        print(f"1px on image is {self._pixel_per_metric:.2f}mm in real")
        self.calculate_jump_value()
        z = 0

        if show_distances_on_image:
            if self.image is None:
                print("No image has been set. Exiting.")
                exit(1)
            self.orig = self.image.copy()

        for ((self.yA, self.xA), (self.yB, self.xB)) in zip(left_line_right_side_coordinates,
                                                            right_line_left_side_coordinates):
            z += 1
            if z % self.jump_value == 0:
                if self.yA == 0 or self.yB == 0:
                    continue

                self.euclidean_distance_between_two_lines = dist.euclidean((int(self.xA), int(self.yA)),
                                                                           (int(self.xB),
                                                                            int(self.yB))) * self._pixel_per_metric
                self.distances_list.append(round(self.euclidean_distance_between_two_lines, 2))
                print(f"Distance at point {z}: {self.euclidean_distance_between_two_lines:.2f}mm")

                (self.mX, self.mY) = self.midpoint((self.xA, self.yA), (self.xB, self.yB))

                if show_distances_on_image:
                    self.draw_distances()
        return self.distances_list


class DataSaver:
    def __init__(self):
        self.y_list = []
        self.x_list = []
        self.distances_list = []

    def save_distances_to_pickle_file(self, distances_list):
        self.distances_list = distances_list
        cpickle.dump(self.distances_list, open('distances.pkl', 'wb'))

    def generate_y_for_distances(self):
        self.y_list = [self.y_list.append(i) for i in range(len(self.distances_list))]
        cpickle.dump(self.y_list, open('y.pkl', 'wb'))

    def generate_x_for_distances(self):
        self.x_list = [self.x_list.append(i) for i in range(len(self.distances_list))]
        cpickle.dump(self.x_list, open('x.pkl', 'wb'))
        self.distances_list.clear()


class RpiCamera:
    def __init__(self, camera_warmup_time=5, image_resolution=(1920, 1080), framerate=30):
        try:
            from picamera.array import PiRGBArray
            from picamera import PiCamera
        except ImportError:
            print("PiCamera library not installed. Exiting...")
            exit(1)
        self.camera_warmup_time = camera_warmup_time
        print("Connecting to PiCamera...")
        self.camera = PiCamera()
        self.camera.resolution = image_resolution
        self.camera.framerate = framerate
        print("Connected successfully. Warming up...")
        self.raw_capture = PiRGBArray(self.camera, size=image_resolution)
        time.sleep(camera_warmup_time)
        print("PiCamera READY.")


class DistanceMeasurementsMethods:
    def __init__(self):
        self.distances_presenter = DistancesPresenter()
        self.data_saver = DataSaver()
        self.laser_lines_calculator = LaserLinesCalculator()

    def perform_distance_measurements_with_picamera(self):
        image_manager = ImageManager(save_frames_from_picamera_to_file=True, rotate_source_image=True)
        self.distances_presenter.referenced_object_real_width = 66
        self.distances_presenter.referenced_object_pixel_width = 118
        rpi = RpiCamera(camera_warmup_time=5)

        for frame in rpi.camera.capture_continuous(rpi.raw_capture, format="bgr", use_video_port=True):
            start = time.time()

            image_array = frame.array
            masked_image = image_manager.mask_image(image_array)
            edged_image = image_manager.get_edged_image_from_masked_image(masked_image, 10, 700)

            self.laser_lines_calculator.find_coordinates_of_lines_from_edged_image(edged_image, 120)
            left_line_right_side_coordinates, right_line_left_side_coordinates = self.laser_lines_calculator.get_side_coordinates_for_left_and_right_lines()

            self.distances_presenter.image = masked_image
            distances_list = self.distances_presenter.calculate_distances_between_laser_lines(
                left_line_right_side_coordinates,
                right_line_left_side_coordinates,
                show_distances_on_image=False)

            self.data_saver.save_distances_to_pickle_file(distances_list)
            self.data_saver.generate_y_for_distances()
            self.data_saver.generate_x_for_distances()

            rpi.raw_capture.truncate(0)

            print("LOOP TIME:", time.time() - start)

    def perform_distance_measurements_from_image_file(self):
        image_manager = ImageManager(rotate_source_image=False)
        image = cv2.imread("PiCameraImage.jpg")
        self.distances_presenter.referenced_object_real_width = 66
        self.distances_presenter.referenced_object_pixel_width = 118
        while True:
            masked_image = image_manager.mask_image(image)
            edged_image = image_manager.get_edged_image_from_masked_image(masked_image, 10, 700)

            self.laser_lines_calculator.find_coordinates_of_lines_from_edged_image(edged_image, 112)
            left_line_right_side_coordinates, right_line_left_side_coordinates = self.laser_lines_calculator.get_side_coordinates_for_left_and_right_lines()

            self.distances_presenter.image = masked_image
            distances_list = self.distances_presenter.calculate_distances_between_laser_lines(
                left_line_right_side_coordinates,
                right_line_left_side_coordinates,
                show_distances_on_image=True)

            self.data_saver.save_distances_to_pickle_file(distances_list)
            self.data_saver.generate_y_for_distances()
            self.data_saver.generate_x_for_distances()


if __name__ == "__main__":
    measurement_method = DistanceMeasurementsMethods()
    if platform == "linux" or platform == "linux2":
        measurement_method.perform_distance_measurements_with_picamera()
    else:
        measurement_method.perform_distance_measurements_from_image_file()
