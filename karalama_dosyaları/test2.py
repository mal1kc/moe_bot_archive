import cv2 as cv

cam = cv.VideoCapture(2)

if not cam.isOpened():
    print("kamera tanınmadı")
    exit()


while True:
    ret, frame = cam.read()

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    if not ret:
        print("kameradan görüntü alınamadı")
        break
    cv.imshow("kamera", frame)

    if cv.waitKey(1) & 0xFF == ord("q"):
        print("görüntü sonlandırıldı")
        break

cam.release()
cv.destroyAllWindows()
