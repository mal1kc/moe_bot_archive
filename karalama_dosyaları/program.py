import cv2
import numpy as np
import pyautogui
from pynput import keyboard

photo_inx = 24


def screenshot():
    global photo_inx
    ekrangor = pyautogui.screenshot()
    ekrangor = cv2.cvtColor(np.array(ekrangor.convert("RGB")), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"ekrangor-{photo_inx}.png", ekrangor)


def on_press(key):
    global photo_inx
    if key == keyboard.KeyCode.from_char("s"):
        photo_inx = photo_inx + 1
        screenshot()
    if key == keyboard.Key.esc:
        quit()


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
