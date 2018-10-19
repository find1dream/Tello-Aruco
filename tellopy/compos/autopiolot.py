import math
import numpy as np
from collections import deque
class autopiolot():
    def __init__(self):
        self.Dronefly_P = 2.0
        self.Dronefly_D = 3.0
        self.SpdLimit = 100
        self.Max_XY = 50
        self.ErrorMargin = 15
        self.Max_error = 50
        self.DroneSpeed_P = 3.0
        self.DroneSpeed_D = 0.0
        self.TargetSpd = 2
        self.MaxRatio = 3
        self.errorpast = np.array([0.0, 0.0, 0.0])
        self.errornow  = np.array([0.0, 0.0, 0.0])
        self.derrordeque = deque([[0.0,0.0,0.0]])
        self.derror = np.arrray([0.0,0.0,0.0])
        self.MaxErrorRate = 10
        self.MaxDErrorRate = 8
    def pidCtl(self,errorlist):
        self.datafilter(errorlist)
        out = self.DroneSpeed_P * self.errornow + self.DroneSpeed_D * self.derror
        return out
    
    def datafilter(self,errorlist):
        self.errorpast = self.erroxnow
        self.errornow = errorlist

        for index, value in enumerate(self.errornow):
            if value > self.MaxErrorRate:
                self.errornow[index] = self.MaxErrorRate
            if value < -self.MaxErrorRate:
                self.errornow[index] = - self.MaxErrorRate

        derror = self.errornow - self.errorpast

        for index, value in enumerate(derror):
            if value > self.MaxErrorRate:
                derror[index] = self.MaxDErrorRate
            if value < -self.MaxErrorRate:
                derror[index] = - self.MaxDErrorRate
        self.derror = derror
        self.derrordeque.append(derror)
        if len(self.derrordeque) > 5:
            self.derrordeque.popleft()
        
    # input: angle, position now and target, 
    # output: pid out of x, y
    def sameAngleAutoflytoXY(nowpos, nowangle, targetpos):
        errorlist = nowpos - targetpos
        out = self.pidCtl(errorlist)
        #if (abs(ErrorX)<ErrorMargin):
        Out_X = out[0]
        #if (abs(ErrorY)<ErrorMargin):
        Out_Y = out[1]

        Out_X = Out_X * math.cos(math.radians(nowangle)) + Out_Y * math.sin(math.radians(nowangle))
        Out_Y = -Out_X * math.sin(math.radians(nowangle)) + Out_Y * math.cos(math.radians(nowangle))
        ratio = 1.0 
        if abs(ErrorX)>ErrorMargin or abs(ErrorY)>ErrorMargin:
            error_rate = abs(ErrorX) if abs(ErrorX) > self.ErrorMargin else abs(ErrorY)
            if error_rate > self.Max_error:
                error_rate = self.Max_error
            ratio = (ratio - self.ErrorMargin*(self.MaxRatio - ratio)/(self.Max_erorr - self.ErrorMargin))+\
                    ((self.MaxRatio - ratio)/(self.Max_error - self.ErrorMargin))*error_rate
        Out_X = Out_X*ratio
        Out_Y = Out_Y*ratio

        if abs(Out_X)>SpdLimit or abs(Out_Y)> SpdLimit:
            Cpsratio = SpdLimit/abs(Out_X) if abs(Out_X)>abs(Out_Y) else SpdLimit/abs(Out_Y)
            Out_X = Cpsratio * Out_X
            Out_Y = Cpsratio * Out_Y
        return Out_X, Out_Y



# input:  position now and target, 
# output: pid out of z
def sameAngleAutoflytoHeight(nowpos,targetpos):
    ErrorZ = targetpos[0] - nowpos[0]
    Out_Z = 0
    if (abs(ErrorZ) >2):
        Out_Z = ErrorZ * Dronefly_P
    return Out_Z



if __name__ == "__main__":
    pass
