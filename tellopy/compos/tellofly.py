# -*- coding: utf-8 -*-
import cv2
import math
import sys
import numpy as np

from math import *
import traceback
import tellopy
import av
import time
import threading
from multiprocessing  import Process
from collections import deque
from autopiolot import *
from datetime import datetime
from computerVision import *
from udp_server import *
from circlefly import *
from transformations import *
from face_tracking import *
import csv
import base64


def handler(event, sender, data, **args):
    pass
    #tellostate.drone = sender
    #if event is tellostate.drone.EVENT_FLIGHT_DATA:
    #   pass

       #print(data.north_speed, data.east_speed, data.ground_speed)

def init_logger():
    handler = StreamHandler()
    handler.setLevel(INFO)
    handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(INFO)

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = './model/frozen_inference_graph_face.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = './protos/face_label_map.pbtxt'

class telloState():
    def __init__(self):
        self.flyflag = False
        self.target = np.array([120, 120, 100])
        self.targe = np.array([120, 120, 100])
        self.framem = None
        self.frameA = None
        self.drone =  tellopy.Tello()
        self.ifshowvideo = False
        self.iffollow = False
        self.iffaceDetect = True
        self.Cap = cv2.VideoCapture(0)
        self.TimeStart = 0
        self.TimeEnd = 0
        self.speedNow = np.array([0.0,0.0,0.0])
        self.drone.connect()
        self.drone.wait_for_connection(60.0)
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, handler)
        #self.drone.set_video_encoder_rate(4)
        self.drone.set_loglevel(self.drone.LOG_WARN)
        self.path = deque()
        self.mission = deque()
        self.modeNow = 100
        self.ifmisson = False
        self.ifpath = False
        self.pathMissonMultiTouch = 0
        self.trackingPos = np.array([0.0,0.0,0.0])
        self.targetangle = 0.0
        self.udpread = getPosData()

        # need to calculate the the angle to point to
    def gettargetagle(self, posNow, posTarget):
        targetangle = 0.0
        try:
             directVec = posTarget - posNow
             if directVec[0] == 0.0:   # 90 degrees
                 targetangle = 90.0
             else:
                 targetangle = math.atan(directVec[1]/directVec[0])*180/math.pi
        except:
            print("please check the gettargetagle input")
        return targetangle
        
class recv_thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run (self):
         print('start recv_thread()')
         container = av.open(tellostate.drone.get_video_stream())
         run_recv_thread = True

         while run_recv_thread:
             print("debug: ready to receive video frames...")
             for f in container.decode(video=0):
                 
                 #frames = container.decode(video=0)
                 tellostate.frameA =  f #next(frames)

                # time.sleep(0.001)

         
                 #if tellostate.droneVideo.worldPos is not None:
                 #    messageToUdp = tellostate.droneVideo.worldPos
                 #    messageToUdp = " ".join(str(x) for x in messageToUdp)
                 #    clientSock.sendto(messageToUdp.encode(), (udp_ip, udp_port))

class msg_thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         while True:
             #print("receive data")
             num, data = tellostate.udpread.getmsg()
             if num != 9:
                 print("num: ", num, "data: ", data)
                 #tellostate.missionOrPath = False
                 tellostate.modeNow = num
                 tellostate.pathMissonMultiTouch = 0
                 if num == 0:
                     tellostate.ifmisson = False
                     tellostate.ifpath = False
                     tellostate.flyflag = True
                 else:
                     tellostate.flyflag = False
                 if num == 2:
                     tellostate.ifpath = True
                     tellostate.ifmission = False
                     tellostate.path.append(data)
                 elif num == 3:
                     tellostate.ifpath = False
                     tellostate.ifmission = True
                     tellostate.mission.append(data)
                 elif num == 5:
                     tellostate.targetangle = data[0]   # angle to point
                     print("targetangnle: ",tellostate.targetangle)
                 elif num == 6:
                     tellostate.trackingPos = data
                     print("tracking pos: ",tellostate.trackingPos)
                     try:
                        tellostate.targetangle = tellostate.gettargetagle(DroneVideo.worldRot,tellostate.trackingPos)
                     except:
                         print("make sure the drone can see the markers")
                 elif num == 7:
                     tellostate.drone.takeoff()
                 elif num == 8:
                     tellostate.drone.land()
                 tellostate.target = data
                 print("tellostate.target: ",tellostate.target)
             else:
                 tellostate.pathMissonMultiTouch += 1
                 print("ready to fly!..................")
                 #tellostate.missonOrPath = True
                 timerThread = None
                 if tellostate.pathMissonMultiTouch <=1:
                     if tellostate.ifpath == True:
                        #print("path deque: ", tellostate.path)
                        timerThread = timer_thread(tellostate.path)
                     else:
                        #print("mission deque: ",tellostate.mission)
                        timerThread = timer_thread(tellostate.mission)
                     timerThread.start()

                 #tellostate.msnOrPath = True
                 #pass
                 tellostate.flyflag = True

