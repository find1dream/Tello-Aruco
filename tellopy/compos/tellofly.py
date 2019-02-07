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
from utils import *
from datetime import datetime
import csv
import base64
import copy

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
PATH_TO_PTH = './model/best_head.pth'


class telloState():
    def __init__(self):
        self.flyflag = False
        self.target = np.array([120, 120, 100])
        self.targe = np.array([120, 120, 100])
        self.postemp = np.array([120,120,100])
        self.framem = None
        self.frameA = None
        self.drone =  tellopy.Tello()
        self.ifshowvideo = False
        self.iffollow = False
        self.ifheadDetect = True
        self.Cap = cv2.VideoCapture(0)
        self.TimeStart = 0
        self.TimeEnd = 0
        self.speedNow = np.array([0.0,0.0,0.0])
        self.Tspeed = np.array([0.0,0.0,0.0])
        self.Tacc = np.array([0.0,0.0,0.0])
        self.drone.connect()
        self.drone.wait_for_connection(60.0)
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, handler)
        self.isflying = False
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
        self.tempposRecord = False
        self.udpread = getPosData()
        self.CmdDict = {0:"fly", 1:"touchfly", 2:"path",3:"mission",
                         5:"arrowAngleTracking", 6:"posTracking",
                        7:"takeoff",8:"land",9:"wait",100:"other"}

        # need to calculate the the angle to point to
    def gettargetagle(self, posNow, posTarget):
        targetangle = 0.0
        try:
             directVec = posTarget - posNow
             length = math.sqrt(directVec[0]**2 + directVec[1]**2)
             if directVec[0] > 0:
                     targetangle =\
                     math.asin(directVec[1]/length)*180/math.pi  - 90.0
             else:
                     targetangle = 90.0-math.asin(directVec[1]/length)*180/math.pi 
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

class msg_thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         while True:
             num, data = tellostate.udpread.getmsg()
             #print("num: ", num, "data: ", data,"tellostate.flyflag: ",tellostate.flyflag)
             if tellostate.CmdDict[num] != "wait":
                 if tellostate.CmdDict[num] != "arrowAngleTracking" and tellostate.CmdDict[num]!= "posTracking":
                    tellostate.modeNow = num
                 tellostate.pathMissonMultiTouch = 0
                 if tellostate.CmdDict[num] == "fly" :
                     tellostate.ifmisson = False
                     tellostate.ifpath = False
                     tellostate.flyflag = True
                 else:
                     if tellostate.CmdDict[num] != "arrowAngleTracking" and tellostate.CmdDict[num] !="posTracking":
                        tellostate.flyflag = False
                 if tellostate.CmdDict[num] == "path":
                     tellostate.tempposRecord = True
                     tellostate.ifpath = True
                     tellostate.ifmission = False
                     tellostate.path.append(data)
                 elif tellostate.CmdDict[num ]== "mission":
                     tellostate.tempposRecord = True
                     tellostate.ifpath = False
                     tellostate.ifmission = True
                     tellostate.mission.append(data)
                 elif tellostate.CmdDict[num] == "arrowAngleTracking":
                     tellostate.targetangle = data[0]   # angle to point
                     #print("targetangnle: ",tellostate.targetangle)
                 elif tellostate.CmdDict[num] == "posTracking":
                     tellostate.trackingPos = data
                     #print("tracking pos: ",tellostate.trackingPos)
                     try:
                        tellostate.targetangle = \
                        tellostate.gettargetagle(DroneVideo.worldPos,tellostate.trackingPos)
                        #print("phone tracking- targetangle: ",
                        #      tellostate.targetangle)
                     except:
                         print("make sure the drone can see the markers")
                 elif tellostate.CmdDict[num] == "takeoff":
                     print("take off!!!!!!!!!!!!!!!!")
                     tellostate.drone.takeoff()
                     tellostate.isflying = True
                 elif tellostate.CmdDict[num] == "land":
                     print("landing!!!!!!!!!!!!!!!!")
                     tellostate.flyflag = False
                     tellostate.isflying = False
                     tellostate.drone.land()
                     
                 if tellostate.CmdDict[num] != "arrowAngleTracking" and tellostate.CmdDict[num] != "posTracking":
                    tellostate.target = data
                 #print("tellostate.target: ",tellostate.target)
             else:
                 tellostate.pathMissonMultiTouch += 1
                 print("ready to fly!..................")
                 timerThread = None
                 tellostate.tempposRecord = False
                 if tellostate.pathMissonMultiTouch <=1:
                     if tellostate.ifpath == True:
                        #print("path deque: ", tellostate.path)
                        if (len(tellostate.path)> 5):  # have many points, else don't move
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
        self.autof = autopiolot()
    def run(self):
       try:
         wantTofly = None
         if tellostate.ifmission == True:
             wantTofly = missionfly(self.pos_deque)
         elif tellostate.ifpath == True:
             wantTofly = pathfly(self.pos_deque)
         #print(wantTofly.targetList)
         next_call = time.time()
         TimeStart, TimeEnd = 0,0
         posindex = 0
         while not wantTofly.ifend():
             try: 
                tellostate.TimeEnd = datetime.now()
                if tellostate.TimeStart != 0:
                    tellostate.targe, posindex = wantTofly.fly(DroneVideo.worldPos)
                    #print("posindex:", posindex)
                    
                    if tellostate.ifpath == True and posindex < len(self.pos_deque) and posindex > 0:
                        ## calculate Tspeed and Tacc 
                        ## Tspeed = (pos2-pos1)/time
                        ## Tacc  = (speed2 - speed1)/time
                        alltime  = tellostate.TimeEnd - tellostate.TimeStart
                        #if alltime == 0.0:
                        #    continue

                        middlePos = (self.pos_deque[posindex] + self.pos_deque[posindex -1])/2.
                        
                        tellostate.Tspeed = (self.pos_deque[posindex] -
                                             self.pos_deque[posindex-1])/alltime.total_seconds()
                        for index, value in enumerate(tellostate.Tspeed):
                            if value > self.autof.MaxSpeed:
                                tellostate.Tspeed[index] = self.autof.MaxSpeed
                            if value < -self.autof.MaxSpeed:
                                tellostate.Tspeed[index] = - self.autof.MaxSpeed


                        Tspeed_temp1 = (middlePos - self.pos_deque[posindex-1])/alltime.total_seconds()
                        Tspeed_temp2 = (self.pos_deque[posindex] - middlePos)/alltime.total_seconds()
                        tellostate.Tacc = (Tspeed_temp2 - Tspeed_temp1)/alltime.total_seconds()
                        #print("alltime",alltime.total_seconds(),tellostate.Tspeed, tellostate.Tacc)
                    else:
                        tellostate.Tspeed = np.array([0.,0.,0.])
                        tellostate.Tacc   = np.array([0.,0.,0.])

                    
                tellostate.TimeStart = datetime.now()
                time.sleep(0.15)
             except:
                print("")
                print(DroneVideo.worldPos,"please check if the drone can see the aruco board")
                #break
         print("timer_thread completed!!!")

         if tellostate.ifmission == True:
             tellostate.mission.clear()
         elif tellostate.ifpath == True:
             tellostate.path.clear()
         tellostate.ifpath = False
         tellostate.ifmisson = False
       except:
             print("wantTofly is None")

