import _pickle as cpickle  # Faster C implementation of Pickle. Used instead of standard pickle


class PickleDistancesSaver:
    def __init__(self):
        self.y_list = []
        self.x_list = []
        self.number_of_scan = 0
        self.full_distances_list = []
        self.current_distances_list = []

    def append_data_for_colors(self, distances_list):
        self.current_distances_list = distances_list
        for i in self.current_distances_list:
            self.full_distances_list.append(i)
        # self.full_distances_list.append(distances_list)
        print(self.full_distances_list)
        cpickle.dump(self.full_distances_list, open('distances.pkl', 'wb'))

    def append_data_for_y(self):
        for i in range(len(self.current_distances_list)):
            self.y_list.append(i)
        cpickle.dump(self.y_list, open('y.pkl', 'wb'))

    def append_data_for_x(self):
        for i in range(len(self.current_distances_list)):
            self.x_list.append(self.number_of_scan)
        cpickle.dump(self.x_list, open('x.pkl', 'wb'))

    def clear_lists(self):
        self.full_distances_list = []
        self.current_distances_list = []
        self.x_list = []
        self.y_list = []