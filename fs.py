class FileServer:
    def __init__(self):
        self.data = [['A', 1], ['B', 3], ['Null', -2], ['C', 4], ['D', -1]]

    def get_data(self):
        return self.data

    def edit_data(self, new_data, location):
        self.data[location] = [new_data, self.data[location][1]]


filesystem = FileServer()
