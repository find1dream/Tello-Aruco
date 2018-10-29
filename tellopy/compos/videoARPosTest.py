# -*- coding: utf-8 -*-
import cv2
import math
import sys
import numpy as np
from math import *
import traceback
import av
import time


aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
parameters =  aruco.DetectorParameters_create()
parameters.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR

#board = aruco.GridBoard_create(5, 7, 0.033, 0.0035, dictionary) 
board = aruco.GridBoard_create(8, 8 ,0.1515, 0.0585, dictionary) 
arucoMarkerLength = 0.1515
PI = 3.141592653











class DroneReg():
    def __init__(self):
        self.worldPos = None
        self.cameraMatrix = np.load('./camPara/mtx.npy')
        self.distanceCoefficients = np.load('./camPara/dist.npy')
        self.cap = cv2.VideoCapture(0)
        
    def findARMarker(self):
        self.ret, self.frame =  self.cap.read()
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(self.frame, dictionary)
        aruco.drawDetectedMarkers(self.frame, self.corners, self.ids, (0,255,0))

    def show(self):
        cv2.imshow("result", self.frame)

    def getDistance(self):
            pass
            #return self.tvec[0][0][2], self.tvec[1][0][2]
    def estimatePos(self):
        if len(self.corners) > 0:
            self.retval, self.rvec, self.tvec =  aruco.estimatePoseBoard(self.corners, self.ids, board, self.cameraMatrix, self.distanceCoefficients)
            self.dst, jacobian = cv2.Rodrigues(self.rvec)
            self.extristics = np.matrix([[self.dst[0][0],self.dst[0][1],self.dst[0][2],self.tvec[0][0]],
                                        [self.dst[1][0],self.dst[1][1],self.dst[1][2],self.tvec[1][0]],
                                        [self.dst[2][0],self.dst[2][1],self.dst[2][2],self.tvec[2][0]],
                                        [0.0, 0.0, 0.0, 1.0]
                    ])
            #print(self.dst,self.tvec)
            #print("self.extr:", self.extristics)
            #print("self.extr.I:",self.extristics.I )
            #self.worldRot = cv2.Rodrigues(self.rvec_trs)
            self.extristics_I = self.extristics.I
            self.worldPos = np.array([round(self.extristics_I[0,3]*100,3),\
                    round(self.extristics_I[1,3]*100,3),\
                    round(self.extristics_I[2,3]*100,3)])
            self.worldRotM = np.zeros(shape=(3,3))
            cv2.Rodrigues(self.rvec, self.worldRotM,  jacobian = 0 )
            self.worldRot = cv2.RQDecomp3x3(self.worldRotM)

            #self.worldPos = - self.tvec * self.rvec_trs 
            #print( self.tvec, self.rvec)
            #self.worldPos = [self.worldPos[0][0],self.worldPos[1][1],  self.worldPos[2][2]]
            print("X:%.0f " % (self.worldPos[0]),\
                    "Y:%.0f "% (self.worldPos[1]),\
                    "Z:%.0f "% (self.worldPos[2]),\
                    "rot:%.0f "% (self.worldRot[0][2]+94))
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


def main():
    try:
            DroneVideo = DroneReg()
                #image = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
            while True:               
                #im = np.array(frame.to_image())
                #image = cv2.flip(im, 0)
                #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                #cv2.imshow('Original', image)
                DroneVideo.findARMarker()
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
