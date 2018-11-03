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

class recv_thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run (self):
         print('start recv_thread()')
         tellostate.drone.connect()
         tellostate.drone.wait_for_connection(60.0)
         tellostate.drone.subscribe(tellostate.drone.EVENT_FLIGHT_DATA, handler)
         tellostate.drone.set_video_encoder_rate(4)
         tellostate.drone.set_loglevel(tellostate.drone.LOG_WARN)
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

def msg_thread():
    udpread = getPosData()
    while True:
        #print("receive data")
        num, data = udpread.getmsg()
        if num != 9:
            tellostate.target = data
            print("tellostate.target: ",tellostate.target)
        else:
            tellostate.flyflag = True

def timer_thread():
    cirfly = circlefly(60,400)
    fnum = 0
    t = 0
    tx = 0.27
    ty = 0.20
    tz = 0.15
    next_call = time.time()
    while True:
        t += 0.015
        A = 1.5   #*(abs(math.sin(0.005*t)))
        x = A*abs(math.sin(tx*t))+0.1
        y = A*abs(math.sin(ty*t))+0.1
        z = A*abs(math.sin(tz*t))+0.1
        tellostate.targe = np.array([x,y,z])*100
        #fnum, targe = cirfly.fly(fnum)
        #print("targe: ", targe)
        next_call = next_call + 0.01;
        #leng = next_call - time.time()
        #print("length: ", leng)
        time.sleep(0.015)

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