class dataCollection_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        fnum = 0
        t = 0
        tx = 0.47
        ty = 0.30
        tz = 0.15
        next_call = time.time()
        while True:
            t += 0.015
            A = 1.5   #*(abs(math.sin(0.005*t)))
            x = A*abs(math.sin(tx*t))+0.1
            y = A*abs(math.sin(ty*t))+0.1
            z = (A-0.3)*abs(math.sin(tz*t))+0.1
            tellostate.targe = np.array([x,y,z])*100
            #fnum, targe = cirfly.fly(fnum)
            #print("targe: ", targe)
            next_call = next_call + 0.01;
            leng = next_call - time.time()
            print("length: ", leng)
            time.sleep(0.015)

class headtracking_thread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         head_detector = HeadDetector(PATH_TO_PTH)
         next_call = time.time()
         while True:
             if tellostate.frameA is not None:
                 
                 frame = np.array(tellostate.frameA.to_image())
                 frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # control tello's direction
                # if boxs is not None:
                #    xmin, xmax = boxs[0][1],boxs[0][3]
                #    center = (xmin + xmax )/2
                #    out = autofly.turnToangle(center)
                #    if tellostate.iffollow is True:
                #        tellostate.drone.counter_clockwise(out)
                #    #print("boxs: ",boxs)
                 tellostate.framem = head_detector.head_detect(frame)
                 #cv2.imshow("test",tellostate.framem)
                 #cv2.waitKey(1)

             next_call = next_call + 0.01;
             leng = next_call - time.time()
             if leng < 0:
                 leng = 0.01
             #print("length: ", leng)
             time.sleep(leng)

