class FlashedError(Exception):
    def __init__(self, message, *args, category='error', **kwargs):
        super(FlashedError, self).__init__(message, *args, **kwargs)
        self.message = message
        self.category = category

    def __str__(self):
        return self.message
