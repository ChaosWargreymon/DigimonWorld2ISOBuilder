class FeedbackBase(object):
    def __init__(self, current=None, previous=None):
        self.current = current
        self.previous = previous
        self.changed = False

    def update(self, value):
        if self.current != value:
            self.previous = self.current
            self.current = value
            self.changed = True
        else:
            self.changed = False

class Percentage(FeedbackBase):
    def __init__(self, max_value):
        self.max = max_value
        super().__init__()

    def calculate(self):
        return (self.current / self.max) * 100

    def output(self):
        self.changed = False
        if self.current and self.previous != self.current:
            self.previous = self.current
            return "{:.1f}%".format(self.calculate()).zfill(5)
        else:
            return "00.0%"


class LoadingBar(FeedbackBase):
    def __init__(self, bar_length=20):
        self.bar_length = bar_length
        super().__init__(current="[{}]".format("-" * self.bar_length))

    def create_bar(self, percent):
        bar = (
            "[{}{}]".format(
                "=" * int((self.bar_length / 100) * percent),
                "-" * int(self.bar_length - (self.bar_length / 100) * percent)
            )
        )
        return bar

    def output(self):
        self.changed = False
        return self.current
