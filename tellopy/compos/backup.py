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
import socket


aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters =  aruco.DetectorParameters_create()
parameters.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR

drone = tellopy.Tello()
board = aruco.GridBoard_create(5, 7, 0.033, 0.0035, dictionary) 
arucoMarkerLength = 0.033
PI = 3.1415

frameA = None
run_recv_thread = True


udp_ip = "127.0.0.1"
udp_port = 5555

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#serverSock.bind((udp_ip, udp_port))

posQueue = deque([[0.0,0.0,0.0]])
#pos = np.random.randint(-10,10,size=(1,10,3))

def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

def init_logger():
    handler = StreamHandler()
    handler.setLevel(INFO)
    handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(INFO)




class DroneReg():
    def __init__(self):
        self.worldPos = None
        self.cameraMatrix = np.load('./camPara/mtx.npy')
        self.distanceCoefficients = np.load('./camPara/dist.npy')

    def findARMarker(self,frame):
        self.frame =  frame
        #Height, Width = frame.shape[:2]
        if len(self.frame.shape) == 3:
            self.Height, self.Width, self.channels = self.frame.shape[:3]
        else:
            self.Height, self.Width = self.frame.shape[:2]
        self.channels = 1
        self.halfHeight = self.Height / 2
        self.halfWidth = self.Width /2
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(self.frame, dictionary)
        #corners[id0,1,2...][][corner0,1,2,3][x,y]
        aruco.drawDetectedMarkers(self.frame, self.corners, self.ids, (0,255,0))

    def show(self):
        cv2.imshow("result", self.frame)

    def getARPoint(self):
        num = self.getExistMarker()
        if num > 0:
            square_points = np.reshape(np.array(self.corners), (4*num, -1))
            G = np.mean(square_points, axis = 0)
            cv2.circle(self.frame, (int(G[0]), int(G[1])), 10, (255, 255, 255), 5)
            x = self.halfHeight - G[0]
            y = G[1] - self.halfWidth
            return x, y

    #AR2つのそれぞれの座標が欲しい場合
    def getARPoint2(self):
        if len(self.corners) >= 2:
            square_points = np.reshape(np.array(self.corners), (4, -1))
            G = np.mean(square_points, axis = 0)
            cv2.circle(self.frame, (int(G[0]), int(G[1])), 10, (255, 255, 255), 5)
            x0 = self.halfHeight - G[0]
            y0 = G[1] - self.halfWidth
            x1 = self.halfHeight - G[2]
            y1 = G[3] - self.halfWidth
            return (x0, y0, x1, y1)

    def getDistance(self):
        if len(self.corners) > 0:
            self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(self.corners, arucoMarkerLength, self.cameraMatrix, self.distanceCoefficients)
            G = np.mean(self.tvec, axis = 0)
            return G[0][2]

            #ARそれぞれの距離が欲しかったらこっち
            #return self.tvec[0][0][2], self.tvec[1][0][2]
    def estimatePos(self):
        if len(self.corners) > 0:
            self.retval, self.rvec, self.tvec = aruco.estimatePoseBoard(self.corners, self.ids, board, self.cameraMatrix, self.distanceCoefficients)
            #self.revc_vec ,_ = cv2.Rodrigues(self.rvec)
            #self.revc_inv 
            self.dst, jacobian = cv2.Rodrigues(self.rvec)
            self.revc_trs = cv2.transpose(self.dst)
            self.worldPos = - self.revc_trs * self.tvec
            self.worldPos = [self.worldPos[0][0],self.worldPos[1][1],  self.worldPos[2][2]]
 #           print("X: ",self.worldPos[0],"Y: ", self.worldPos[1], "Z: ", self.worldPos[2])
            #self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(self.corners[0], arucoMarkerLength, self.cameraMatrix, self.distanceCoefficients)
            if self.retval != 0:
                self.frame = aruco.drawAxis(self.frame, self.cameraMatrix, self.distanceCoefficients, self.rvec, self.tvec, 0.1)

    def getAngle(self):
            (roll_angle, pitch_angle, yaw_angle) =  self.rvec[0][0][0]*180/PI, self.rvec[0][0][1]*180/PI, self.rvec[0][0][2]*180/PI
            if pitch_angle < 0:
                roll_angle, pitch_angle, yaw_angle = -roll_angle, -pitch_angle, -yaw_angle
            return (roll_angle, pitch_angle, yaw_angle)

    def getExistMarker(self):
        return len(self.corners)


DroneVideo = DroneReg()
def recv_thread():
    global frameA
    global run_recv_thread
    global drone
    print('start recv_thread()')
    drone.connect()
    drone.wait_for_connection(60.0)
    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.set_video_encoder_rate(4)
    drone.set_loglevel(drone.LOG_WARN)
    container = av.open(drone.get_video_stream())
    run_recv_thread = True
    while run_recv_thread:
        print("debug: ready to receive video frames...")
        for f in container.decode(video=0):
            frameA = f
           # frames = container.decode(video=0)
           # #print(next(frames))
           # frameA = next(frames)
           # if DroneVideo.worldPos is not None:
           #     messageToUdp = DroneVideo.worldPos
           #     messageToUdp = " ".join(str(x) for x in messageToUdp)
           #     clientSock.sendto(messageToUdp.encode(), (udp_ip, udp_port))
            time.sleep(0.001)

def showCamPos_thread():
    global ax
    global posQueue
    global DroneVideo
    
  #  plt.ion()
  #  fig = plt.figure()
  #  ax = fig.add_subplot(111, projection = '3d')
  #  posQueue = deque([[0.0,0.0,0.0]])
  #  while True:
  #      y = 0
  #      print("why............")
  #      if DroneVideo.worldPos is not None:
  #          posQueue.append(DroneVideo.worldPos)
  #          print(posQueue)
  #          if len(posQueue) > 10:
  #              posQueue.popleft()
  #              ax.plot([posQueue[i][0] for i in range(0,10)],\
  #                      [posQueue[i][1] for i in range(0,10)],\
  #                      [posQueue[i][2] for i in range(0,10)])
  #              plt.draw()  1
  #              plt.pause(0.1)
  #              ax.cla()


def main():
    try:
        
        frameCount = 0
        threading.Thread(target = recv_thread).start()
        #threading.Thread(target = showCamPos_thread).start()
        while run_recv_thread:
            if frameA is None :
                time.sleep(0.01)
            else:
                #---------show frame start-------------------------------#
                frameCount += 1
                frame = frameA
                im = np.array(frame.to_image())
                image = cv2.flip(im, 0)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                #image = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
                
                #cv2.imshow('Original', image)
                DroneVideo.findARMarker(image)
                DroneVideo.estimatePos()
                #$print(DroneVideo.getARPoint2())
                DroneVideo.show()
                if cv2.waitKey(10) & 0xFF == ord('t'):
                    cv2.imwrite (str(frameCount) + ".png", image)
                #---------show frame end---------------------------------#
                #print("debug: got frame")

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        #drone.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
