# -*- coding: utf-8 -*-
import cv2
import sys
import numpy as np
from math import *

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters =  aruco.DetectorParameters_create()
parameters.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR

board = aruco.GridBoard_create(5, 7, 0.033, 0.003, dictionary) 
arucoMarkerLength = 0.033
PI = 3.1415

class AR():
    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        self.cameraMatrix = np.load('mtx.npy')
        self.distanceCoefficients = np.load('dist.npy')

    def findARMarker(self):
        self.ret, self.frame = self.cap.read()
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
            #print(self.rvec)
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

    def release(self):
        self.cap.release()
        
if __name__ == '__main__':

    myCap = AR()
    while True:
        myCap.findARMarker()
        myCap.estimatePos()
        #$print(myCap.getARPoint2())
        myCap.show()
        if cv2.waitKey(1) > 0:
            myCap.release()
            cv2.destroyAllWindows()
            break
