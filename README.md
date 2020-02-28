# Tello-Aruco
 
the main file is /tellopy/compos/tellofly.py

the code is based on library [tellopy](https://github.com/hanyazou/TelloPy)


my code is for my project, so it changes ofen, if you want to use some of it, the best way maybe by reading the code I wrote and try it in you own project.

**Main differece with tellopy**:

I hacked the library and then can use 

  1.high speed mode(in theory max 10m/s, doesn't work now)
  
  2.mvo data(speed, position)
  
  3.tello attitudes
  

**what I've done**:

  1.use cascade PID to control tello position(very fast and stable)
  
  2.use an additional camera(bottom facing) to esitimate the position of tello now
  
  3.use multiple threads to perform all kinds of work(like: udp receiving/sending, video receving, face tracking, timer and so on)
  
  4.use pytorch(I use the gpu version) to perform head tracking
  
  5.integrate https://github.com/find1dream/dronePosPlan to the project

  
  
  Head recognition example.
  ![](https://github.com/find1dream/Tello-Aruco/blob/master/head%20recognition.png)
  
  
  
  
  
