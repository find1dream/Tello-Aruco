import math
Dronefly_P = 5.0
Dronefly_D = 0.0
Limit_XY = 20
Limit_Z = 20
# input: angle, position now and target, 
# output: pid out of x, y
def sameAngleAutoflytoXY(nowpos, nowangle,targetpos):
    ErrorX = targetpos[0] - nowpos[0]
    ErrorY = targetpos[1] - nowpos[1]
    Out_X = 0
    Out_Y = 0
    if (abs(ErrorX)>3):
        Out_X = ErrorX * Dronefly_P
    if (abs(ErrorY)>3):
        Out_Y = ErrorY * Dronefly_P
    if (abs(Out_X)>Limit_XY):
        Out_X = Limit_XY if Out_X > 0 else -Limit_XY
    if (abs(Out_Y)>Limit_XY):
        Out_Y = Limit_XY if Out_Y > 0 else -Limit_XY

    Out_X = Out_X * math.cos(math.radians(nowangle)) + Out_Y * math.sin(math.radians(nowangle))
    Out_Y = -Out_X * math.sin(math.radians(nowangle)) + Out_Y * math.cos(math.radians(nowangle))
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
