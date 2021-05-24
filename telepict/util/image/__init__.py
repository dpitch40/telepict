import logging

from PIL import Image
import redis

redis_client = redis.Redis()

logger = logging.getLogger('Telepict.image')

def flatten_rgba_image(img, background_color=(255, 255, 255)):
    background = Image.new('RGB', img.size, background_color)
    background.paste(img, mask=img.split()[3])
    return background

class ImageBackend:
    instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls.instance is None:
            cls.instance = cls(**kwargs)
        return cls.instance

    def generate_key(self, drawing):
        raise NotImplementedError

    async def _load(self, drawing):
        raise NotImplementedError

    async def load(self, drawing):
        key = self.generate_key(drawing)
        if redis_client.exists(key):
            logger.debug('Cache hit for %s', key)
            return redis_client.get(key)
        logger.debug('Cache miss for %s', key)
        data = await self._load(drawing)
        redis_client.set(key, data)
        return data

    def _save(self, drawing):
        raise NotImplementedError

    def save(self, drawing):
        redis_client.set(self.generate_key(drawing), drawing.drawing)
        self._save(drawing)
