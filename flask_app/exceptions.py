class FlashedError(Exception):
    def __init__(self, message, category='error'):
        self.message = message
        self.category = category

    def __str__(self):
        return self.message
