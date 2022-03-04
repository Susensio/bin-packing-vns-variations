import colorsys
from time import sleep
from PIL import Image, ImageDraw
from random import random, seed


def random_color():
    h, s, l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0  # noqa: E741
    r, g, b = [int(256*i) for i in colorsys.hls_to_rgb(h, l, s)]
    return r, g, b


img_height = 700
img_padding = 10

bin_width = 20
bin_margin = 5
bin_padding = 1
bin_count = 10

item_margin = 0

bin_height = img_height - 2*(img_padding+bin_margin)


def plot(solution):
    seed(0)
    bin_count = len(solution.bins)
    bin_size = solution.bin_size
    scale = bin_height / bin_size

    img_width = (bin_width+bin_margin)*bin_count + img_padding*2-bin_margin

    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    for b, bin_ in enumerate(solution):
        x0 = img_padding + b*(bin_width+bin_margin)
        y0 = img_padding
        x1 = img_padding + (b+1)*(bin_width+bin_margin) - bin_margin
        y1 = img_padding + scale*bin_size

        draw.rectangle((x0-bin_padding,
                        y0-bin_padding,
                        x1+bin_padding,
                        y1+bin_padding
                        ), outline='black')

        for item in bin_:
            y1 = y0 + item*scale
            draw.rectangle((x0+item_margin,
                            y0+item_margin,
                            x1-item_margin,
                            y1-item_margin),
                           fill=random_color(),
                           outline='black')
            y0 = y1

    img.show()
    sleep(0.1)
