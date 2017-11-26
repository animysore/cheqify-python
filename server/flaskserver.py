import requests
import json
from PIL import Image
import shutil
import io
import sqlite3
import os
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from api import call, maincall, analyze
import cv2

UPLOAD_FOLDER = '/home/aniruddha_mysore/cheqify-python/server/static/img'
STATIC_PATH = '/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__, static_url_path=STATIC_PATH)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
@app.route('/index',methods = ['POST', 'GET'])
def getdb():
    maincall()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM IMAGEINFO")
    res = cur.fetchall()
    print(res)
    return render_template('upload.html', res = res)

@app.route('/view', methods = ['POST', 'GET'])
def view():
    print('Rec')
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM IMAGEINFO")
    res = cur.fetchall()
    print(res)
    return render_template('upload.html', res = res)

@app.route('/evaluate/<chq_num>')
def evaluate(chq_num):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM IMAGEINFO where chq_num = {}".format(chq_num))
    res = cur.fetchall()
    
    #The sql query result gives an array. We want an associative array so we do 2 steps to match rows and columns:
    #step 1:  cursor.description holds column information. iterate to get just the name
    cols = [col[0] for col in cur.description]
    #step 2: Use zip to match columns to rows from query result
    user_data=dict(zip(cols,res[0]))

    eval_data = analyze(chq_num)

    return render_template('evaluate.html', eval_data=eval_data, user_data=user_data)


@app.route('/',methods = ['POST', 'GET'])
def new():
    return render_template('index.html')
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=8000)

