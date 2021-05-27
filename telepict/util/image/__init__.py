import logging
import io

from PIL import Image
import redis
from flask import current_app

redis_client = redis.Redis()

logger = logging.getLogger('Telepict.image')

def flatten_p_image(img, background_color=(255, 255, 255)):
    background = Image.new('RGBA', img.size, background_color)
    background.paste(img)
    return flatten_rgba_image(background, background_color)

def flatten_rgba_image(img, background_color=(255, 255, 255)):
    background = Image.new('RGB', img.size, background_color)
    background.paste(img, mask=img)
    return background

def convert_image(img_file):
    image = Image.open(img_file)
    if image.mode == 'RGBA':
        image = flatten_rgba_image(image)
    elif image.mode == 'P':
        image = flatten_p_image(image)
    elif image.mode != 'RGB':
        raise ValueError('Unsupported image mode: ' + image.mode)
    # Scale image if necessary
    width_factor = image.size[0] / current_app.config['MAX_IMAGE_WIDTH']
    height_factor = image.size[1] / current_app.config['MAX_IMAGE_HEIGHT']
    max_factor = max(height_factor, width_factor)
    if max_factor > 1:
        target_size = (int(image.size[0] // max_factor),
                       int(image.size[1] // max_factor))
        image = image.resize(target_size)

    bio = io.BytesIO()
    image.save(bio, format='JPEG', quality=current_app.config['JPEG_QUALITY'])
    return bio.getvalue()

class ImageBackend:
    instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls.instance is None:
            logger.info('Started image backend; redis ping = %s', redis_client.ping())
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
        key = self.generate_key(drawing)
        logger.debug('Saving %s', key)
        redis_client.set(key, drawing.drawing)
        self._save(drawing)

if __name__ == '__main__':
    import sys
    from telepict.flask_app import app
    with app.app_context(), open(sys.argv[1], 'rb') as fobj:
            bytes_ = convert_image(fobj)
            with open('out.jpg', 'wb') as fobj2:
                fobj2.write(bytes_)