if __name__ == '__main__':
    try:
        tellostate = telloState()
       # flightData = tellopy.FlightData()
        DroneVideo = DroneReg()
        autofly = autopiolot()
        rcvThread = recv_thread("video thread")
        face_thread =  facetracking_thread("face tracking thread")
        rcvThread.start()
        face_thread.start()
        #threading.Thread(target = msg_thread).start()
        #threading.Thread(target = timer_thread).start()
        aa = cv2.imread("./marker/Calibration_letter_chessboard_7x5.png")
        cv2.imshow("result", aa)
        TimeStart = 0
        TimeEnd = 0
        frameCount = 0
        speedNow = np.array([0.0,0.0,0.0])
        frame = tellostate.frameA
        frameold = None
        Cap = cv2.VideoCapture(0)
        #tDetector = TensoflowFaceDector(PATH_TO_CKPT)
       # tellostate.drone.connect()
       # tellostate.drone.wait_for_connection(60.0)
       # tellostate.drone.subscribe(tellostate.drone.EVENT_FLIGHT_DATA, handler)
        #tellostate.drone.set_video_encoder_rate(4)
       # tellostate.drone.set_loglevel(tellostate.drone.LOG_WARN)
        with open('result.csv','w') as csvfile:
             writer = csv.writer(csvfile)
             writer.writerow(['posx','posy','posz','velx','vely','velz','angx'\
                              ,'angy','angz','gyrx','gyry','gryz','accx','accy','accz',\
                             'tposx','tposy','tposz','tvelx','tvely','tvelz','tangx'\
                              ,'tangy','tangz','tgyrx','tgyry','tgryz','taccx','taccy','taccz' ])
             while True:
                _, frame_pos = Cap.read()
                
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
                        frame_face = tellostate.framem #np.array(tellostate.frameA.to_image())
                        cv2.imshow("tensorflow based " , frame_face)
                        #cv2.waitKey(1)
                     #print("tensorflow")
                   DroneVideo.findARMarker(frameold)
                   DroneVideo.estimatePos()
                   if tellostate.ifshowvideo is True:
                        DroneVideo.show()
                   if tellostate.flyflag == True:

                       TimeEnd = datetime.now()
                       if TimeStart != 0:
                           speedNow = autofly.getspeed(DroneVideo.worldPos, (TimeEnd - TimeStart).total_seconds())
                       TimeStart = datetime.now()
                       #targe = np.array([100,100,100])
                       dspeed = np.array([round(-tellostate.drone.acce[1]*100,2)+1,round(-tellostate.drone.acce[0]*100,2)+1,round(-tellostate.drone.acce[2]*100,2)+1])
                       AdjustX, AdjustY, refspd = \
                       autofly.sameAngleAutoflytoXY(DroneVideo.worldPos,speedNow,dspeed,\
                                                    DroneVideo.worldRot[0][2]+94,tellostate.targe)
                       tellostate.drone.flytoXYZ(AdjustX, AdjustY, 0)
                       q = tellostate.drone.quater
                       euler = euler_from_quaternion(q) 
                       euler = np.array([math.sin(euler[2]),math.sin(euler[1]),math.sin(euler[0])])
                       #print('Targe:  %f ' % (count, time.time()-start_time), end="")
                        #print('Read a new frame %-4d, time used: %8.2fs \r' % (count, time.time()-start_time), end="")
                       #print("targe: ", targe)
                       #print("euler: ",euler)
                      # writer.writerow([DroneVideo.worldPos[0],DroneVideo.worldPos[1],DroneVideo.worldPos[2],speedNow[0],speedNow[1],speedNow[2],\
                      #                  euler[0],euler[1],euler[2],round(tellostate.drone.gyro[0]*100,2),round(tellostate.drone.gyro[1]*100,2),round(tellostate.drone.gyro[2]*100,2),\

                      #                  round(-tellostate.drone.acce[1]*100,2),round(-tellostate.drone.acce[0]*100,2),round(-tellostate.drone.acce[2]*100,2),\
                      #                  tellostate.targe[0],tellostate.targe[1],tellostate.targe[2],refspd[0],refspd[1],refspd[2],0.0,0.0,euler[2],\
                      #                  0.0,0.0,0.0,0.0,0.0,round(-tellostate.drone.acce[2]*100,2)])
                       #print("adjust: ",AdjustX, AdjustY)
                       #if tellostate.targetAchived == True:
                       #    count += 1
                       #    if count % 2 == 1:
                       #        tellostate.target = [15, 15, 15]
                       #    else:
                       #        tellostate.target = [2,2,2]
                   key = cv2.waitKey(1)
                   if key & 0xFF == ord ('j'):
                       tellostate.drone.down(20)
                   if key & 0xFF == ord ('q'):
                       tellostate.drone.up(20)
                   elif key & 0xFF == ord ('k'):
                       tellostate.drone.down(0)
                   elif key & 0xFF == ord ('a'):
                       tellostate.flyflag = True
                   elif key & 0xFF == ord ('o'):
                       tellostate.drone.clockwise(40)
                   elif key & 0xFF == ord ('b'):
                       tellostate.targe= np.array([150,150,120])
                       
                   elif key & 0xFF == ord ('m'):
                       tellostate.targe= np.array([20,50,40])
                   
                  # elif key & 0xFF == ord ('p'):
                  #     autofly.tellostate.dronefly_P += 0.03
                  # elif key & 0xFF == ord ('y'):
                  #     autofly.tellostate.dronefly_P -= 0.03

                   elif key & 0xFF == ord ('l'):
                       autofly.tellostate.dronefly_I += 0.03
                   elif key & 0xFF == ord ('/'):
                       autofly.tellostate.dronefly_I -= 0.03

                   elif key & 0xFF == ord ('f'):
                       autofly.tellostate.dronefly_D += 0.2
                   elif key & 0xFF == ord ('g'):
                       autofly.tellostate.dronefly_D -= 0.2

                   elif key & 0xFF == ord ('c'):
                       autofly.tellostate.droneSpeed_P += 0.03
                   elif key & 0xFF == ord ('r'):
                       autofly.tellostate.droneSpeed_P -= 0.03

                   elif key & 0xFF == ord ('t'):
                       autofly.tellostate.droneSpeed_D += 0.1
                   elif key & 0xFF == ord ('n'):
                       autofly.tellostate.droneSpeed_D -= 0.1

                   elif key & 0xFF == ord ('e'):
                       autofly.SpdLimit += 2.0
                   elif key & 0xFF == ord ('u'):
                       autofly.SpdLimit -= 2.0

                   elif key & 0xFF == ord ('o'):
                       tellostate.drone.counter_clockwise(20)
                   elif key & 0xFF == ord ('s'):
                       tellostate.drone.counter_clockwise(0)
                       tellostate.drone.forward(0)
                       tellostate.drone.right(0)
                   elif key & 0xFF == ord ('h'):
                       tellostate.drone.takeoff()
                   elif key & 0xFF == ord ('d'):
                       tellostate.drone.land()
                       tellostate.flyflag = False
                   elif key & 0xFF == ord ('p'):
                       tellostate.iffollow = True

                   elif key & 0xFF == ord ('y'):
                       tellostate.iffollow = False
                   #elif key & 0xFF == ord('t'):
                   #    cv2.imwrite (str(frameCount) + ".png", image)
                   #test fly

                   #print("limit: ",autofly.SpdLimit,"speed_P",\
                   #      autofly.tellostate.droneSpeed_P,'speed_D', autofly.tellostate.droneSpeed_D ,"P",autofly.tellostate.dronefly_P\
                   #        ,"D", autofly.tellostate.dronefly_D)
                  # if cv2.waitKey(5) & 0xFF == ord ('q'):
                   #---------show frame end---------------------------------#
                   #print("debug: got frame")
                   #TimeEnd = datetime.now()
                   #alltime  = TimeEnd - TimeStart
                   #print("all time: ",int(alltime.total_seconds()*1000),"ms", " aaaall time: ",int(aalltime.total_seconds()*1000),"ms")

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        #tellostate.drone.quit()
        cv2.destroyAllWindows()
