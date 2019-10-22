import requests
import json
import os
from flask import Flask, redirect, url_for, request, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from api import maincall, analyze
import cv2
import numpy as np
from matplotlib import pyplot as plt
from pytesseract import image_to_string 

def ocr(filename):
    img = cv2.imread(f'static/images/cheques/{filename}')

    max_brightness = 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    canvas = img.copy()
    #ret,thresh = cv2.threshold(gray,199,255,1)
    blur = cv2.medianBlur(img,5)
    edged = cv2.Canny(blur, 25, 70)
    contours,h= cv2.findContours(edged,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(img, contours,-1, (0,255,0), 3)

    for cnt in contours:
        rect = cv2.boundingRect(cnt)
        x, y, w, h = rect
        if w*h > 40000:
            mask = np.zeros(img.shape, np.uint8)
            mask[y:y+h, x:x+w] = img[y:y+h, x:x+w]
            brightness = np.sum(mask)
            if brightness > max_brightness:
                brightest_rectangle = rect
                max_brightness = brightness

    x, y, w, h = brightest_rectangle
    crop_img = img[y:y+h, x:x+w]

    edges = cv2.Canny(crop_img,101,200)

    crop_img = img[y:y+h, x:x+w]
    cheque = {}

    cheque['date'] = { 'bounds': (int(h*0.07), int(h*0.14), int(w*0.75),int(w*0.965) )}
    cheque['name'] = { 'bounds': (int(h*0.17), int(h*0.27), int(w*0.07),int(w*0.6) )}
    cheque['amt_words1'] = { 'bounds': (int(h*0.28), int(h*0.36), int(w*0.15),int(w*0.72) )}
    cheque['amt_words2'] = { 'bounds': (int(h*0.36), int(h*0.45), int(w*0.03),int(w*0.65) )}
    cheque['amt_no'] = { 'bounds': (int(h*0.36), int(h*0.45), int(w*0.77),int(w*0.97) )}
    cheque['acc_no'] = { 'bounds': (int(h*0.49), int(h*0.55), int(w*0.09),int(w*0.40) )}
    cheque['micr_code'] = { 'bounds': (int(h*0.85), int(h*0.95), int(w*0.2 ),int(w*0.75) )}

    out = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    text = {}

    for f in cheque:
        y0, y1, x0, x1 = cheque[f]['bounds']
        crop_field = crop_img[y0:y1,x0:x1]
        cv2.rectangle(out, (x0,y0),(x1,y1), color=(0,255,0), thickness=3 )
        text[f] = image_to_string(crop_field)
        print(f, ':' , text[f])

    
    cv2.imwrite(f'static/images/cropped/{filename}',cv2.resize(crop_img,  (640,350)))
    cv2.imwrite(f'static/images/canny/{filename}',cv2.resize(out,  (640,350)))
    return text

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
            text_data = ocr(file.filename)
            with open('./static/data/'+filename[:-4]+'_analyze.txt','w') as fil:
                fil.write('1950020'+'\n')
                fil.write(text_data['amt_words1']+'\n')
                fil.write(text_data['amt_no']+'\n')
                fil.write('__/__/____'+'\n')
                fil.write(text_data['micr_code'].split()[1]+'\n')
                fil.write(text_data['micr_code'].split()[3]+'\n')
                fil.write(text_data['name']+'\n')
                fil.write(text_data['acc_no']+'\n')
                fil.write(('yes'+'\n')*2)
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
        with open('./static/data/'+str(chq_num)[:-4]+'_analyze.txt') as f:
            eval_data = dict() 
            for i,val in enumerate(f.read().splitlines()):
                eval_data[fields[i]] = val
    except: 
        user_data = dict()
        eval_data = dict()
        
    user_data['chq_num'] = chq_num
    return render_template('evaluate.html', eval_data=eval_data, user_data=user_data)

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == 'admin@pes.edu':
            if request.form['password'] == 'admin123':
                return redirect(url_for('index'))
            else:
                flash("Invalid Email or Password")
        elif request.form['password'] != 'admin123':
            flash("Invalid Email or Password")
        else:
            flash("Invalid Email or Password")
    return render_template('login.html')

if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=8000)
