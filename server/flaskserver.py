import requests
import json
from PIL import Image
import shutil
import io
import os
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from api import maincall, analyze
import cv2
import pyrebase

config = {
    "apiKey": "AIzaSyBUgnKb_q1B-z5UVaUPlMNVq8Hf8yhdQL0",
    "authDomain": "cheqify.firebaseapp.com",
    "databaseURL": "https://cheqify.firebaseio.com",
    "projectId": "cheqify",
    "storageBucket": "cheqify.appspot.com",
    "appId": "1:250796738064:web:81c3fa872c7d8ccce7ec95",
    "serviceAccount": "/Users/adishrao/Desktop/Projects/cheqify-python/server/serviceAccount.json"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

UPLOAD_FOLDER = '/home/aniruddha_mysore/cheqify-python/server/static/img'
STATIC_PATH = '/static'

app = Flask(__name__, static_url_path=STATIC_PATH)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/view', methods = ['POST', 'GET'])
def view():
    #images = [f for f in storage.list_files()]
    #urls = [img.get_url(None) for img in images]
    res = []
    print(res)
    return render_template('upload.html', res = res)

@app.route('/evaluate/<chq_num>')
def evaluate(chq_num):
    res = None
    
    #The sql query result gives an array. We want an associative array so we do 2 steps to match rows and columns:
    #step 1:  cursor.description holds column information. iterate to get just the name
    cols = ['','']
    #step 2: Use zip to match columns to rows from query result
    user_data=dict(zip(cols,res))

    eval_data = analyze(chq_num)

    return render_template('evaluate.html', eval_data=eval_data, user_data=user_data)

@app.route('/',methods = ['POST', 'GET'])
def new():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=8000)

