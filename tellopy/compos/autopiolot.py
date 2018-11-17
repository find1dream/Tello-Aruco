import math
import numpy as np
from collections import deque
class autopiolot():
    def __init__(self):
        self.Dronefly_P = 2.20#1.96
        self.Dronefly_I = 0.0  #0.17
        self.Dronefly_D = 15.0  #1 10
        self.SpdLimit = 99
        self.Max_XY = 50
        self.oldpos = None
        self.ErrorMargin = 15
        self.Max_error = 50
        self.DroneSpeed_P = 0.58
        self.DroneSpeed_D = -1.5
        self.MaxSpeed = 200   #max speed is 200cm/s
        self.TargetSpd = 2
        self.MaxRatio = 3
        self.speed = np.array([0.0,0.0,0.0])
        self.errorpast = np.array([0.0, 0.0, 0.0])
        self.errornow  = np.array([0.0, 0.0, 0.0])
        self.derrordeque = deque([[0.0,0.0,0.0]])
        self.derror = np.array([0.0,0.0,0.0])
        self.ierror = np.array([0.0,0.0,0.0])
        self.Max_ierror = 50
        self.MaxErrorRate = 10
        self.MaxDErrorRate = 8


        self.angError = 0.0
        self.angPast = 0
        self.targetAngle = 0.5
        self.DroneAng_P = 330.0
        self.DroneAng_D = 800.0

    def pidCtl(self,errorlist, nowspeed,dspeed):
        self.datafilter(errorlist)
        #print(errorlist, self.errorpast, self.errornow, self.derror)
        #ref_pout = self.Dronefly_P * self.errornow 
        #ref_dout = self.Dronefly_D 
        out_refSpd = self.Dronefly_P * self.errornow + self.Dronefly_I*self.ierror + self.Dronefly_D * self.derror
        #print("drone para",self.Dronefly_P, self.Dronefly_D,"outP:", self.Dronefly_P *self.errornow,\
        #        "outD:", self.Dronefly_D*self.derror)
        #print("out_refSpd: ", out_refSpd)
        spderror = out_refSpd - nowspeed
        for index, value in enumerate(spderror):
            if value < 1 and value > -1:
                spderror[index] = 0
        dspeed[2]+= 99.74
        out_spd = self.DroneSpeed_P * (spderror ) + self.DroneSpeed_D * dspeed
        #print(out_spd, errorlist, self.ierror)
        return out_spd,out_refSpd
    
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

        self.ierror += self.errornow

        for index, value in enumerate(self.ierror):
            if value > self.Max_ierror:
                self.ierror[index] = self.Max_ierror
            if value < -self.Max_ierror:
                self.ierror[index] = - self.Max_ierror
        #print("derror: ", self.derror)
        self.derrordeque.append(derror)
        if len(self.derrordeque) > 5:
            self.derrordeque.popleft()
        
    # input: angle, position now and target, 
    # output: pid out of x, y
  #  def sameAngleAutoflytoXY(self,nowpos, nowangle, targetpos):
  #      #print(nowpos, targetpos, nowpos-targetpos)
  #      #print(self.Drone)
  #      errorlist = targetpos - nowpos
  #      out = self.pidCtl(errorlist)

  #      Out_X = out[0] * math.cos(math.radians(nowangle)) + out[1] * math.sin(math.radians(nowangle))
  #      Out_Y = -out[0] * math.sin(math.radians(nowangle)) + out[1] * math.cos(math.radians(nowangle))
  #      ratio = 1.0 
  #      #print("out now: ",Out_X, Out_Y)
  #     # if abs(self.errornow[0])>self.ErrorMargin or abs(self.errornow[1])>self.ErrorMargin:
  #     #     error_rate = abs(self.errornow[0]) if abs(self.errornow[0]) > self.ErrorMargin else abs(self.errornow[1])
  #     #     if error_rate > self.Max_error:
  #     #         error_rate = self.Max_error
  #     #     ratio = (ratio - self.ErrorMargin*(self.MaxRatio - ratio)/(self.Max_error - self.ErrorMargin))+\
  #     #             ((self.MaxRatio - ratio)/(self.Max_error - self.ErrorMargin))*error_rate
  #     # Out_X = Out_X*ratio
  #     # Out_Y = Out_Y*ratio

  #      if abs(Out_X)>self.SpdLimit or abs(Out_Y)> self.SpdLimit:
  #          Cpsratio = self.SpdLimit/abs(Out_X) if abs(Out_X)>abs(Out_Y) else self.SpdLimit/abs(Out_Y)
  #          Out_X = Cpsratio * Out_X
  #          Out_Y = Cpsratio * Out_Y
  #      #print("out after transfrom: ", Out_X, Out_Y)
  #      return Out_X, Out_Y

    def getspeed(self, nowpos, dtime):
        
        if self.oldpos is not None:
            try:
                length = (nowpos-self.oldpos)    # cm/s
                #print("length: ", length)
                self.speed = length / dtime
                for index, value in enumerate(self.speed):
                    if value > self.MaxSpeed:
                        self.speed[index] = self.MaxSpeed
                    if value < -self.MaxSpeed:
                        self.speed[index] = - self.MaxSpeed
            
            except:
                print("dtime is zero!!")
        self.oldpos = nowpos
        #print("speed now : ", self.speed)
        return self.speed

    def turnToangle(self, angleNow):
        self.angPast = self.angError
        self.angError = self.targetAngle - angleNow
        out = self.DroneAng_P * self.angError + self.DroneAng_D * (self.angError - self.angPast)
        if out > 100:
            out = 100
        elif out < -100:
            out = -100
        return out
        

    def sameAngleAutoflytoXYZ(self,nowpos, nowspeed, dspeed, nowangle, targetpos):
        #print(nowpos, targetpos, nowpos-targetpos)
        #print(self.Drone)
        errorlist = targetpos - nowpos
        out,refspd = self.pidCtl(errorlist,nowspeed,dspeed)
        #print("out: " , out)
        Out_X = out[0] * math.cos(math.radians(nowangle)) + out[1] * math.sin(math.radians(nowangle))
        Out_Y = -out[0] * math.sin(math.radians(nowangle)) + out[1] * math.cos(math.radians(nowangle))
        Out_Z = out[2]
        ratio = 1.0 
        #print("out now: ",Out_X, Out_Y, Out_Z)
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
        if Out_Z > self.SpdLimit:
            Out_Z = self.SpdLimit
        elif Out_Z < -self.SpdLimit:
            Out_Z = -self.SpdLimit
        #print("out after transfrom: ", Out_X, Out_Y)
        return Out_X, Out_Y, Out_Z, refspd

# input:  position now and target, 
# output: pid out of z
def sameAngleAutoflytoHeight(nowpos,targetpos):
    ErrorZ = targetpos[0] - nowpos[0]
    Out_Z = 0
    return Out_Z



if __name__ == "__main__":
    pass
