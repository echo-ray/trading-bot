from time import gmtime, strftime


class Combiner:
    def __init__(self, on_combined_value, log):
        self.left = None
        self.right = None
        self.on_combined_value = on_combined_value
        self.log = log

    def on_left(self, value):
        if self.log:
            print("left value {}".format(strftime("%H:%M:%S", gmtime())))
        self.left = value

        if self.right:
            self.emit()

    def on_right(self, value):
        if self.log:
            print("right value {}".format(strftime("%H:%M:%S", gmtime())))
        self.right = value

        if self.left:
            self.emit()

    def emit(self):
        if self.log:
            print("emit value {}".format(strftime("%H:%M:%S", gmtime())))
        self.on_combined_value((self.left, self.right))