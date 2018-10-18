import sys
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph.opengl as gl
import pyqtgraph as pg


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(777, 777)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.graph = gl.GLViewWidget(self.centralwidget)
        self.graph.setObjectName("graph")
        self.verticalLayout.addWidget(self.graph)

        self.graph.opts['distance'] = 30
        self.graph.show()
        self.g = gl.GLGridItem()
        self.graph.addItem(self.g)

        self.n=1
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
        self.graph.addItem(self.scttrPlt)

        self.psbtn = QtGui.QPushButton(self.centralwidget)
        self.psbtn.setObjectName("psbtn")
        self.psbtn.setText("Plot")
        self.verticalLayout.addWidget(self.psbtn)

        QtCore.QObject.connect(self.psbtn, QtCore.SIGNAL("clicked()"), self.plot)

    def plot(self):
        self.n+=1
        numX, startX, endX = self.n, -1, 1+self.n
        numY, startY, endY = self.n, -1, 1+self.n
        numZ, startZ, endZ = self.n, -1, 1+self.n

        X = np.linspace(startX, endX, numX)
        Y = np.linspace(startY, endY, numY)
        Z = np.linspace(startZ, endZ, numZ)

        pos = np.array([[i,j,k] for i in X for j in Y for k in Z])
        color = (1,1,1,1)
        size = 0.5

        self.scttrPlt.setData(pos=pos,color=color,size=size)


pg.setConfigOption('foreground', 'k')
pg.setConfigOption('background', 'w')


class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
