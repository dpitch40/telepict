from PIL import Image
import redis

redis_client = redis.Redis()

def flatten_rgba_image(img, background_color=(255, 255, 255)):
    background = Image.new('RGB', img.size, background_color)
    background.paste(img, mask=img.split()[3])
    return background

class ImageBackend:
    def __init__(self, drawing):
        self.drawing = drawing

    def generate_key(self):
        raise NotImplementedError

    async def _load(self):
        raise NotImplementedError

    async def load(self):
        key = self.generate_key()
        if redis_client.exists(key):
            return redis_client.get(key)
        data = await self._load()
        redis_client.set(key, data)
        return data

    def _save(self):
        raise NotImplementedError

    def save(self):
        redis_client.set(self.generate_key(), self.drawing.drawing)
        self._save()
