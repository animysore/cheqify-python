
# import the necessary packages
import cv2
from time import sleep
import numpy as np

def call(image):
    import cv2
    from sklearn.externals import joblib
    from skimage.feature import hog
    import numpy as np
    
    # Load the classifier
    #havent created one yet. 
    
    im = image
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (5, 5), 0)
    ret, im_th = cv2.threshold(im_gray, 120, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("Resulting Imasdangular ROIs", im_th)
    _,ctrs, hier = cv2.findContours(im_th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(ctr) for ctr in ctrs]
    for rect in rects:
        cv2.rectangle(im, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3) 
        leng = int(rect[3] * 1.6)
        pt1 = int(rect[1] + rect[3] // 2 - leng // 2)
        pt2 = int(rect[0] + rect[2] // 2 - leng // 2)
        roi = im_th[pt1:pt1+leng, pt2:pt2+leng]
        # Resize the image
        print(roi.shape[:2])
        if(roi.shape[0] > 28 and roi.shape[1] > 28):
            roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
            roi = cv2.dilate(roi, (3, 3))
        else:
            continue;
        
        cv2.putText(im, '', (rect[0], rect[1]),cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 200, 200), 1)
    cv2.imshow("Resulting Image with Rectangular ROIs", im)
    
    
    
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
#ret,thresh = cv2.threshold(gray,199,255,1)
blur = cv2.medianBlur(img,5)
edged = cv2.Canny(blur, 25, 70)
zz,contours,h= cv2.findContours(edged,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

#cv2.imshow("asd",zz)
#cv2.drawContours(img, contours,-1, (0,255,0), 3)
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
crop_img = img[y:y+h, x:x+w]


#cropped image will hold the cheque (crop_img)
date = crop_img[int(h*0.07):int(h*0.12), int(w*0.75):int(w*0.965)]
name = crop_img[int(h*0.17):int(h*0.27), int(w*0.07):int(w*0.6)]
amt_words1 = crop_img[int(h*0.28):int(h*0.36), int(w*0.15):int(w*0.72)]
amt_words2 = crop_img[int(h*0.36):int(h*0.45), int(w*0.03):int(w*0.65)]
amt_no = crop_img[int(h*0.36):int(h*0.45), int(w*0.77):int(w*0.97)]
acc_no = crop_img[int(h*0.49):int(h*0.55), int(w*0.09):int(w*0.40)]


micr_code = crop_img[int(h*0.85):int(h*0.95), int(w*0.2):int(w*0.75)]
cv2.imshow('name',micr_code)

call(name)
cv2.line
cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 255, 0), 3)
#cv2.imshow("canvas", canvas)
#cv2.imshow("asdasd", date)
#cv2.imwrite("result.jpg", canvas)
#cv2.waitKey(0)

