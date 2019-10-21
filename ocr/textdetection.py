import pytesseract
from datetime import datetime,timedelta
import cv2
import sys
import math
import re
import pickle
import numpy as np
import os
import os.path
#from bengali import ocr,fetch_output
from scene import ocr_ticker,ocr

class benhinocr:
  confThreshold = 0.5
  nmsThreshold = 0.5
  inpWidth = 480
  inpHeight = 320

  model = "frozen_east_text_detection.pb"

  kWinName = "Text Detector running"
  #cv2.namedWindow(kWinName, cv2.WINDOW_NORMAL)
  outNames = []
  outNames.append("feature_fusion/Conv_7/Sigmoid")
  outNames.append("feature_fusion/concat_3")

  textlist =[]
  scenetext = dict()

  def __init__(self):
    #Initialization
    self.base_dir = '/mnt/'
    self.video_dir = re.findall('/mnt/rds/redhen/gallina(/tv.*)',sys.argv[2])[0]
    #Local run
    #self.base_dir = ''
    #self.video_dir = sys.argv[2]

    self.video =sys.argv[1]
    self.lang = sys.argv[3]
  
    self.net = cv2.dnn.readNet(self.base_dir+"frozen_east_text_detection.pb")
  
    if os.path.isfile(self.base_dir+'tickimg.jpg'):
      print("removing")	
      os.remove(self.base_dir+'tickimg.jpg')
    if os.path.isfile(self.base_dir+'backup.jpg'):
      os.remove(self.base_dir+'backup.jpg') 
    print(self.video_dir, self.video, self.lang)

    self.op =open(self.base_dir+'outputs/'+self.video.replace('mp4','ocr'),'w+')
    f1 = open(self.video_dir+self.video.replace('mp4','txt'),'r')
    text = f1.read()
    split_head = text.split('\n')
    if re.findall('END|',split_head[-2]):
      self.endtag = split_head[-2]
      text = '\n'.join(split_head[:-2])
    elif re.findall('END|',split_head[-1]): 
      self.endtag = split_head[-1]
      text = '\n'.join(split_head[:-1])
    else:
      self.endtag = ''
    self.op.write(text+'\n')
    self.ts = re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}([:]\d+)?',text).group(0)
    self.base = (datetime.strptime(self.ts,"%Y-%m-%d %H:%M:%S")) - timedelta(hours=5,minutes=30)

  def scene(self,img,ms,no,boxes):
    try:
      text,con = ocr(img,self.lang,1,0)
      text = text.replace('\n',' ').replace('\r',' ')
      if text == '':
        raise Exception('error')
    except :
      try:
        #text,con = ocr(img,lang,1,1)
        return
        #print('aslt')
        #text = text.replace('\n',' ').replace('\r',' ')
      except Exception as err:
        er = open(self.base_dir+'outputs/output1.txt',"a")
        er.write("scene: "+str(err))
        er.close()
        return
    if text != '':
        if len(re.findall('[a-z0-9]',text.lower())) > (len(re.findall('[\u0900-\u097Fa-zA-Z0-9]',text))*0.5) and (con.empty or con[1] <65):
            return
        else:
            text_keychars = re.findall('[\u0900-\u097Fa-zA-Z0-9]',text)
            text_keychars = ''.join(text_keychars)
            start =self.base+timedelta(milliseconds=ms)
            end = start + timedelta(milliseconds = 2200)

            if text_keychars in self.scenetext:
              if(abs(self.scenetext[text_keychars][-1][7] - no) <= 330):
                self.scenetext[text_keychars][-1][7] = no
                self.scenetext[text_keychars][-1][1] = end
              else:
                self.textlist.append((text_keychars,len(self.scenetext[text_keychars])))
                self.scenetext[text_keychars].append([start,end,boxes[0],boxes[2],abs(boxes[1]-boxes[0]),abs(boxes[3]-boxes[2]),no,no,text])
            else:
              self.textlist.append((text_keychars,0))
              self.scenetext[text_keychars] = [[start,end,boxes[0],boxes[2],(boxes[1]-boxes[0]),(boxes[3]-boxes[2]),no,no,text]]

  def hashfn(self,vertex):
    return int(vertex/10)*10

  def ticker_detect(self,vertices,ticker):
    # is a ticker
    if ticker[2] > vertices[1][1]:
      ticker[2] = vertices[1][1]
    if ticker[3] < vertices[0][1]:
      ticker[3] = vertices[0][1]
    if ticker[0] > vertices[0][0]:
      if ticker[1]+100<vertices[0][0]:
        return ticker
      if vertices[0][0] < 0: 
        ticker[0] = 0
      else:
        ticker[0]  = vertices[0][0] 
    if ticker[1] < vertices[2][0] and vertices[2][0] < 640:
      ticker[1] = vertices[2][0]
    return ticker
        
  def find_boxes(self,vertices,array):
    y = self.hashfn(vertices[1][1])
    if y in array:
      array[y] = self.ticker_detect(vertices,array[y])
    elif y-10 in array:
      # y -10
      array[y -10] = self.ticker_detect(vertices,array[y-10])
    elif y+10 in array:
      # y+10
      array[y+10] = self.ticker_detect(vertices,array[y+10])    
    else:
      array[y] = [vertices[1][0],vertices[3][0],vertices[1][1],vertices[3][1]]
    return array

