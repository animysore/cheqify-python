import cv2
import numpy as np
from matplotlib import pyplot as plt
from pytesseract import image_to_string 

def ocr(filename):
    img = cv2.imread(f'static/images/cheques/{filename}')

    max_brightness = 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    canvas = img.copy()
    #ret,thresh = cv2.threshold(gray,199,255,1)
    blur = cv2.medianBlur(img,5)
    edged = cv2.Canny(blur, 25, 70)
    contours,h= cv2.findContours(edged,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

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
    crop_img = img[y:y+h, x:x+w]

    edges = cv2.Canny(crop_img,101,200)

    crop_img = img[y:y+h, x:x+w]
    cheque = {}

    cheque['date'] = { 'bounds': (int(h*0.07), int(h*0.14), int(w*0.75),int(w*0.965) )}
    cheque['name'] = { 'bounds': (int(h*0.17), int(h*0.27), int(w*0.07),int(w*0.6) )}
    cheque['amt_words1'] = { 'bounds': (int(h*0.28), int(h*0.36), int(w*0.15),int(w*0.72) )}
    cheque['amt_words2'] = { 'bounds': (int(h*0.36), int(h*0.45), int(w*0.03),int(w*0.65) )}
    cheque['amt_no'] = { 'bounds': (int(h*0.36), int(h*0.45), int(w*0.77),int(w*0.97) )}
    cheque['acc_no'] = { 'bounds': (int(h*0.49), int(h*0.55), int(w*0.09),int(w*0.40) )}
    cheque['micr_code'] = { 'bounds': (int(h*0.85), int(h*0.95), int(w*0.2 ),int(w*0.75) )}

    out = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    text = {}

    for f in cheque:
        y0, y1, x0, x1 = cheque[f]['bounds']
        crop_field = crop_img[y0:y1,x0:x1]
        cv2.rectangle(out, (x0,y0),(x1,y1), color=(0,255,0), thickness=3 )
        text[f] = image_to_string(crop_field)
        print(f, ':' , text[f])

    cv2.imwrite(f'static/images/canny/{filename}',out)
    return text
