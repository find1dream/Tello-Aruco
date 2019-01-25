# Tello-Aruco
Videos: https://www.youtube.com/watch?v=2h3xuEerZMY
 
the main file is /tellopy/compos/tellofly.py

for the librarys, you can install them by reading https://github.com/hanyazou/TelloPy

my code is for my project, so it changes ofen, if you want to use some of it, the best way maybe by reading the code I wrote and try it in you own project.

**Main different with tellopy**:
I hacked the library and then can use 

  1.high speed mode(in theory max 10m/s)
  
  2.mvo data(speed, position)
  
  3.tello attitudes
  

**what I've done**:

  1.use cascade PID to control tello position(very fast and stable)
  
  2.use an additional camera(bottom facing) to esitimate the position of tello now
  
  3.use multiple threads to perform all kinds of work(like: udp receiving, video receving, timer and so on)
  
  4.use tensorflow(I use the gpu version) to perform face tracking

**todo**:

  1.integrate https://github.com/find1dream/drone-path-training to the project now
  
  2.try multiple tellos