class timer_thread(threading.Thread):
    def __init__(self,pos_deque):
        threading.Thread.__init__(self)
        self.pos_deque = pos_deque
        #self.cact = cact    # cactergory
    def run(self):
       try:
         wantTofly = None
         if tellostate.ifmission == True:
             wantTofly = missionfly(self.pos_deque)
         elif tellostate.ifpath == True:
             wantTofly = pathfly(self.pos_deque)
         #print(wantTofly.targetList)
         next_call = time.time()
         while not wantTofly.ifend():
             try: 
                tellostate.targe = wantTofly.fly(DroneVideo.worldPos)
                print("timer_thread- targe: ",tellostate.targe)
                #next_call = next_call + 0.01;
                #leng = next_call - time.time()
                #print("length: ", leng)
                time.sleep(0.15)
             except:
                #print("")
                print(DroneVideo.worldPos,"please check if the drone can see the aruco board")
                break
         print("timer_thread completed!!!")

         if tellostate.ifmission == True:
             tellostate.mission.clear()
         elif tellostate.ifpath == True:
             tellostate.path.clear()
       except:
             print("wantTofly is None")
        # cirfly = circlefly(60,400)
        # fnum = 0
        # t = 0
        # tx = 0.27
        # ty = 0.20
        # tz = 0.15
        # next_call = time.time()
        # while True:
        #     t += 0.015
        #     A = 1.5   #*(abs(math.sin(0.005*t)))
        #     x = A*abs(math.sin(tx*t))+0.1
        #     y = A*abs(math.sin(ty*t))+0.1
        #     z = A*abs(math.sin(tz*t))+0.1
        #     tellostate.targe = np.array([x,y,z])*100
        #     #fnum, targe = cirfly.fly(fnum)
        #     #print("targe: ", targe)
        #     next_call = next_call + 0.01;
        #     #leng = next_call - time.time()
        #     #print("length: ", leng)
        #     time.sleep(0.015)

class facetracking_thread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         tDetector = TensoflowFaceDector(PATH_TO_CKPT)
         next_call = time.time()
         while True:
             if tellostate.frameA is not None:
                 
                 frame = np.array(tellostate.frameA.to_image())
                 frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                 (boxs, boxes, scores, classes, num_detections) = tDetector.run(frame)
                 vis_util.visualize_boxes_and_labels_on_image_array(
                     frame,
                     np.squeeze(boxes),
                     np.squeeze(classes).astype(np.int32),
                     np.squeeze(scores),
                     category_index,
                     use_normalized_coordinates=True,
                     min_score_thresh=0.3,
                     line_thickness=4)

                # control tello's direction
                 if boxs is not None:
                    xmin, xmax = boxs[0][1],boxs[0][3]
                    center = (xmin + xmax )/2
                    out = autofly.turnToangle(center)
                    if tellostate.iffollow is True:
                        tellostate.drone.counter_clockwise(out)
                    #print("boxs: ",boxs)

                 tellostate.framem = frame
                 #print("realdy to show")
                 #print(boxes, scores, classes, num_detections)
                 #cv2.imshow("tensorflow based " , frame)
                 #cv2.waitKey(1)

             next_call = next_call + 0.030;
             leng = next_call - time.time()
             if leng < 0:
                 leng = 0.01
             #print("length: ", leng)
             time.sleep(leng)

