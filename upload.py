import requests

url = 'https://private-anon-125930794b-chequegetinfo.apiary-mock.com/ChequeInfo/TEAM_ID/CHQ_NUM/9cf1034d-08c0-497e-b638-4fdb533f0a91'
para =  {
            'team_id': '8730826854', 
            'cheque_no': 123456, 
           }

print (len(str(para))) # Prints 6717
with open("image.jpg", "rb") as image_file:
    #encoded_image = base64.b64encode(image_file.read())
    files = {'field_name': image_file}
    #cookie = {cookiename: token.value}
    r = requests.post(url, files=files,params=para)
#r = requests.post(url, params=payload)
print (r.status_code) # Prints 200
print (r.text) # Prints expected JSON results