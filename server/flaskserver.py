import requests
import json
from PIL import Image
import shutil
import io
import sqlite3
import os
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from api import call, maincall

UPLOAD_FOLDER = '/home/poulami/Documents/Github/cheqify-python/server'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
@app.route('/index',methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        #user = request.form['
        maincall()
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM IMAGEINFO")
        list = cur.fetchall()
        return render_template('upload.html', list = list)
@app.route('/',methods = ['POST', 'GET'])
def new():
    return render_template('index.html')
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')




r=requests.get("http://www.example.com/", headers={"content-type":"text"});