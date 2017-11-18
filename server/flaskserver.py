import requests
import json
from PIL import Image
import shutil
import io
import os
from flask import Flask, redirect, url_for, request
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
        return "Success"


if __name__ == '__main__':
   app.run(debug = True)




r=requests.get("http://www.example.com/", headers={"content-type":"text"});