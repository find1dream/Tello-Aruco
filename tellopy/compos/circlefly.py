#to make the drone fly according to the circle path

#!!!!!!! figure out how the drone keep video clear
#from autopiolot import *
import math
import numpy as np


class circlefly():
    def __init__(self,r,num):
        self.targetList = np.array(self.pointsInCircum(r,num))


    def circleTargetPosCalcu(self, fNum):
        if fNum >= len(self.targetList):
            return self.targetList[0]
        else:
            return self.targetList[fNum]

    def checkIfTargetComplete(self,posNow, targetPos, fnumNow):
        print(posNow, targetPos)
        if math.sqrt((posNow[0]-targetPos[0])**2 + (posNow[1]-targetPos[1])**2 ) < 7:
            print(math.sqrt((posNow[0]-targetPos[0])**2 + (posNow[1]-targetPos[1])**2 ) )
            fnumNow = fnumNow + 1 if fnumNow < len(self.targetList) else 0
        if fnumNow >= len(self.targetList):
            fnumNow = 0
        return fnumNow
    
    # input: position now
    def fly(self, finishedNum, posNow):
            targetPos = self.circleTargetPosCalcu(finishedNum)
            fnumnow = self.checkIfTargetComplete(posNow, targetPos, finishedNum)
            targetPos = self.circleTargetPosCalcu(fnumnow)
            # write pid controll here
            ##
            ##
            return fnumnow, targetPos
    
    def pointsInCircum(self, r=40,n = 100):
            return [[80 + math.cos(2*math.pi/n*x)*r,80 + math.sin(2*math.pi/n*x)*r,100] for x in range(0,n+1)]

if __name__ == "__main__":
    posNow = np.array([14,15,20])
    finishedNum = 16
    fly = circlefly(40,16)
    finishedNum, targetPos = fly.fly( finishedNum, posNow)
    print("finishedNum: ", finishedNum)
    print("targetPos:", targetPos )
                            

