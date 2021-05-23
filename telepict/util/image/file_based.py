import os.path

from . import ImageBackend

class FileImageBackend(ImageBackend):
    storage_dir = 'drawings/'

    def generate_key(self):
        d = self.drawing
        return f'{d.stack.game_id}_{d.stack.owner.name}_{d.stack.id_}_{d.author.name}_{d.stack_pos}'

    def generate_fname(self):
        return os.path.join(self.storage_dir, self.generate_key() + '.jpg')

    def load(self):
        with open(self.generate_fname(), 'rb') as fobj:
            return fobj.read()

    def save(self):
        with open(self.generate_fname(), 'wb') as fobj:
            fobj.write(self.drawing.drawing)
