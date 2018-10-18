from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import socket
from collections import deque
udp_ip = "127.0.0.1"
udp_port = 5555

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverSock.bind((udp_ip, udp_port))
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.setGeometry(0,110,1920,1080)
w.show()

gx = gl.GLGridItem()
gx.rotate(90, 0, 1, 0)
gx.translate(-10, 0, 0)
w.addItem(gx)
gy = gl.GLGridItem()
gy.rotate(90, 1, 0, 0)
gy.translate(0, -10, 0)
w.addItem(gy)
gz = gl.GLGridItem()
gz.translate(0, 0, -10)
w.addItem(gz)

pos = np.random.randint(-10,10,size=(1,8,3))
#pos[:,:,2] = np.abs(pos[:,:,2])

ScatterPlotItems = {}
for point in np.arange(8):
    ScatterPlotItems[point] = gl.GLScatterPlotItem(pos=pos[:,point,:])
    w.addItem(ScatterPlotItems[point])
#w.removeItem(ScatterPlotItems[0])
color = np.zeros((pos.shape[0],10,4), dtype=np.float32)
color[:,:,0] = 1
color[:,:,1] = 1
color[:,:,2] = 1
color[0:5,:,3] = 1 #np.tile(np.arange(1,6)/5., (10,1)).T

posQueue = deque([[0.0,0.0,0.0]])
#pos = np.random.randint(-10,10,size=(1,10,3))
def update():
    ## update volume colors
    global color
    
    data, addr = serverSock.recvfrom(1024)
    data = data.decode()
    data = [float(m)*50 for m in data.split()]
    posQueue.append(data)
    #print(posQueue)
    if len(posQueue) > 8:
        
        posQueue.popleft()
        pos[0] = posQueue
        print(posQueue, pos)
        for point in np.arange(8):
            w.removeItem(ScatterPlotItems[point])
        for point in np.arange(8):
            ScatterPlotItems[point] = gl.GLScatterPlotItem(pos=pos[:,point,:])
            w.addItem(ScatterPlotItems[point])
    #for point in np.arange(3):
    #    ScatterPlotItems[point].setData(color=color[:,point,:])
    color = np.roll(color,1, axis=0)

t = QtCore.QTimer()
t.timeout.connect(update)
t.start(5)
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
