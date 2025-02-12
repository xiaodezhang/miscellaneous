from numpy.lib import math
import cv2 as cv
import numpy as np

def cyan_enhance():
    return [[255, 255, i] for i in reversed(range(256))]

def blue_enhance():
    return [[255, i, 0] for i in reversed(range(128))] + [[i, 0, 0] for i in reversed(range(128, 255))]

def green_enhance():
    return [[128, i, 0] for i in reversed(range(128, 256))]

def yellow_enhance():
    return [[i, 255, 255] for i in reversed(range(0, 128))]

def red_enhance():
    return [[0, i, 255] for i in reversed(range(0, 256))]

bgr_lut = cyan_enhance()+ blue_enhance()+ green_enhance() + yellow_enhance() + red_enhance()
# bgr_lut = [255, 255, 255] + blue_enhance() + yellow_enhance()+ red_enhance()

def value_to_color(value, max=255, min=0):
    index = 0
    try:
        index = math.floor((len(bgr_lut)-1)*(value-min)/(max-min))
        to = bgr_lut[index]
        return to
    except Exception as e:
        print('error: ', index)
        print('value: ', value)

# print(value_to_color(0))

user_lut = cv.imread('image/colormap/colorMap1.jpg')
user_lut = cv.rotate(user_lut, cv.ROTATE_90_CLOCKWISE)
user_lut = cv.resize(user_lut, (1, 256), interpolation=cv.INTER_NEAREST)
# user_lut[0, 0] = [59, 54, 49]
user_lut[0, 0] = [0, 0, 0]
user_lut[0, 0] = [255, 255, 255]
