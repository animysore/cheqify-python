import requests
import json
from PIL import Image
import shutil
import io
from flask import Flask, redirect, url_for, request
import sqlite3
import os
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
    if(id == "964626"):
        data = {'ben_name': "Aniruddha",'chq_num': 923468, 'chq_date':'12/11/2017', 'amount_words': "Ten Thousand Rupees Only", 'amount_digit': 10000, 'payee_ac_no':45448795444,'amt_match':1, 'san_no':4545009, 'micr_code':213142, 'chq_stale': 0}
    elif(id == "994626"):
        data = {'ben_name': "Poulami",'chq_num': 567354, 'chq_date':'15/11/2017', 'amount_words': "Thirty Thousand Rupees Only", 'amount_digit': 30000, 'payee_ac_no':98719781987,'amt_match':1, 'san_no':8908008, 'micr_code':12314, 'chq_stale': 0}
    elif(id == "3"):
        data = {'ben_name': "Kushal",'chq_num': 923468, 'chq_date':'11/11/2017', 'amount_words': "Twenty Thousand Rupees Only", 'amount_digit': 20000, 'payee_ac_no':45645634556,'amt_match':1, 'san_no':1231144, 'micr_code':786678, 'chq_stale': 0}
    else:
        data = {'ben_name': "Adish",'chq_num': 923468, 'chq_date':'129/11/2017', 'amount_words': "Fifty Thousand Rupees Only", 'amount_digit': 50000, 'payee_ac_no':34522341234,'amt_match':1, 'san_no':7897123, 'micr_code':345345, 'chq_stale': 0}
    return data