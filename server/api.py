import requests
import json
from time import sleep
import numpy as np
from PIL import Image
import shutil
import io
from flask import Flask, redirect, url_for, request
import sqlite3
import os
from pytesseract import image_to_string 
import cv2

script_dir = os.path.dirname(__file__) 
#app = Flask(__name__)
def call(url,i):
    headers = {'api-key': '9cf1034d-08c0-497e-b638-4fdb533f0a91'}
    #print (len(str(para))) # Prints 6717
    r = requests.get(url, headers=headers)
    #print (r.status_code) # Prints 200
    #print(type(image))

    #img = Image.open(StringIO(r.content))
    with open(os.path.join(script_dir, "static/img/"+str(i)+".jpg"), 'wb') as f:
        f.write(r.content)

def maincall():
    conn = sqlite3.connect('data.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS IMAGEINFO
         (amt_match char(20),
	      chq_date  date,
	      micr_code int,
	      payee_ac_no int,
	      amount_digit real,
	      chq_num int unique,
	      san_no int,
	      chq_stale char(20),
	      amount_words char(100),
	      ben_name char(100),
	      act_type char(100),
          encoding char(100));''')

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
  

    #print(NoOfImg)
    for i in range(NoOfImg):
        cur = conn.cursor()
        #only insert if cheque number does not already exist
        cur.execute("SELECT chq_num FROM IMAGEINFO where chq_num="+ str(data['items'][i]['chq_num']))
        if (cur.fetchall()==[] and data['items'][i]['chq_num']!=1234 and data['items'][i]['chq_num']!=12345 and data['items'][i]['chq_num']!=994626):
            url = data['items'][i]['links'][0]['href']
            conn.execute("INSERT INTO IMAGEINFO (amt_match,chq_date,micr_code,payee_ac_no,amount_digit,chq_num,san_no,chq_stale,amount_words,ben_name,act_type,encoding)\
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(data['items'][i]['amt_match'],data['items'][i]['chq_date'],data['items'][i]['micr_code'],data['items'][i]['payee_ac_no'],data['items'][i]['amount_digit'],data['items'][i]['chq_num'],data['items'][i]['san_no'],data['items'][i]['chq_stale'],data['items'][i]['amount_words'],data['items'][i]['ben_name'],data['items'][i]['act_type'],  data['items'][i]['encoding']));        
            conn.commit()
            call(url,data['items'][i]['chq_num'])

    conn.close()
#maincall()


    #print(data)
    
def analyze(chq_num):
    #conn = sqlite3.connect('data.db')
    #cur = conn.cursor()
    #cur.execute("SELECT * FROM IMAGEINFO where chq_num = "+chq_num)
    #res = cur.fetchall()
    #img = cv2.imread("static/img/{}.jpg".format(chq_num)
        
    img = cv2.imread("/home/aniruddha/Documents/Github/cheqify-python/server/static/img/{}.jpg".format(str(chq_num)))
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
    #with open('data.json', 'w') as outfile:  
#    json.dump(data, outfile)