class postracking_thread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         next_call = time.time()
         tDetector = TensoflowFaceDector(PATH_TO_CKPT)
         while True:
             if tellostate.frameA is not None or tellostate.framem is not None:
                 
                 #print("realdy to show")
                 #print(boxes, scores, classes, num_detections)
                 #cv2.imshow("tensorflow based " , frame)
                 #cv2.waitKey(1)

                # control tello's direction
                 try:
                     pass
                    #out = autofly.turnToangle_abs(DroneVideo.worldRot[0][2]+94,tellostate.targetangle)
                    #tellostate.drone.counter_clockwise(out)
                    #print("boxs: ",boxs)
                 except:
                    print("please check if the drone can see the markers")
                 try:
                     frame = None
                     if tellostate.iffaceDetect == True and tellostate.framem is not None:
                        #print("framem:",tellostate.framem)
                        #frame = np.array(tellostate.framem.to_image())
                        #print("aaa")
                        frame = cv2.resize(tellostate.framem,(160,120))
                     else:
                        frame = np.array(tellostate.frameA.to_image())
                        frame = cv2.resize(frame,(160,120))
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),100]
                     encoded, buf = cv2.imencode('.jpg', frame)
                     jpg_as_text = base64.b64encode(buf)
                     try:
                         #print("send video to udp")
                         datalen = 8000
                         IP = '192.168.100.152'
                         Port = 5555
                         if len(jpg_as_text) > datalen:
                             trunck1 = jpg_as_text[:datalen]
                             trunck2 = jpg_as_text[datalen:]
                             temp1 = list(trunck1)
                             temp2 = list(trunck2)
                             temp1[0] = 97
                             temp1 = bytearray(temp1)
                             temp2 = bytearray(temp2)
                             tellostate.udpread.socket.sendto(temp1,(IP, Port))
                             tellostate.udpread.socket.sendto(temp2,(IP, Port))
                         else:
                             tellostate.udpread.socket.sendto(jpg_as_text,(IP, Port))
                     except:
                         print("jpg_as_text may be too long: ", len(jpg_as_text))

                     #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                 except:
                     print("please checke if the camera of drone got right data")

             next_call = next_call + 0.030;
             leng = next_call - time.time()
             if leng < 0:
                 leng = 0.01
             #print("length: ", leng)
             time.sleep(leng)


