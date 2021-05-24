import os.path

from . import ImageBackend

class FileImageBackend(ImageBackend):
    storage_dir = 'drawings/'

    def generate_key(self, d):
        return f'{d.stack.game_id}_{d.stack.owner.name}_{d.stack.id_}_{d.author.name}_{d.stack_pos}'

    def generate_fname(self, drawing):
        return os.path.join(self.storage_dir, self.generate_key(drawing) + '.jpg')

    async def _load(self, drawing):
        with open(self.generate_fname(drawing), 'rb') as fobj:
            return fobj.read()

    def _save(self, drawing):
        with open(self.generate_fname(drawing), 'wb') as fobj:
            fobj.write(drawing.drawing)
