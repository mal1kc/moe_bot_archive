import cv2 as cv
import numpy as np
import pyautogui
from pynput import keyboard


def main():
    print("başladı")
    # resim = cv.imread("kizkulesi.jpg")
    ekrangor = pyautogui.screenshot()
    # ekrangor = ekrangor.resize((1920,1080))
    ekrangor = cv.cvtColor(np.array(ekrangor.convert("RGB")), cv.COLOR_RGB2BGR)
    cv.imwrite("ekrangor.png", ekrangor)
    # ekrangor = cv.imread("ekrangor.png")
    # cv.imshow('ekrangor',ekrangor)
    # cv.waitKey()
    # ekrangor_gri = cv.cvtColor( ekrangor,cv.COLOR_BGR2GRAY)
    # cv.imshow('ekrangorgri',ekrangor_gri)
    # cv.waitKey()s
    # cv.imshow("resim penceresi", resim)
    # cv.imshow("resim penceresi",ekrangor_gri)
    template = cv.imread("uhh.png")
    # cv.imshow('template',template)
    # cv.waitKey()
    # plt.imshow(resim)
    # plt.show()

    # k=cv.waitKey(0)
    # yer=np.zeros(resim.shape)
    # if k==113:
    #     print("q tuşuna bas")

    # elif k==ord("a"):
    #     print("a tuşuna basıldı")
    #     yer = cv.cvtColor(resim, cv.COLOR_BGR2GRAY)
    #     cv.imwrite("kizkulesigri.jpg", yer)d
    # (templateB, templateG, templateR) = cv.split(template)
    # (ekrangorB ,ekrangorG ,ekrangorR) = cv.split(ekrangor)
    # w, h = templateB.shape[::-1]
    # blue_pints = template_match_with_layer(ekrangorB,templateB,"res_blue.png")
    # green_points = template_match_with_layer(ekrangorG,templateG,"res_gree.png")
    # red_points = template_match_with_layer(ekrangorR,templateR,"res_red.png")

    template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    ekrangor_gray = cv.cvtColor(ekrangor, cv.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]
    gray_points = template_match_with_layer(ekrangor_gray, template_gray, "res_gray.png", thresh=0.3)
    for point in gray_points:
        cv.rectangle(ekrangor, point, (point[0] + w, point[1] + h), (0, 255, 255), 2)
    cv.imwrite("cikti_1.jpeg", ekrangor)

    ekrangor_gray_1_5 = cv.resize(ekrangor_gray, (1280, 720), interpolation=cv.INTER_AREA)

    gray_points = template_match_with_layer(ekrangor_gray_1_5, template_gray, "res_gray.png", thresh=0.3)
    for point in gray_points:
        cv.rectangle(ekrangor_gray_1_5, point, (point[0] + w, point[1] + h), (0, 255, 255), 2)
    cv.imwrite("cikti_1_5.jpeg", ekrangor_gray_1_5)

    print("işlembitti")
    # for bp in blue_points:
    #     print(bp)
    # for gp in green_points:
    #     print(gp)
    # for rp in red_points:
    #     print(rp)

    # res = cv.matchTemplate(ekrangor_gri,template,cv.TM_CCOEFF_NORMED)
    # threshold = 0.45656
    # cv.imwrite("ress.png",res)
    # loc = np.where( res >= threshold)
    # for pt in zip(*loc[::-1]):
    #     cv.rectangle(ekrangor, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    # cv.imwrite('res.png',ekrangor)
    # print("işlem bitti")
    # cv.destroyWindow("resim penceresi")


def template_match_with_layer(src_layer, template_layer, fname, thresh=0.5, opcode=cv.TM_CCOEFF_NORMED):
    res = cv.matchTemplate(src_layer, template_layer, opcode)
    cv.imwrite(fname, res)
    loc = np.where(res >= thresh)
    points = zip(*loc[::-1])
    return points


def on_release(key):
    print("{0} released".format(key))
    if key == keyboard.KeyCode.from_char("s"):
        main()
    if key == keyboard.KeyCode.from_char("d"):
        return quit()


with keyboard.Listener(on_release=on_release) as listener:
    listener.join()

# listener = keyboard.Listener()

# import cv2
# import numpy as np

# img_rgb = cv2.imread('ekrangor.png')
# img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

# template = cv2.imread('wood2.png',0)
# w, h = template.shape[::-1]
# res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
# cv2.imwrite("res.png",res,cv2.COLOR_GRAY2BGR)
# threshold = 0.5
# loc = np.where( res >= threshold)
# for pt in zip(*loc[::-1]):
#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
# cv2.imwrite("cikti.jpeg",img_rgb)
# cv2.imshow('Detected',img_rgb)
