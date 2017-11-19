import requests
import json
from PIL import Image
import shutil
import io
from flask import Flask, redirect, url_for, request
import sqlite3
import os

script_dir = os.path.dirname(__file__) 
#app = Flask(__name__)
def call(url,i):
    para =  {
                'team_id': '8730826854', 
                'cheque_no': 123456, 
            }
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
    conn.execute('''DROP TABLE if exists IMAGEINFO''')
    conn.commit()
    conn.execute('''CREATE TABLE IMAGEINFO
         (amt_match char(20),
	      chq_date  date,
	      micr_code int,
	      payee_ac_no int,
	      amount_digit real,
	      chq_num int ,
	      san_no int,
	      chq_stale char(20),
	      amount_words char(100),
	      ben_name char(100),
	      act_type char(100));''')

    url = 'http://apiplatformcloudse-gseapicssbisecond-uqlpluu8.srv.ravcloud.com:8001/ChequeInfo/8730826854'
    para =  {
                'team_id': '8730826854', 
                'cheque_no': 123456, 
            }
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
        url = data['items'][i]['links'][0]['href']
        conn.execute("INSERT INTO IMAGEINFO (amt_match,chq_date,micr_code,payee_ac_no,amount_digit,chq_num,san_no,chq_stale,amount_words,ben_name,act_type)\
        VALUES (?,?,?,?,?,?,?,?,?,?,?)",(data['items'][i]['amt_match'],data['items'][i]['chq_date'],data['items'][i]['micr_code'],data['items'][i]['payee_ac_no'],data['items'][i]['amount_digit'],data['items'][i]['chq_num'],data['items'][i]['san_no'],data['items'][i]['chq_stale'],data['items'][i]['amount_words'],data['items'][i]['ben_name'],data['items'][i]['act_type']));        
        conn.commit()
        call(url,data['items'][i]['chq_num'])
    conn.close()
#maincall()


    #print(data)
    
def dummy_data(id):
	if(id == 964626):
		data = {'name': "Aniruddha",'chq_no': 923468, 'date':'12/11/2017', 'amt': 10000, 'acc':45448795444,'valid':True, 'SAN':4545009, 'micr':213142}
		return data
	if(id == 2):
		data = {'name': "Poulami",'chq_no': 567354, 'date':'15/11/2017', 'amt': 30000, 'acc':98719781987,'valid':True, 'SAN':8908008, 'micr':12314}
		return data
	if(id == 3):
		data = {'name': "Kushal",'chq_no': 923468, 'date':'11/11/2017', 'amt': 20000, 'acc':45645634556,'valid':True, 'SAN':1231144, 'micr':786678}
		return data
	if(id == 4):
		data = {'name': "Adish",'chq_no': 923468, 'date':'129/11/2017', 'amt': 50000, 'acc':34522341234,'valid':True, 'SAN':7897123, 'micr':345345}
		return data