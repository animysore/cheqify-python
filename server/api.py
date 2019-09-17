import requests
import json
from time import sleep
import numpy as np
from PIL import Image
import shutil
import io
from flask import Flask, redirect, url_for, request
import os
from pytesseract import image_to_string 
import cv2

script_dir = os.path.dirname(__file__) 

def maincall():
    #    amt_match char(20),
	#     chq_date  date,
	#     micr_code int,
	#      payee_ac_no int,
	#      amount_digit real,
	#      chq_num int unique,
	#      san_no int,
	#      chq_stale char(20),
	#     amount_words char(100),
	#      ben_name char(100),
	#      act_type char(100),
    #      encoding char(100));''')

    url = 'http://apiplatformcloudse-gseapicssbisecond-uqlpluu8.srv.ravcloud.com:8001/ChequeInfo/8730826854'
    
    headers = {'api-key': '9cf1034d-08c0-497e-b638-4fdb533f0a91'}
    r = requests.get(url, headers=headers)
    if(r.status_code == 200):
        data = json.loads(r.text)
        NoOfImg = data['count']
        with open('imagedata.json', 'w') as outfile:  
            json.dump(data, outfile)
    else:
        return "Fail"
    NoOfImg = data['count']
  
def analyze(chq_num):
    
    img = cv2.imread("/home/poulami/Documents/Github/cheqify-python/server/static/img/{}.jpg".format(str(chq_num)))
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
    cv2.imshow('name',amt_words1)
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
    #data = {'cheque':[{'date': d,'name': n, 'amount1': a1, 'amount2': a2,'Ammount(Numbers)': ano,'Account Number': acno}]}
    #print(data)
    data = {'ben_name': n,'chq_num': chq_num, 'chq_date':d, 'amount_words': a1, 'amount_digit': ano, 'payee_ac_no':acno,'amt_match':1, 'san_no':7897123, 'micr_code':345345, 'chq_stale': 0}
    return data
