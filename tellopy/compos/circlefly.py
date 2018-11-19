#to make the drone fly according to the circle path

#!!!!!!! figure out how the drone keep video clear
#from autopiolot import *
import math
import numpy as np


class  pathfly():
    def __init__(self,pos_deque):
        self.targetList =  pos_deque
        self.targetLen = len(self.targetList)
        #self.targetList = np.array(self.pointsInCircum(r,num))
        self.finishedNum = 0
        self.posNow = np.array([0.0,0.0,0.0])
        self.iffinished = False

    def TargetPosCalcu(self, fNum):
        if fNum >= self.targetLen:
            return self.targetList[self.targetLen-1]
        else:
            return self.targetList[fNum]

    def checkIfTargetComplete(self, fnumNow):
        #print(posNow, targetPos)
        if fnumNow == 0 or fnumNow == self.targetLen:
            if math.sqrt((self.posNow[0]-self.targetPos[0])**2 + (self.posNow[1]-self.targetPos[1])**2) < 10:
                if fnumNow == self.targetLen:
                    self.iffinished = True
                #print(math.sqrt((self.posNow[0]-self.targetPos[0])**2 + (self.posNow[1]-self.targetPos[1])**2 ) )
                fnumNow = fnumNow + 1
            
        else:
                fnumNow = fnumNow + 1

        if fnumNow > len(self.targetList):
            fnumNow = len(self.targetList)
        return fnumNow
    
    def fly(self, posNow):
        self.posNow = posNow
        self.targetPos = self.TargetPosCalcu(self.finishedNum)
        fnumnow = self.checkIfTargetComplete(self.finishedNum)
        self.targetPos = self.TargetPosCalcu(fnumnow)
        self.finishedNum = fnumnow
        return self.targetPos
    def ifend(self):
        if self.finishedNum == self.targetLen and self.iffinished == True:
            return True
        else:
            return False
        pass

class  missionfly():
    def __init__(self,pos_deque):
        self.targetList =  pos_deque
        self.targetLen = len(self.targetList)
        #self.targetList = np.array(self.pointsInCircum(r,num))
        self.finishedNum = 0
        self.posNow = np.array([0.0,0.0,0.0])
        self.iffinished = False

    def TargetPosCalcu(self, fNum):
        if fNum >= self.targetLen:
            return self.targetList[self.targetLen-1]
        else:
            return self.targetList[fNum]

    def checkIfTargetComplete(self, fnumNow):
        #print(posNow, targetPos)
        if math.sqrt((self.posNow[0]-self.targetPos[0])**2 + (self.posNow[1]-self.targetPos[1])**2) < 10:
                if fnumNow == self.targetLen:
                    self.iffinished = True
                #print(math.sqrt((self.posNow[0]-self.targetPos[0])**2 + (self.posNow[1]-self.targetPos[1])**2 ) )
                fnumNow = fnumNow + 1
            

        if fnumNow > len(self.targetList):
            fnumNow = len(self.targetList)
        return fnumNow
    
    def fly(self, posNow):
        self.posNow = posNow
        print("eeeeeeeeeeeee")
        self.targetPos = self.TargetPosCalcu(self.finishedNum)
        print("nnnnnnnnnnnnnn")
        fnumnow = self.checkIfTargetComplete(self.finishedNum)
        print("aaaaaaaaaaaaaa")
        self.targetPos = self.TargetPosCalcu(fnumnow)
        print("ooooooooooooooooo")
        self.finishedNum = fnumnow
        return self.targetPos

    def ifend(self):
        if self.finishedNum == self.targetLen and self.iffinished == True:
            return True
        else:
            return False
    # input: position now
   # def fly(self, finishedNum, posNow):
   #         targetPos = self.circleTargetPosCalcu(finishedNum)
   #         fnumnow = self.checkIfTargetComplete(posNow, targetPos, finishedNum)
   #         targetPos = self.circleTargetPosCalcu(fnumnow)
   #         # write pid controll here
   #         ##
   #         ##
   #         return fnumnow, targetPos
    



class circlefly():
    def __init__(self,r,num):
        #self.targetList =  np.array([[20,20,100],[10,21*7,100],[21*7,21*7,100],[21*7,10,100]])
        self.targetList = np.array(self.pointsInCircum(r,num))


    def circleTargetPosCalcu(self, fNum):
        if fNum >= len(self.targetList):
            return self.targetList[0]
        else:
            return self.targetList[fNum]

    def checkIfTargetComplete(self, fnumNow):
        #print(posNow, targetPos)
        #if math.sqrt((posNow[0]-targetPos[0])**2 + (posNow[1]-targetPos[1])**2) < 10:
            #print(math.sqrt((posNow[0]-targetPos[0])**2 + (posNow[1]-targetPos[1])**2 ) )
        fnumNow = fnumNow + 1 if fnumNow < len(self.targetList) else 0
        if fnumNow >= len(self.targetList):
            fnumNow = 0
        return fnumNow
    
    def fly(self, finishedNum):
            targetPos = self.circleTargetPosCalcu(finishedNum)
            fnumnow = self.checkIfTargetComplete(finishedNum)
            targetPos = self.circleTargetPosCalcu(fnumnow)
            # write pid controll here
            ##
            ##
            return fnumnow, targetPos
    # input: position now
   # def fly(self, finishedNum, posNow):
   #         targetPos = self.circleTargetPosCalcu(finishedNum)
   #         fnumnow = self.checkIfTargetComplete(posNow, targetPos, finishedNum)
   #         targetPos = self.circleTargetPosCalcu(fnumnow)
   #         # write pid controll here
   #         ##
   #         ##
   #         return fnumnow, targetPos
    
    def pointsInCircum(self, r=40,n = 100):
            return [[85 - math.cos(-(0.25*math.pi)+2*math.pi/n*x)*r,85 + math.sin(-(0.25*math.pi)+2*math.pi/n*x)*r,100] for x in range(0,n+1)]

if __name__ == "__main__":
    posNow = np.array([14,15,20])
    finishedNum = 16
    #fly = circlefly(40,16)
    #finishedNum, targetPos = fly.fly( finishedNum, posNow)
    #!print("finishedNum: ", finishedNum)
    #print("targetPos:", targetPos )
                            

