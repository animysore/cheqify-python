import cv2
from time import sleep
import numpy as np
from PIL import Image 
import json
import sqlite3
from pytesseract import image_to_string 

conn = sqlite3.connect('/home/aniruddha/Documents/Github/cheqify-python/server/data.db')
cur = conn.cursor()
cur.execute("SELECT chq_num FROM IMAGEINFO")
file = cur.fetchall()

img = cv2.imread("/home/aniruddha/Documents/Github/cheqify-python/server/static/img/{}.jpg".format(file[2][0]))
print(file[1][0])
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


im = img
crop_img = img[y:y+h, x:x+w]
date = crop_img[int(h*0.09):int(h*0.13), int(w*0.756):int(w*0.958)]
name = crop_img[int(h*0.17):int(h*0.267), int(w*0.1):int(w*0.6)]
amt_words1 = crop_img[int(h*0.28):int(h*0.36), int(w*0.15):int(w*0.72)]
amt_words2 = crop_img[int(h*0.36):int(h*0.45), int(w*0.03):int(w*0.65)]
amt_no = crop_img[int(h*0.36):int(h*0.45), int(w*0.77):int(w*0.97)]
acc_no = crop_img[int(h*0.49):int(h*0.55), int(w*0.09):int(w*0.40)]
micr_code = crop_img[int(h*0.85):int(h*0.95), int(w*0.2):int(w*0.75)]
cv2.imshow('name',name)
#cv2.waitKey(0)
date = Image.fromarray(date, 'RGB')
name = Image.fromarray(name, 'RGB')
amt_words1 = Image.fromarray(amt_words1, 'RGB')
amt_words2 = Image.fromarray(amt_words2, 'RGB')
amt_no = Image.fromarray(amt_no, 'RGB')
acc_no = Image.fromarray(acc_no, 'RGB')
d = image_to_string(date,lang='eng')
n = image_to_string(name,lang='eng')
a1 = image_to_string(amt_words1,lang='eng')
a1 = a1.rsplit(' ', 1)[0]
#print(a1)
a2 = image_to_string(amt_words2,lang='eng')
ano = image_to_string(amt_no,lang='eng')
ano =int(''.join(c for c in ano if c.isdigit()))
acno = image_to_string(acc_no,lang='eng')
data = {'cheque':[{'date': d,'name': n, 'amount1': a1, 'amount2': a2,'Ammount(Numbers)': ano,'Account Number': acno}]}
print(data)
#with open('data.json', 'w') as outfile:  
#    json.dump(data, outfile)
