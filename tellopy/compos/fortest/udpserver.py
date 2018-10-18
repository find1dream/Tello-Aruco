import socket
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import deque
udp_ip = "127.0.0.1"
udp_port = 5555

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverSock.bind((udp_ip, udp_port))

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
posQueue = deque([[0.0,0.0,0.0]])
while True:
    data, addr = serverSock.recvfrom(1024)
    data = data.decode()
    data = [float(m) for m in data.split()]
    posQueue.append(data)
    #print(posQueue)
    if len(posQueue) > 10:
        posQueue.popleft()
        ax.plot([posQueue[i][0]*100 for i in range(0,10)],\
                        [posQueue[i][1]*100 for i in range(0,10)],\
                        [posQueue[i][2]*100 for i in range(0,10)])
        plt.draw()
        plt.pause(0.05)
        ax.cla()
    #print("messages: ", data)
