class FlashedError(Exception):
    def __init__(self, message, *args, category='danger', redirect=None, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
        self.category = category
        self.redirect = redirect

    def __str__(self):
        return self.message
