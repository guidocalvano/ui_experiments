import matplotlib.pyplot as plt
import numpy as np
import freetype
from PIL import Image

from string import ascii_lowercase, ascii_uppercase

import pandas as pd


# https://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python
# https://freetype.org/freetype2/docs/tutorial/step2.html

def render(screen, bounding_box, text, font, color):
    font_map = font_table(font, [chr(i) for i in range(0, 127)])
    character_bitmaps = [font_map[c] for c in text]

    coordinates = text_coordinates(text, character_bitmaps)


    for (x, y), bitmap in zip(coordinates, character_bitmaps):

        w, h = bitmap.shape[0:2]
        if w == 0: continue
        if h == 0: continue

        # plt.imshow((screen[x: x + w, y: y + h, :] * (1 - bitmap[:,:,np.newaxis]) +
        #                               bitmap[:, :, np.newaxis] * color[np.newaxis, np.newaxis, :]))
        # plt.show()
        if x + w > screen.shape[0]: break
        if y + h > screen.shape[1]: break
        screen[x: x + w, y: y + h, :] = (screen[x: x + w, y: y + h, :] * (1 - (bitmap[:,:,np.newaxis] / 255)) +
                                         (bitmap[:, :, np.newaxis] / 255) * color[np.newaxis, np.newaxis, :])





def text_coordinates(text, character_bitmaps):
    lines = text.splitlines(True)

    coordinate_list = []
    i = 0
    current_x = 0
    current_y = 0
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            current_x += character_bitmaps[i].shape[0]

            coordinate_list.append([current_x, current_y])
            i += 1

        current_x = 0
        current_y += character_bitmaps[0].shape[1]

    # coordinates = np.array([[x * 20, y * 34]  for y, line in enumerate(lines) for x, c in enumerate(line)])
    coordinates = np.array(coordinate_list)

    return coordinates


def font_table(font, characters):

    return {c: font_to_array(font, c) for c in characters}

maxBearing=0
minBearing=100000

def font_to_array(font, c):
    global maxBearing, minBearing
    if ord(c) < 32: c = ' '
    if ord(c) >= 127: c = ' '

    font.load_char(c)
    bitmap = font.glyph.bitmap

    character_x = int(font.glyph.metrics.horiBearingX / 64)
    character_width = int(font.glyph.metrics.width / 64)
    character_y = int((font.size.ascender - font.glyph.metrics.horiBearingY) / 64)

    if font.glyph.bitmap_top != (int(font.glyph.metrics.horiBearingY / 64)):
        pass

    char_height_px = int(font.size.height / 64)
    char_advance_width_px = int(font.glyph.advance.x / 64) + 1
    # maybe font.glyph.metrics/horiAdvance

    minimum_descender = font.bbox.yMin / 64
    maximum_ascender = font.bbox.yMax / 64

    max_range = maximum_ascender - minimum_descender
    line_gap = char_height_px - max_range

    distance_base_line_top = maximum_ascender + line_gap / 2
    distance_base_line_bottom = abs(minimum_descender) + line_gap / 2

    print(F"NEXT CHAR {c}")
    print(f'{font.bbox.yMax=}')
    print(f'{font.bbox.yMin=}')

    print(f'{font.ascender=}')
    print(f'{font.size.ascender=}')
    print(f'{font.size.descender=}')

    print(f'{font.glyph.metrics.horiBearingY=}')
    print(f'{font.glyph.metrics.height=}')
    maxBearing = font.glyph.metrics.horiBearingY if maxBearing < font.glyph.metrics.horiBearingY else maxBearing
    print(f'{maxBearing=}')
    minBearing = font.glyph.metrics.horiBearingY if minBearing > font.glyph.metrics.horiBearingY else minBearing
    print(f'{minBearing=}')

    full_height = int((font.size.ascender - font.size.descender) / 64)
    print(f'{full_height=}')
    print(f'{font.size.height/64=}')
    print(f'{font.size.descender/64}')


    top = int(font.glyph.metrics.horiBearingY / 64)
    left = int(font.glyph.metrics.horiBearingX / 64)
    distance_glyph_top = char_height_px - top
    character = np.reshape(np.array(bitmap.buffer), [bitmap.rows, bitmap.width]).T

    background = np.zeros((max(char_advance_width_px, character_x + character.shape[0]), char_height_px), dtype=np.uint8)
    # x_min, y_min, x_max, y_max = font.bbox.xMin, font.bbox.yMin, font.bbox.xMax, font.bbox.yMax
    # array = np.zeros_like(font_to_array('a')) if (array.shape[0] == 0 or array.shape[1] == 0) else array
    visual = background.copy()

    if character_x < 0:
        raise Exception("Can't render with negative horizontal bearing x")
    visual[character_x :character_x + character.shape[0], character_y:(character_y + character.shape[1])] = character    # plt.imshow(array)
    # plt.show()


    return visual


def render_screen_of_ascii():
    screen = np.zeros([1920, 1080, 3], dtype=np.uint8)
    font = freetype.Face("NotoSansMath-Regular.ttf")
    # font = freetype.Face("whitneylight.otf")
    font = freetype.Face("JetBrainsMono-Regular.ttf")
    font.set_char_size(30 * 64)

    large_diverse_line = ''.join([chr(i) for i in range(32, 126)])
    testing_text = (large_diverse_line + "\n") * 25

    
    render(screen, [], testing_text , font, np.array([0,0,255]))

    Image.fromarray(np.transpose(screen, [1, 0, 2])).save("letter_rendering.png")
    plt.imshow(screen)

    plt.show()

def font_statistics(font_file_path):
    font = freetype.Face(font_file_path)
    font.set_char_size(30 * 64)

    character_set = ''.join([chr(i) for i in range(32, 126)])

    property_dict = {
        "ascender": [],
        "descender": [],
        "size.ascender": [],
        "size.descender": [],
        "size.height": [],
        "size.max_advance": [],
        "bbox.xMin": [],
        "bbox.yMin": [],
        "bbox.xMax": [],
        "bbox.yMax": [],
        "glyph.advance.x": [],
        "glyph.advance.y": [],

        "glyph.metrics.horiBearingX": [],
        "glyph.metrics.horiBearingY": [],
        "glyph.metrics.height": [],
        "glyph.metrics.width": [],
        "glyph.metrics.horiAdvance": [],

    }

    def collect_property(font, property):
        path = property.split('.')

        obj = font
        for segment in path:
            obj = getattr(obj, segment)

        return obj

    for character in character_set:
        font.load_char(character)

        for property in property_dict.keys():
            property_dict[property].append(collect_property(font, property))


    return pd.DataFrame.from_dict({'character': list(character_set), **property_dict})


def main():
    df = font_statistics("JetBrainsMono-Regular.ttf")
    pd.set_option('display.max_columns', None)
    df.describe()

def render_letter(l):
    face = freetype.Face("JetBrainsMono-Regular.ttf")
    face.set_char_size(48 * 64)
    face.load_char(l)
    bitmap = face.glyph.bitmap

    x_min, y_min, x_max, y_max = face.bbox.xMin, face.bbox.yMin, face.bbox.xMax, face.bbox.yMax
    array = np.reshape(np.array(bitmap.buffer), [bitmap.rows, bitmap.width])

    plt.imshow(array)
    plt.show()

    pass






if __name__ == '__main__':
    main()