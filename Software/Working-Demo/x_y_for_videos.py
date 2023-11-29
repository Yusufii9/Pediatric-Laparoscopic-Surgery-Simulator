import cv2


def click_button(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"X: {x}, Y: {y}")


cap = cv2.VideoCapture("outpy.mp4")

ret, frame = cap.read()

if ret:
    cv2.imshow("Frame", frame)
    cv2.setMouseCallback("Frame", click_button)

cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()