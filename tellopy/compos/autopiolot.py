import math
import numpy as np
from collections import deque
class autopiolot():
    def __init__(self):
        self.Dronefly_P = 1.0
        self.Dronefly_D = 12.0  #1 10
        self.SpdLimit = 30
        self.Max_XY = 50
        self.ErrorMargin = 15
        self.Max_error = 50
        self.DroneSpeed_P = 0.0
        self.DroneSpeed_D = 0.0
        self.TargetSpd = 2
        self.MaxRatio = 3
        self.errorpast = np.array([0.0, 0.0, 0.0])
        self.errornow  = np.array([0.0, 0.0, 0.0])
        self.derrordeque = deque([[0.0,0.0,0.0]])
        self.derror = np.array([0.0,0.0,0.0])
        self.MaxErrorRate = 10
        self.MaxDErrorRate = 8

    def pidCtl(self,errorlist):
        self.datafilter(errorlist)
        #print(errorlist, self.errorpast, self.errornow, self.derror)
        out = self.Dronefly_P * self.errornow + self.Dronefly_D * self.derror
        print("drone para",self.Dronefly_P, self.Dronefly_D,"outP:", self.Dronefly_P *self.errornow,\
                "outD:", self.Dronefly_D*self.derror)
        return out
    
    def datafilter(self,errorlist):
        self.errorpast = self.errornow
        self.errornow = errorlist


        derror = self.errornow - self.errorpast

        for index, value in enumerate(derror):
            if value > self.MaxDErrorRate:
                derror[index] = self.MaxDErrorRate
            if value < -self.MaxDErrorRate:
                derror[index] = - self.MaxDErrorRate
        self.derror = derror
        print("derror: ", self.derror)
        self.derrordeque.append(derror)
        if len(self.derrordeque) > 5:
            self.derrordeque.popleft()
        
    # input: angle, position now and target, 
    # output: pid out of x, y
    def sameAngleAutoflytoXY(self,nowpos, nowangle, targetpos):
        #print(nowpos, targetpos, nowpos-targetpos)
        #print(self.Drone)
        errorlist = targetpos - nowpos
        out = self.pidCtl(errorlist)

        Out_X = out[0] * math.cos(math.radians(nowangle)) + out[1] * math.sin(math.radians(nowangle))
        Out_Y = -out[0] * math.sin(math.radians(nowangle)) + out[1] * math.cos(math.radians(nowangle))
        ratio = 1.0 
        print("out now: ",Out_X, Out_Y)
       # if abs(self.errornow[0])>self.ErrorMargin or abs(self.errornow[1])>self.ErrorMargin:
       #     error_rate = abs(self.errornow[0]) if abs(self.errornow[0]) > self.ErrorMargin else abs(self.errornow[1])
       #     if error_rate > self.Max_error:
       #         error_rate = self.Max_error
       #     ratio = (ratio - self.ErrorMargin*(self.MaxRatio - ratio)/(self.Max_error - self.ErrorMargin))+\
       #             ((self.MaxRatio - ratio)/(self.Max_error - self.ErrorMargin))*error_rate
       # Out_X = Out_X*ratio
       # Out_Y = Out_Y*ratio

        if abs(Out_X)>self.SpdLimit or abs(Out_Y)> self.SpdLimit:
            Cpsratio = self.SpdLimit/abs(Out_X) if abs(Out_X)>abs(Out_Y) else self.SpdLimit/abs(Out_Y)
            Out_X = Cpsratio * Out_X
            Out_Y = Cpsratio * Out_Y
        print("out after transfrom: ", Out_X, Out_Y)
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
