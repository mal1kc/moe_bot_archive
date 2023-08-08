from functools import partial

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab


def screenshot():
    global photo_inx
    ekrangor = pyautogui.screenshot()
    ekrangor = cv2.cvtColor(np.array(ekrangor.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"./tmp/ekrangor.png", ekrangor)


if __name__ == "__main__":
    # from ctypes import windll
    # SM_XVIRTUALSCREEN = 76
    # SM_YVIRTUALSCREEN = 77
    # SM_CXVIRTUALSCREEN = 78
    # SM_CYVIRTUALSCREEN = 79
    # SM_CMONITORS = 80
    # left = windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    # top = windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    # width = windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    # height = windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    # print(left, top, width, height)

    ImageGrab.grab = partial(ImageGrab.grab, bbox=(1600, -172, 3520, 907), all_screens=True)
    screenshot()

# from functools import partial
# ImageGrab.grab = partial(ImageGrab.grab, bbox=(1600, -172, 3520, 907), all_screens=True)

# grabb = ImageGrab.grab

# import cv2
# import numpy as np
# import pyautogui
# from PIL import ImageGrab


# def screenshot():
#     global photo_inx
#     ekrangor = pyautogui.screenshot()
#     ekrangor = cv2.cvtColor(np.array(ekrangor.convert('RGB')), cv2.COLOR_RGB2BGR)
#     cv2.imwrite('./tmp/ekrangor.png', ekrangor)


# def imagegrap_2ndmon(bbox=None, include_layered_windows=False, all_screens=True, xdisplay=None):
#     # wrapper for imagegrab.grab(bbox=(0, 0, 1920, 1080))
#     # auto chaned values to 2nd monitor versions
#     # 2nd monitor resolution: 1920x1080
#     # 1st monitor resolution: 1600x900

#     x_ = 1600
#     y_ = -172
#     w_ = 3520
#     h_ = 907

#     if bbox:
#         x_ = bbox[0] + 1600
#         y_ = bbox[1] - 172
#         w_ = bbox[2] + 1600
#         h_ = bbox[3] - 172

#     return grabb(
#         bbox=(x_, y_, w_, h_), include_layered_windows=include_layered_windows, all_screens=True, xdisplay=xdisplay
#     )


# ImageGrab.grab = imagegrap_2ndmon
