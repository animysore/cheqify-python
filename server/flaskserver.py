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
    return render_template('upload.html', res = res)

@app.route('/view',methods = ['POST', 'GET'])
def view():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM IMAGEINFO")
    res = cur.fetchall()
    return render_template('upload.html', res = res)

@app.route('/evaluate/<chq_num>')
def evaluate(chq_num):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM IMAGEINFO where chq_num = {chq_num}")
    res = cur.fetchall()
    return render_template('evaluate.html', eval_data = analyze(chq_num), user_data = res)


@app.route('/',methods = ['POST', 'GET'])
def new():
    return render_template('index.html')
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')

