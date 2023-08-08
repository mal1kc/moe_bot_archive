# file where detection loop is stored
# Path: src\detection_utils.py
# importing libraries
import os
from multiprocessing.connection import PipeConnection
from pathlib import Path

import pyautogui

# detection loop function

# check close loop


def tespitDongusu(conn: PipeConnection, threshold: float):
    """
    detection loop to detect objects in screenshot
    """
    # use with pyautogui.locateOnScreen() to find coordinates of objects
    # start detection loop
    while True:
        # locate on screen of imgs folder imgs if found
        for img in os.listdir(Path("imgs")):
            event = conn.recv()  # wait for event from main process
            assert img.endswith(".png"), "image file must be .png"
            # use locateOnScreen() to find coordinates of object
            if event == "close":
                conn.send("closing")
                conn.close()
                return
            result = pyautogui.locateOnScreen(str(Path("imgs", img)), grayscale=True, confidence=threshold)
            if result is not None:
                # if object is found add coordinates to queue
                conn.send(["found", result])
                # print('found ' + img + ' at ' + str(result))

        # add coordinates to queue
