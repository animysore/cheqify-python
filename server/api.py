import requests
import json
from PIL import Image
import shutil
import io
from flask import Flask, redirect, url_for, request
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
    with open("img"+str(i)+".jpg", 'wb') as f:
        f.write(r.content)

def maincall():
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
        call(url,i)
#maincall()


    #print(data)
    