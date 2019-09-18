import requests
import json
import os
from flask import Flask, redirect, url_for, request, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from api import maincall, analyze
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

UPLOAD_FOLDER = './static/images/cheques'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

STATIC_PATH = '/static'

app = Flask(__name__, static_url_path=STATIC_PATH)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/view', methods = ['POST', 'GET'])
def view():
    images = os.listdir('./static/images/cheques')
    res = [(img[:-4],img) for img in images]
    return render_template('gallery.html', res = res)

@app.route('/evaluate/<chq_num>')
def evaluate(chq_num):
    res = None
    user_data = {
        'chq_num': chq_num,
        'amount_words': 'Hundred only',
        'amount_digit': 100,
        'chq_date': 'Never',
        'micr_code': '1234',
        'san_no': '5567',
        'ben_name': 'Aniruddha',
        'payee_ac_no': '8302013',
        'chq_stale': 'Stale Bread',
        'amt_match': 'Yes',
    }
    eval_data = analyze(chq_num)
    return render_template('evaluate.html', eval_data=eval_data, user_data=user_data)

@app.route('/',methods = ['POST', 'GET'])
def new():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=8000)

