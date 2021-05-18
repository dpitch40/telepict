import itertools

import PIL
import PIL.ImageColor

angles = list(range(0, 360, 30))

def hsv_str(h, s, v):
    return f'hsv({h},{s}%,{v}%)'

def hsv_to_rgb(h, s, v):
    return '#%02X%02X%02X' % PIL.ImageColor.getrgb(hsv_str(h, s, v))

def gen_colors(angle):
  return [hsv_to_rgb(angle, 100, 100),
          hsv_to_rgb(angle, 50, 100),
          hsv_to_rgb(angle, 100, 75),
          hsv_to_rgb(angle, 100, 50)]

colors = [hsv_to_rgb(0, 0, v) for v in (100, 75, 50, 0)]
colors.extend(list(itertools.chain(*[gen_colors(a) for a in angles])))
colors = colors[0::4] + colors[1::4] + colors[2::4] + colors[3::4]
print(colors)
