import requests
import json
import os
from flask import Flask, redirect, url_for, request, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from api import maincall, analyze


UPLOAD_FOLDER = './static/images/cheques'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

STATIC_PATH = '/static'

app = Flask(__name__, static_url_path=STATIC_PATH)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'I am a random secret key'
fields = ['chq_num','amount_words', 'amount_digit', 'chq_date',
        'micr_code','san_no','ben_name','payee_ac_no','chq_stale','amt_match']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #try:
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
            field_list = ['cheq_num','sum_in_words','sum_in_num','cheq_date','MICR','SAN','name','acc_no','Chq_Stale','Amount_Match']
            with open('./static/data/'+filename[:-4]+'.txt','w') as fil:
                for key in field_list:
                    fil.write(request.form[key]+'\n')
            return redirect(url_for('gallery'))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/gallery')
def gallery():
    images = os.listdir('./static/images/cheques')
    # Get list of (filename without ext, full filename)
    res = [(img[:-4],img) for img in images]
    return render_template('gallery.html', res = res)


@app.route('/evaluate/<chq_num>')
def evaluate(chq_num):
    try:
        with open('./static/data/'+str(chq_num)[:-4]+'.txt') as f:
            user_data = dict() 
            for i,val in enumerate(f.read().splitlines()):
                user_data[fields[i]] = val
    except: 
        user_data = dict()
        
    user_data['chq_num'] = chq_num
    eval_data = analyze(chq_num)
    return render_template('evaluate.html', eval_data=eval_data, user_data=user_data)

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=8000)

