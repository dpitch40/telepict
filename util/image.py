from PIL import Image

def flatten_rgba_image(img, background_color=(255, 255, 255)):
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    return background
