from PIL import Image
from pytesser import *

image_file = 'image.tif'
im = Image.open(image_file)
text = image_to_string(im)
text = image_file_to_string(image_file)
text = image_file_to_string(image_file, graceful_errors=True)
print("=====output=======\n")
print(text)
