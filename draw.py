import colorsys
from functools import lru_cache
from time import sleep
from PIL import Image, ImageDraw
from random import Random


@lru_cache
def random_color(seed=0):
    rng = Random(seed)
    h, s, l = (rng.random(),                # noqa: E741
               0.5 + rng.random()/2.0,
               0.4 + rng.random()/5.0)

    r, g, b = [int(256*i) for i in colorsys.hls_to_rgb(h, l, s)]
    return r, g, b


img_height = 300
img_padding = 10

bin_width = 20
bin_margin = 5
bin_padding = 1
bin_count = 10

item_margin = 0

bin_height = img_height - 2*(img_padding+bin_margin)


def plot(solution):
    bin_count = len(solution.bins)
    bin_size = solution.bin_size
    scale = bin_height / bin_size

    img_width = (bin_width+bin_margin)*bin_count + img_padding*2-bin_margin

    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    for bin_index, bin in enumerate(solution):

        x0 = img_padding + bin_index*(bin_width+bin_margin)
        y0 = img_padding
        x1 = img_padding + (bin_index+1)*(bin_width+bin_margin) - bin_margin
        y1 = img_padding + scale*bin_size

        # Draw bins
        draw.rectangle((x0-bin_padding,
                        y0-bin_padding,
                        x1+bin_padding,
                        y1+bin_padding
                        ), outline='black')

        # Draw items
        for item in bin:
            y1 = y0 + item*scale
            draw.rectangle((x0+item_margin,
                            y0+item_margin,
                            x1-item_margin,
                            y1-item_margin),
                           fill=random_color(item),
                           outline='black')
            y0 = y1

    img.save('result.png')
    sleep(0.1)
    # img.show()

    return img


# class Plotter:
#     SEED = 0
#     rng: Random

#     def __init__(self) -> None:
#         self.rng = Random(self.SEED)

#     def reset_seed(self):
#         self.rng.seed()
