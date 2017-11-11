# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 15:36:06 2017

@author: Kushal
"""

from PIL import Image
import pytesseract

im = Image.open("result.jpg")

text = pytesseract.image_to_string(im, lang = 'eng')

print(text)