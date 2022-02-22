import _pickle as cpickle  # Faster C implementation of pickle. Used instead of standard pickle


class PickleDistancesSaver:
    def __init__(self):
        self.y_list = []
        self.x_list = []
        self.distances_list = []

    def save_distances_to_pickle_file(self, distances_list):
        self.distances_list = distances_list
        cpickle.dump(self.distances_list, open('distances.pkl', 'wb'))

    def generate_y_for_distances(self):
        for i in range(len(self.distances_list)):
            self.y_list.append(i)
        cpickle.dump(self.y_list, open('y.pkl', 'wb'))

    def generate_x_for_distances(self):
        for i in range(len(self.distances_list)):
            self.x_list.append(0)
        cpickle.dump(self.x_list, open('x.pkl', 'wb'))

    def clear_lists(self):
        self.distances_list = []
        self.x_list = []
        self.y_list = []