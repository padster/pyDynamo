import math
import numpy as np

from PyQt5 import QtCore, QtWidgets

from .scatter3DCanvas import Scatter3DCanvas
from .dendriteCanvasActions import DendriteCanvasActions
from .dendriteVolumeCanvas import DendriteVolumeCanvas
from .np2qt import np2qt
from .QtImageViewer import QtImageViewer


# MEGA HACK
def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

MAT = rotation_matrix([0, 0, 1], math.pi / 2.0)

def hackRotate(points):
    print (MAT.shape)
    print (points.shape)
    return np.dot(MAT, points.T).T

# HACK
n = 5
POINTS = np.random.rand(n, 3)
ROTPOINTS = hackRotate(POINTS)

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, hackVolume, hackModel):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Dynamo")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QHBoxLayout(self.main_widget)
        self.scatter3d = Scatter3DCanvas(hackModel, self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(self.scatter3d)
        self.dendrites = DendriteVolumeCanvas(hackVolume, hackModel, self.scatter3d, self.main_widget)
        l.addWidget(self.dendrites)
        self.actionHandler = DendriteCanvasActions(self.dendrites)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", "Fill in stuff here?")

    def keyPressEvent(self, event):
        key = event.key()
        print (key)
        if (key == 32):
            newP = np.random.rand(n, 3)
            newPRot = absorient.hackRotate(newP)
        elif (key == 49): # '1' = next z axis plane
            self.dendrites.changeZAxis(1)
        elif (key == 50): # '2' = previous z axis plane
            self.dendrites.changeZAxis(-1)
        elif (key == 52): # '4'
            self.dendrites.brightnessAction(-1, 0)
        elif (key == 53): # '5'
            self.dendrites.brightnessAction(1, 0)
        elif (key == 54): # '6'
            self.dendrites.brightnessAction(0, 0, reset=True)
        elif (key == 55): # '7'
            self.dendrites.brightnessAction(0, -1)
        elif (key == 56): # '8'
            self.dendrites.brightnessAction(0, 1)
        elif (key == 88): # x = zoom in
            self.actionHandler.zoom(-0.2) # ~= ln(0.8) as used in matlab
        elif (key == 90): # z = zoom out
            self.actionHandler.zoom(0.2)
        elif (key == 87): # w = pan up
            self.actionHandler.pan(0, -1)
        elif (key == 65): # a = pan left
            self.actionHandler.pan(-1, 0)
        elif (key == 83): # s = pan down
            # TODO - ctrl-s = save
            self.actionHandler.pan(0, 1)
        elif (key == 68): # d = pan right
            self.actionHandler.pan(1, 0)
