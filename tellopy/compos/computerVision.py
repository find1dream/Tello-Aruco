import cv2
import numpy as np
#import time
#from datetime import datetime

class DroneReg():
    def __init__(self):
        self.worldPos = None
        self.cameraMatrix = np.load('./camPara/mtx.npy')
        self.distanceCoefficients = np.load('./camPara/dist.npy')
        self.aruco = cv2.aruco
        self.dictionary = self.aruco.getPredefinedDictionary(self.aruco.DICT_6X6_1000)
        self.parameters =  self.aruco.DetectorParameters_create()
        self.parameters.cornerRefinementMethod = self.aruco.CORNER_REFINE_CONTOUR

        #self.board = self.aruco.GridBoard_create(5, 7, 0.033, 0.0035, self.dictionary) 
        self.board = self.aruco.GridBoard_create(8, 8,0.1515, 0.0585, self.dictionary) 

    def findARMarker(self,frame):
        self.frame =  frame
        self.corners, self.ids, self.rejectedImgPoints = self.aruco.detectMarkers(self.frame, self.dictionary)
        self.aruco.drawDetectedMarkers(self.frame, self.corners, self.ids, (0,255,0))

    def show(self):
        cv2.imshow("result", self.frame)

    def getDistance(self):
            pass
            #return self.tvec[0][0][2], self.tvec[1][0][2]
    def estimatePos(self):
        if len(self.corners) > 0:
            self.retval, self.rvec, self.tvec = self.aruco.estimatePoseBoard(self.corners, self.ids, self.board, self.cameraMatrix, self.distanceCoefficients)
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
            #self.worldRot[0][2] += 94

            #self.worldPos = - self.tvec * self.rvec_trs 
            #print( self.tvec, self.rvec)
            #self.worldPos = [self.worldPos[0][0],self.worldPos[1][1],  self.worldPos[2][2]]
           # print("X:%.0f " % (self.worldPos[0]),\
           #         "Y:%.0f "% (self.worldPos[1]),\
           #         "Z:%.0f "% (self.worldPos[2]),\
           #         "rot:%.0f "% (self.worldRot[0][2]))
            #self.rvec, self.tvec, _ = aruco.estimatePoseSingleMarkers(self.corners[0], arucoMarkerLength, self.cameraMatrix, self.distanceCoefficients)
            if self.retval != 0:
                self.frame = self.aruco.drawAxis(self.frame, self.cameraMatrix, self.distanceCoefficients, self.rvec, self.tvec, 0.1)
            

    def getAngle(self):
            pass
    def getExistMarker(self):
        return len(self.corners)