class sendvideo_thread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
         next_call = time.time()
         while True:
             if tellostate.frameA is not None or tellostate.framem is not None:
                 

                # control tello's direction
                 try:
                     frame = None
                     if tellostate.ifheadDetect == True and tellostate.framem is not None:
                        frame = cv2.resize(tellostate.framem,(180,135))
                     else:
                        frame = np.array(tellostate.frameA.to_image())
                        frame = cv2.resize(frame,(180,135))
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),100]
                     encoded, buf = cv2.imencode('.jpg', frame)
                     jpg_as_text = base64.b64encode(buf)
                     try:
                         #print("send video to udp")
                         IP = '192.168.100.156'
                         Port = 5555
                         trunck1 = jpg_as_text[:int(len(jpg_as_text)/2)]
                         trunck2 = jpg_as_text[int(len(jpg_as_text)/2):]
                         temp1 = list(trunck1)
                         temp2 = list(trunck2)
                         temp1[0] = 97
                         temp1 = bytearray(temp1)
                         temp2 = bytearray(temp2)
                         tellostate.udpread.socket.sendto(temp1,(IP, Port))
                         tellostate.udpread.socket.sendto(temp2,(IP, Port))
                         #print("send complete")
                     except:
                         print("jpg_as_text may be too long: ", len(jpg_as_text))

                     #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                 except:
                     print("please checke if the camera of drone got right data")

             next_call = next_call + 0.020;
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
         while True:
             if tellostate.frameA is not None or tellostate.framem is not None:

                 try:
                # if tellostate.isflying == True:
                    #print("tracking the angnle")
                    #print("angle now", DroneVideo.realAngle, "target angle: ", tellostate.targetangle)
                    out = autofly.turnToangle_abs(DroneVideo.realAngle,tellostate.targetangle)
                    tellostate.drone.counter_clockwise(out)
                 except:
                    print("angletracking: please check if the drone can see the markers")
             next_call = next_call + 0.020;
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
        sendvideo = sendvideo_thread("sendvideo")
        sendvideo.start()
        mesgThread.start()
        rcvThread = recv_thread("video thread")
        rcvThread.start()
        postracking = postracking_thread("postracking")
        postracking.start()


        #dataCollection = dataCollection_thread()
        #dataCollection.start()
        if tellostate.ifheadDetect == True:
            print("head tracking............")
            head_thread =  headtracking_thread("head tracking thread")
            head_thread.start()
        chess = cv2.imread("./marker/linux.jpg")
        cv2.imshow("result", chess)
        posEsti = PosEstimate("./model/bestmodel_bothxy.pth","./model/alldata.csv")
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
                       # frame_head = tellostate.framem #np.array(tellostate.frameA.to_image())
                       # cv2.imshow("tensorflow based " , frame_head)
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
                       targPos = copy.copy(tellostate.targe)
                    
                       if tellostate.CmdDict[tellostate.modeNow] == "fly" or tellostate.CmdDict[tellostate.modeNow] == "touchfly":
                            targPos = copy.copy(tellostate.target)
                            tellostate.postemp = tellostate.target
                       elif tellostate.CmdDict[tellostate.modeNow] == "mission" or tellostate.CmdDict[tellostate.modeNow] == "path":
                            if tellostate.tempposRecord == True:
                                tellostate.targe = tellostate.postemp
                            targPos = copy.copy(tellostate.targe)
                            #if tellostate.CmdDict[tellostate.modeNow] =="path":

                       drone_state =\
                                [targPos[0],targPos[1],targPos[2],tellostate.Tspeed[0],tellostate.Tspeed[1],tellostate.Tspeed[1],
                                                  0,0,0,0,0,0,
                                                  round(-tellostate.Tacc[0]*100,2),round(-tellostate.Tacc[1]*100,2),-99.74]
                       estX, estY = posEsti.estimate(drone_state)
                                #print("tellostate.Tspeed",tellostate.Tspeed,
                                #      "tellostate.Tacce", -tellostate.Tacc)
                                #print("estimate pos, x:",estX,"targetx",targPos[0],"y:",estY,"targety",targPos[1])
                       if abs(targPos[0] - estX) < 40 and abs(targPos[1] - estY) < 40:
                            targPos[0] = copy.copy(estX)
                            targPos[1] = copy.copy(estY)
                        
                       AdjustX, AdjustY, AdjustZ, refspd = \
                       autofly.sameAngleAutoflytoXYZ(DroneVideo.worldPos,tellostate.speedNow,dspeed,\
                                                    DroneVideo.realAngle,targPos)
                       #print("targe now: ", targPos)
                       tellostate.drone.flytoXYZ(AdjustX, AdjustY, AdjustZ)
                      # q = tellostate.drone.quater
                      # euler = euler_from_quaternion(q) 
                      # euler = np.array([math.sin(euler[2]),math.sin(euler[1]),math.sin(euler[0])])
                       #print('Targe:  %f ' % (count, time.time()-start_time), end="")
                        #print('Read a new frame %-4d, time used: %8.2fs \r' % (count, time.time()-start_time), end="")
                       #print("targe: %0.2f,%0.2f,%0.2f "% \
                       #      (targPos[0],targPos[1],targPos[2]),"modeNow:",
                       #      tellostate.CmdDict[tellostate.modeNow])
                       #print("posnow: %0.2f,%0.2f,%0.2f "% \
                       #      (DroneVideo.worldPos[0],DroneVideo.worldPos[1],DroneVideo.worldPos[2]))
                       #print("euler: ",euler)
                      # q = tellostate.drone.quater
                      # euler = euler_from_quaternion(q) 
                      # euler = np.array([math.sin(euler[2]),math.sin(euler[1]),math.sin(euler[0])])
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
                       tellostate.isflying = True
                   elif key & 0xFF == ord ('d'):
                       tellostate.drone.land()
                       tellostate.flyflag = False
                       tellostate.isflying = False
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
        tellostate.drone.land()
        cv2.destroyAllWindows()
