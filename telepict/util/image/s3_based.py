from . import ImageBackend

class S3ImageBackend(ImageBackend):
    def load(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
