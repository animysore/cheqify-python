import requests
import flask
from flask import Flask
from flask import Flask, redirect, url_for, request
app = Flask(__name__)

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/index',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      #user = request.form['nm']
      return redirect(url_for('success',name = "Poulami"))
   else:
      #user = request.args.get('nm')
      #return redirect(url_for('success',name = user))
      if request.args.get('key') and request.args.get('key') == '9cf1034d-08c0-497e-b638-4fdb533f0a91':
        #request.headers.extend({'api-key': '9cf1034d-08c0-497e-b638-4fdb533f0a91'})
        return requests.get('http://apiplatformcloudse-gseapicssbisecond-uqlpluu8.srv.ravcloud.com:8001/ChequeInfo/8730826854').content
if __name__ == '__main__':
   app.run(debug = True)










#url = 'https://private-anon-125930794b-chequegetinfo.apiary-mock.com/ChequeInfo/TEAM_ID/CHQ_NUM/9cf1034d-08c0-497e-b638-4fdb533f0a91'
#para =  {
#            'team_id': '8730826854', 
#            'cheque_no': 123456, 
#           }
#
#print (len(str(para))) # Prints 6717
#with open("image.jpg", "rb") as image_file:
#    #encoded_image = base64.b64encode(image_file.read())
#    files = {'field_name': image_file}
#    #cookie = {cookiename: token.value}
#    r = requests.post(url, files=files,params=para)
#r = requests.post(url, params=payload)
#print (r.status_code) # Prints 200
#print (r.text) # Prints expected JSON results