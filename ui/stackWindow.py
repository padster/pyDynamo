import math
import numpy as np

from PyQt5 import QtCore, QtWidgets

import files

from .scatter3DCanvas import Scatter3DCanvas
from .dendriteCanvasActions import DendriteCanvasActions
from .dendriteVolumeCanvas import DendriteVolumeCanvas
from .np2qt import np2qt
from .QtImageViewer import QtImageViewer

class StackWindow(QtWidgets.QMainWindow):
    def __init__(self, windowIndex, imagePath, fullActions, uiState, parent):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.windowIndex = windowIndex
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(imagePath)

        # TODO - option for when imagePath=None, have a button to load an image?
        assert imagePath is not None
        self.imagePath = imagePath;
        imageVolume = files.tiffRead(imagePath)
        uiState.parent().updateVolumeSize(np.shape(imageVolume))

        self.root = QtWidgets.QWidget(self)
        self.dendrites = DendriteVolumeCanvas(
            windowIndex, imageVolume, fullActions, uiState, parent, self.root
        )
        self.actionHandler = DendriteCanvasActions(self.dendrites, uiState)
        self.fullActions = fullActions
        self.uiState = uiState

        # Assemble the view hierarchy.
        l = QtWidgets.QGridLayout(self.root)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.dendrites, 0, 0, QtCore.Qt.AlignCenter)
        self.root.setFocus()
        self.setCentralWidget(self.root)

        # Top level menu:
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('Quit &Window', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_W)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Shortcuts', self.actionHandler.showHotkeys, QtCore.Qt.Key_F1)

    def redraw(self):
        self.dendrites.redraw()

    def fileQuit(self):
        self.close()

    def closeEvent(self, event):
        self.parent().removeStackWindow(self.windowIndex)

    def showHotkeys(self):
        self.actionHandler.showHotkeys()

    def keyPressEvent(self, event):
        if self.parent().childKeyPress(event):
            return

        # TODO: add menu items for some of these too.
        key = event.key()
        if (key == ord('4')):
            self.actionHandler.changeBrightness(-1, 0)
        elif (key == ord('5')):
            self.actionHandler.changeBrightness(1, 0)
        elif (key == ord('6')):
            self.actionHandler.changeBrightness(0, 0, reset=True)
        elif (key == ord('7')):
            self.actionHandler.changeBrightness(0, -1)
        elif (key == ord('8')):
            self.actionHandler.changeBrightness(0, 1)
        elif (key == ord('X')):
            self.actionHandler.zoom(-0.2) # ~= ln(0.8) as used in matlab
        elif (key == ord('Z')):
            self.actionHandler.zoom(0.2)
        elif (key == ord('W')):
            self.actionHandler.pan(0, -1)
        elif (key == ord('A')):
            self.actionHandler.pan(-1, 0)
        elif (key == ord('S')):
            # TODO - ctrl-s = save
            self.actionHandler.pan(0, 1)
        elif (key == ord('D')):
            self.actionHandler.pan(1, 0)
        elif (key == ord('F')):
            self.dendrites.uiState.showAnnotations = not self.dendrites.uiState.showAnnotations
            self.redraw()
        elif (key == ord('V')):
            self.dendrites.uiState.drawAllBranches = not self.dendrites.uiState.drawAllBranches
            self.redraw()
        elif (key == ord('Q')):
            self.actionHandler.getAnnotation(self)
        elif (key == QtCore.Qt.Key_Delete):
            self.fullActions.deletePoint(self.windowIndex, self.uiState.currentPoint())
            self.parent().redrawAllStacks() # HACK - auto redraw on change