################################################### END ###################################################


def write_scenetext(ocr1):  
  for i,j in ocr1.textlist:
    d = ocr1.scenetext[i][j]
    st = ''.join(re.findall('\d',str(d[0])[:-3])) 
    en = ''.join(re.findall('\d',str(d[1])[:-3]))
    ocr1.op.write(st[:-3]+'.'+str("%.3d" %int(st[-3:])) +'|'+en[:-3]+'.'+str("%.3d" %int(en[-3:]))+'|OCR2|'+str("%06d" %d[6])+'|'+\
      str("%03d" %int(d[2]))+' '+str("%03d" %int(d[3]))+' '+str("%03d" %int(d[4]))+' '+str("%03d" %int(d[5]))+'|')
    ocr1.op.write(d[-1]+'\n')

def color_detect_ticker(frame):
    if frame.size == 0:
      return frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    blue_lower=np.array([99,115,150],np.uint8)
    blue_upper=np.array([110,255,255],np.uint8) 
    red_lower=np.array([136,87,111],np.uint8)
    red_upper=np.array([180,255,255],np.uint8)

    blue = cv2.inRange(hsv, blue_lower, blue_upper) 
    red = cv2.inRange(hsv, red_lower, red_upper) 

    kernal = np.ones((5 ,5), "uint8")
    blue=cv2.dilate(blue,kernal)
    red=cv2.dilate(red,kernal)
    resb=cv2.bitwise_and(frame, frame, mask = blue)
    resr=cv2.bitwise_and(frame, frame, mask = red)

    if (np.count_nonzero(resb)>800 and np.count_nonzero(resr)>3000):
      return 1
    else :
      return 0

def decode(scores, geometry, scoreThresh):
    detections = []
    confidences = []
    ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):
        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]
            # If score is lower than threshold score, move to next x
            if(score < scoreThresh):
                continue
            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]
            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]
            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])
            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0],  sinA * w + offset[1])
            center = (0.5*(p1[0]+p3[0]), 0.5*(p1[1]+p3[1]))
            detections.append((center, (w,h), -1*angle * 180.0 / math.pi))
            confidences.append(float(score))
    # Return detections and confidences
    return [detections, confidences]

print("press 1 to quit")