if __name__ == '__main__':
    try:
        tellostate = telloState()
        DroneVideo = DroneReg()
        autofly = autopiolot()
        mesgThread = msg_thread("message ")
        postracking = postracking_thread("postracking")
        postracking.start()
        mesgThread.start()
        rcvThread = recv_thread("video thread")
        rcvThread.start()
        if tellostate.iffaceDetect == True:
            face_thread =  facetracking_thread("face tracking thread")
            face_thread.start()
        #threading.Thread(target = msg_thread).start()
        #threading.Thread(target = timer_thread).start()
        chess = cv2.imread("./marker/Calibration_letter_chessboard_7x5.png")
        cv2.imshow("result", chess)
        with open('result.csv','w') as csvfile:
             writer = csv.writer(csvfile)
             writer.writerow(['posx','posy','posz','velx','vely','velz','angx'\
                              ,'angy','angz','gyrx','gyry','gryz','accx','accy','accz',\
                             'tposx','tposy','tposz','tvelx','tvely','tvelz','tangx'\
                              ,'tangy','tangz','tgyrx','tgyry','tgryz','taccx','taccy','taccz' ])
             frame = tellostate.frameA
             frameold = None
             print("received data from camera!!!")
             while True:
                _, frame_pos = tellostate.Cap.read()
                
                if frame_pos is frameold:
                    pass
                else:
                   frameold = frame_pos
                   #print(tellostate.framem,"is to show....................k")
                   if tellostate.framem is None:
                       pass
                   else:
                     # pass
                     if tellostate.ifshowvideo is True:
                         pass
                       # frame_face = tellostate.framem #np.array(tellostate.frameA.to_image())
                       # cv2.imshow("tensorflow based " , frame_face)
                        #cv2.waitKey(1)
                     #print("tensorflow")
                   DroneVideo.findARMarker(frameold)
                   DroneVideo.estimatePos()
                   #if tellostate.ifshowvideo is True:
                   #DroneVideo.show()

                    # touch button to fly
                   if tellostate.flyflag == True:

                       tellostate.TimeEnd = datetime.now()
                       if tellostate.TimeStart != 0:
                           tellostate.speedNow = autofly.getspeed(DroneVideo.worldPos, (tellostate.TimeEnd - tellostate.TimeStart).total_seconds())
                       tellostate.TimeStart = datetime.now()
                       #targe = np.array([100,100,100])
                       dspeed = np.array([round(-tellostate.drone.acce[1]*100,2)+1,round(-tellostate.drone.acce[0]*100,2)+1,round(-tellostate.drone.acce[2]*100,2)+1])
                       targPos = tellostate.targe
                       if tellostate.modeNow == 0 or tellostate.modeNow == 1:
                            targPos = tellostate.target
                       elif tellostate.modeNow == 2 or tellostate.modeNow == 3:
                            targPos = tellostate.targe
                       AdjustX, AdjustY, AdjustZ, refspd = \
                       autofly.sameAngleAutoflytoXYZ(DroneVideo.worldPos,tellostate.speedNow,dspeed,\
                                                    DroneVideo.worldRot[0][2]+94,targPos)
                       #print("targe now: ", targPos,"pos now: ", DroneVideo.worldPos)
                       #print("adjustZ: ", AdjustZ)
                       tellostate.drone.flytoXYZ(AdjustX, AdjustY, AdjustZ)
                      # q = tellostate.drone.quater
                      # euler = euler_from_quaternion(q) 
                      # euler = np.array([math.sin(euler[2]),math.sin(euler[1]),math.sin(euler[0])])
                       #print('Targe:  %f ' % (count, time.time()-start_time), end="")
                        #print('Read a new frame %-4d, time used: %8.2fs \r' % (count, time.time()-start_time), end="")
                       print("targe: %0.2f,%0.2f,%0.2f "% \
                             (tellostate.targe[0],tellostate.targe[1],tellostate.targe[2]))
                       print("posnow: %0.2f,%0.2f,%0.2f "% \
                             (DroneVideo.worldPos[0],DroneVideo.worldPos[1],DroneVideo.worldPos[2]))
                       #print("euler: ",euler)
                      # writer.writerow([DroneVideo.worldPos[0],DroneVideo.worldPos[1],DroneVideo.worldPos[2],tellostate.speedNow[0],tellostate.speedNow[1],tellostate.speedNow[2],\
                      #                  euler[0],euler[1],euler[2],round(tellostate.drone.gyro[0]*100,2),round(tellostate.drone.gyro[1]*100,2),round(tellostate.drone.gyro[2]*100,2),\

                      #                  round(-tellostate.drone.acce[1]*100,2),round(-tellostate.drone.acce[0]*100,2),round(-tellostate.drone.acce[2]*100,2),\
                      #                  tellostate.targe[0],tellostate.targe[1],tellostate.targe[2],refspd[0],refspd[1],refspd[2],0.0,0.0,euler[2],\
                      #                  0.0,0.0,0.0,0.0,0.0,round(-tellostate.drone.acce[2]*100,2)])
                   key = cv2.waitKey(1)
                   if key & 0xFF == ord ('j'):
                       tellostate.drone.down(40)
                   elif key & 0xFF == ord ('q'):
                       tellostate.drone.up(40)
                   elif key & 0xFF == ord ('k'):
                       tellostate.drone.down(0)
                   elif key & 0xFF == ord ('a'):
                       tellostate.flyflag = True
                   elif key & 0xFF == ord (';'):
                       tellostate.flyflag = False
                   elif key & 0xFF == ord ('o'):
                       tellostate.drone.clockwise(40)
                   elif key & 0xFF == ord ('s'):
                       tellostate.drone.counter_clockwise(0)
                       tellostate.drone.forward(0)
                       tellostate.drone.right(0)
                   elif key & 0xFF == ord ('b'):
                       tellostate.targe= np.array([100,100,120])
                       
                   elif key & 0xFF == ord ('m'):
                       tellostate.targe= np.array([20,50,40])
                   
                   elif key & 0xFF == ord ('h'):
                       tellostate.drone.takeoff()
                   elif key & 0xFF == ord ('d'):
                       tellostate.drone.land()
                       tellostate.flyflag = False
                   elif key & 0xFF == ord ('1'):
                       tellostate.iffollow = True

                   elif key & 0xFF == ord ('2'):
                       tellostate.iffollow = False
                   #elif key & 0xFF == ord('t'):
                   #    cv2.imwrite (str(frameCount) + ".png", image)
                   #test fly

                  # print("limit:%d " % (autofly.SpdLimit),\
                  #      "spd_P:%.1f "% (autofly.DroneSpeed_P),\
                  #      "spd_D:%.1f "% (autofly.DroneSpeed_D),\
                  #      "pos_P:%.1f "% (autofly.Dronefly_P),\
                  #      "pos_I:%.1f "% (autofly.Dronefly_I),\
                  #      "pos_D:%.1f "% (autofly.Dronefly_D))
                   #print("limit: ",autofly.SpdLimit,"speed_P",\
                   #      autofly.tellostate.droneSpeed_P,'speed_D', autofly.tellostate.droneSpeed_D ,"P",autofly.tellostate.dronefly_P\
                   #        ,"D", autofly.tellostate.dronefly_D)
                  # if cv2.waitKey(5) & 0xFF == ord ('q'):
                   #---------show frame end---------------------------------#
                   #tellostate.TimeEnd = datetime.now()
                   #alltime  = tellostate.TimeEnd - tellostate.TimeStart
                   #print("all time: ",int(alltime.total_seconds()*1000),"ms", " aaaall time: ",int(aalltime.total_seconds()*1000),"ms")

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        #tellostate.drone.quit()
        cv2.destroyAllWindows()
