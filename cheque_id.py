
# import the necessary packages
import cv2
from time import sleep
import numpy as np
img = cv2.imread("image.jpg")
#img = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
#edges = cv2.Canny(img,20,100)
#
#key = cv2.waitKey(1) & 0xFF
#
#
#cv2.imshow('mask',edges)
#cv2.imshow("Frame", frame)

max_brightness = 0
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canvas = img.copy()
ret,thresh = cv2.threshold(gray,199,255,1)
edged = cv2.Canny(gray, 30, 200)
zz,contours,h= cv2.findContours(edged,2,3)
cv2.imshow("asd",zz)
cv2.drawContours(img, contours,-1, (0,255,0), 3)
for cnt in contours:
    rect = cv2.boundingRect(cnt)
    x, y, w, h = rect
    if w*h > 40000:
        mask = np.zeros(img.shape, np.uint8)
        mask[y:y+h, x:x+w] = img[y:y+h, x:x+w]
        brightness = np.sum(mask)
        if brightness > max_brightness:
            brightest_rectangle = rect
            max_brightness = brightness

x, y, w, h = brightest_rectangle
cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 255, 0), 3)
cv2.imshow("canvas", canvas)
cv2.imshow("asdasd", img)
#cv2.imwrite("result.jpg", canvas)
cv2.waitKey(0)