def detect_text(file,ocr1):
    no = 109
    cap = ap = cv2.VideoCapture(file)

    while cv2.waitKey(1) < 0:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
          break
        no+=1
        backup=0
        hasFrame, frame = cap.read()
        copy =frame
        if no%(110) != 0 :
          backup =1
          if (no-10)%(110) != 0:
            #cv2.imshow(kWinName,frame)
            continue
        
        arg =len(sys.argv)
        # Read frame 
        if not hasFrame:
            cv2.waitKey()
            break
        # Get frame height and width
        height_ = frame.shape[0]
        width_ = frame.shape[1]
        rW = width_ / float(ocr1.inpWidth)
        rH = height_ / float(ocr1.inpHeight)
        # Create a 4D blob from frame.
        blob = cv2.dnn.blobFromImage(frame, 1.0, (ocr1.inpWidth, ocr1.inpHeight), (123.68, 116.78, 103.94), True, False)
        # Run the model
        ocr1.net.setInput(blob)
        outs = ocr1.net.forward(ocr1.outNames)
        t, _ = ocr1.net.getPerfProfile()
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
        # Get scores and geometry
        scores = outs[0]
        geometry = outs[1]
        [boxes, confidences] = decode(scores, geometry, ocr1.confThreshold)
        # Apply NMS
        indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, ocr1.confThreshold,ocr1.nmsThreshold)
        
        #ticker coordinates x1:x2,y1:y2
        ticker =[999,0,999,0]
        array ={}
        ######################################### Iterate through each detected text region ###################################################
        for i in indices:
            snip = 0
            # get 4 corners of the rotated rect
            vertices = cv2.boxPoints(boxes[i[0]])
            # scale the bounding box coordinates based on the respective ratios
            for j in range(4):
                vertices[j][0] *= rW
                vertices[j][1] *= rH            
            if int(vertices[1][1]) >= 450:
              ticker = ocr1.ticker_detect(vertices,ticker)
              resp = 1
              continue
            else :  resp =0
            array = ocr1.find_boxes(vertices,array)

        ############################################################### END ################################################################### 
        # Put efficiency information
        cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
        
        # If ticker is detected crop it
        if ticker[2:] == [999,0]:
          cropped = np.empty(0)
        else:
          cropped = frame[int(453):int(485),int(1):int(500)]
          #cropped = frame[int(ticker[2]):int(ticker[3]),int(1):int(500)]                                        #Not hardcoded
          if color_detect_ticker(cropped):
            #array[int(ticker[2])] = [110,600,ticker[2],ticker[3]]                                               #Not hardcoded
            array[int(453)] = [110,600,453,485]
            cropped = np.empty(0)
        
        # Convert to grayscale
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        if backup == 0:
          if cropped.size:
            # Convert ticker to grayscale
            cropped = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
            cv2.imwrite(ocr1.base_dir+'tickimg.jpg',cropped)
            #Extras
            #cc = copy[int(453):int(485),int(1):int(500)]
            #cv2.imwrite(self.base_dir+'img/tick'+'-'+str(cap.get(cv2.CAP_PROP_POS_MSEC))+'.jpg',cropped)
          prev = cap.get(cv2.CAP_PROP_POS_MSEC)
          
          if len(array)>1:
              # Scene text OCR
              for i in array.values():
                boxes = i
                crop_sc = frame[int(boxes[2]):int(boxes[3]),int(boxes[0]-4):int(boxes[1])+4]
                cv2.imwrite(ocr1.base_dir+'img.jpg',crop_sc)
                # Scene text OCR
                ocr1.scene(ocr1.base_dir+'img.jpg',prev,no,boxes)
                array ={}
                #Extras
                #cv2.imwrite(ocr1.base_dir+'scene/'+str(prev)+'.'+str(ocr1.hashfn(boxes[2]))+'.'+str(ocr1.hashfn(boxes[0]))+'.jpg',crop_sc)
        else:
          if cropped.size:
            cv2.imwrite(ocr1.base_dir+'backup.jpg',cropped)
            #Extras
            #cv2.imwrite(self.base_dir+'backup/tick-'+str(prev)+'.jpg',cropped)
          # Ticker OCR
          if os.path.isfile(ocr1.base_dir+'tickimg.jpg'):
            ocr_ticker(ocr1.op,ticker,no,prev,ocr1.base,ocr1.lang)      

        # Display green boxes
        '''for j in range(4):
         p1 = (vertices[j][0], vertices[j][1])
          p2 = (vertices[(j + 1) % 4][0], vertices[(j + 1) % 4][1])
          if arg <2:
            cv2.line(copy, p1, p2, (0, 255, 0), 2);'''
        # Video display
        #cv2.imshow(ocr1.kWinName,copy)
    write_scenetext(ocr1)
    ocr1.op.write(ocr1.endtag)
    ocr1.op.close()
    print("done")
    print("Writing")
    print(no)

ocr1 = benhinocr()
print(ocr1.video_dir+ocr1.video)
if sys.argv[3] == 'ben':
  detect_text(ocr1.base_dir+'temp.mp4',ocr1)
else:
  detect_text(ocr1.video_dir+ocr1.video,ocr1)

