from . import ImageBackend

class S3ImageBackend(ImageBackend):
    def generate_key(self):
        d = self.drawing
        return f'{d.stack.game_id}/{d.stack.owner.name}/{d.stack.id_}/{d.author.name}/{d.stack_pos}.jpg'

    async def load(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
