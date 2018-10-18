from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys


class Visualizer(object):
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        self.traces = gl.GLLinePlotItem(pos = [0,0,0]) #initialize with empty plot
        self.w = gl.GLViewWidget()
        self.w.addItem(self.traces)
        #self.traces = dict()
        self.w.opts['distance'] = 20
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        #self.y = np.linspace(-1, 1, self.n)
        self.phase = 0

        self.n=5
        numX, startX, endX = self.n, -1, 1+self.n
        numY, startY, endY = self.n, -1, 1+self.n
        numZ, startZ, endZ = self.n, -1, 1+self.n
        X = np.linspace(startX, endX, numX)
        Y = np.linspace(startY, endY, numY)
        Z = np.linspace(startZ, endZ, numZ)

        #position of scatter in 3D
        pos = np.array([[i,j,k] for i in X for j in Y for k in Z])

        color = (1,1,1,1)
        size = 0.5

        self.scttrPlt = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        self.scttrPlt.translate(5,5,0)
        self.w.addItem(self.scttrPlt)


       # for i in range(self.n):
       #     yi = np.array([self.y[i]] * self.m)
       #     d = np.sqrt(self.x ** 2 + yi ** 2)
       #     z = np.random.rand(2)
       #     #pts = np.vstack([self.x, yi, z]).transpose()
       #     #self.traces[i] = gl.GLLinePlotItem(pos=pts, color=pg.glColor(
       #     #    (i, self.n * 1.3)), width=(i + 1) / 10, antialias=True)
       #     color=pg.glColor((i, self.n * 1.3)),
       #     pos = pts
       #     size = 2
       #     self.scttrPlt = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
       #     #self.scttrPlt.translate(5,5,0)
       #     self.w.addItem(self.scttrPlt)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)

    def update(self):
        #self.n+=1
        numX, startX, endX = self.n, -1, 1+self.n
        numY, startY, endY = self.n, -1, 1+self.n
        numZ, startZ, endZ = self.n, -1, 1+self.n

        X = np.linspace(startX, endX, numX)
        Y = np.linspace(startY, endY, numY)
        Z = np.linspace(startZ, endZ, numZ)

        pos = np.array([[i,j,k] for i in X for j in Y for k in Z])
        color = (1,1,1,1)
        size = 5

        self.scttrPlt.setData(pos=pos,color=color,size=size)
       # for i in range(self.n):
       #     yi = np.random.rand(2)
       #     #yi = np.array([self.y[i]] * self.m)
       #     #d = np.sqrt(self.x ** 2 + yi ** 2)
       #     z = np.random.rand(2)
       #     pts = np.vstack([self.x, yi, z]).transpose()
       #     #self.set_plotdata(
       #     #    name=i, points=pts,
       #     #    color=pg.glColor((i, self.n * 1.3)),
       #     #    width=(i + 1) / 10
       #     #)
       #     #self.phase -= .003

       #     color=pg.glColor((i, self.n * 1.3)),
       #     pos = pts
       #     size = 2
       #     self.scttrPlt = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
       #     self.scttrPlt.translate(5,5,0)
       #     self.w.addItem(self.scttrPlt)
    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer()
    v.animation()
