import pytesseract
import cv2
import sys
import math
import numpy as np
from datetime import datetime,timedelta
import os
from PIL import Image
from os import listdir
from os.path import isfile, join
import re
import pandas as pd


base_dir ="/mnt/"
#base_dir =""                                                   #Uncomment to run locally

def ocr(file,lang,option,d): 
  # Define config parameters.
  # '--oem 1' for using LSTM OCR Engine
  config = ('-l '+lang+' --oem 1 --psm 3')
  if option == 1:
    # Read image from disk
    im = cv2.imread(file, cv2.IMREAD_COLOR)
  else :
    im = file
  
  if d == 1:
    # Without denoising (Ticker only)
    temp = im
    temp = cv2.bitwise_not(temp)
    temp = cv2.resize(temp, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = 127
    temp = cv2.threshold(temp, thresh, 255, cv2.THRESH_BINARY)[1]
    temp = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY_INV)[1]
    con = pytesseract.image_to_data(temp, output_type='data.frame')
    con = con[con.conf != -1]
    con = con.groupby(['block_num'])['conf'].mean()
    text = pytesseract.image_to_string(temp, config=config)
  else:
    #With denoising (Invertion)
    temp = im
    temp = cv2.fastNlMeansDenoisingColored(temp,None,20,10,7,21)
    temp = cv2.fastNlMeansDenoising(temp,None,10,7,21)
    temp = cv2.bitwise_not(temp)
    temp = cv2.resize(temp, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = 127
    temp = cv2.threshold(temp, thresh, 255, cv2.THRESH_BINARY)[1]
    #temp = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY_INV)[1]
    con = pytesseract.image_to_data(temp, output_type='data.frame')
    con = con[con.conf != -1]
    con = con.groupby(['block_num'])['conf'].mean()
    text = pytesseract.image_to_string(temp, config=config)
  
  #With denoising (Without invertion)
  temp1 =im
  temp1 = cv2.fastNlMeansDenoisingColored(temp1,None,20,10,7,21)
  temp1 = cv2.fastNlMeansDenoising(temp1,None,10,7,21)
  temp1 = cv2.bitwise_not(temp1)
  temp1 = cv2.resize(temp1, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
  thresh = 127
  if lang != 'ben':
    temp1 = cv2.threshold(temp1, thresh, 255, cv2.THRESH_BINARY)[1]
  temp1 = cv2.threshold(temp1, 0, 255, cv2.THRESH_BINARY_INV)[1]  
  con1 = pytesseract.image_to_data(temp1, output_type='data.frame')
  con1 = con1[con1.conf != -1]
  con1 = con1.groupby(['block_num'])['conf'].mean()    
  text1 = pytesseract.image_to_string(temp1, config=config) 

  # Test conditions
  f=0
  if con.empty and text != '' and con1.empty and text1 != '':
    return (text,con)
  if con.empty and con1.empty:
    if text1 != '':
      return (text1,con1)  
    else: return (text,con)
  elif con1.empty and text !='':
    con1 =con
    return (text,con)
  elif con.empty and text1 !='':
    con =con1
    return (text1,con1)
  if con[1] > con1[1]:
    text = text
  elif con1[1] >con[1]:
    text = text1
    con = con1    
  return(text,con)


# Write to output file   

def writefile(op,boxes,no,ms,base,text,lang):
  start = base+timedelta(milliseconds=ms)
  end = end = start + timedelta(milliseconds = 2200)
  st = int(''.join(re.findall('\d',str(start))))/1000000
  en = int(''.join(re.findall('\d',str(end))))/1000000

  # Modify ticker text for continuity
  splitted = text.split()
  if len(splitted)>2: 
    if re.findall('[A-Za-z0-9]',splitted[0]):
      if len(splitted[0])<6:                                      #English
        splitted = splitted[1:] 
    elif len(splitted[0])<=8:                                     #General
      splitted = splitted[1:]
    #Eliminate last word
    if re.findall('[A-Za-z0-9]',splitted[-1]):
      if len(splitted[-1])<=4:                                    #English
        splitted = splitted[:-1]
    elif len(splitted[-1])<=8:                                    #Hindi/Bengali
      splitted = splitted[:-1]
  text = ' '.join(splitted)

  # Write output to file
  op.write(str("%.3f"%round(st,3)) +'|'+str("%.3f"%round(en,3))+'|TIC2|'+str("%06d" %no)+'|'+\
    str("%03d" %int(boxes[0]))+' '+str("%03d" %int(boxes[2]))+' '+str("%03d" %abs(boxes[1]-boxes[0]))+' '+str("%03d" %abs(boxes[3]-boxes[2]))+'|')
  op.write(text.replace('\n',' ').replace('\r',' ')+'\n')


## fetch_output(file,boxes,frame_no,timestamp,start_time_utc,lang)

def ocr_ticker(op,boxes,no,ts,base,lang):
  text=''
  try:
    text,con = ocr(base_dir+'tickimg.jpg',lang,1,1)
    if "".join(text.split()) == '':
      raise Exception('blank')
    writefile(op,boxes,no,ts,base,text,lang)     
    os.remove(base_dir+'tickimg.jpg')
    os.remove(base_dir+'backup.jpg') 
  except:
    #Execute backup if tickimg is blank or exception
    try:
      text,con =ocr(base_dir+'backup.jpg',lang,1,1)
      if text != '':
        writefile(op,boxes,no,ts,base,text,lang)
      os.remove(base_dir+'tickimg.jpg')
      os.remove(base_dir+'backup.jpg') 
    except Exception as err:
      return
      ''' ERROR
      er = open(base_dir+'outputs/output1.txt',"a")
      er.write(str(no)+str(err))
      er.write('\n')
      er.close()'''
