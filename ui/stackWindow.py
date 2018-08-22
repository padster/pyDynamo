import math
import numpy as np
import traceback

from PyQt5 import QtCore, QtWidgets

import files
import util

from .actions.dendriteCanvasActions import DendriteCanvasActions
from .dendriteVolumeCanvas import DendriteVolumeCanvas
from .np2qt import np2qt
from .QtImageViewer import QtImageViewer
from .topMenu import TopMenu

_IMG_CACHE = files.ImageCache()

class StackWindow(QtWidgets.QMainWindow):
    def __init__(self, windowIndex, imagePath, fullActions, uiState, parent):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.windowIndex = windowIndex
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)

        # TODO - option for when imagePath=None, have a button to load an image?
        assert imagePath is not None
        self.imagePath = imagePath
        uiState.imagePath = imagePath
        _IMG_CACHE.handleNewUIState(uiState)

        self.windowIndex = windowIndex
        self.updateTitle()

        self.root = QtWidgets.QWidget(self)
        self.dendrites = DendriteVolumeCanvas(
            windowIndex, fullActions, uiState, parent, self, self.root
        )
        self.actionHandler = DendriteCanvasActions(self.dendrites, imagePath, uiState)
        self.fullActions = fullActions
        self.uiState = uiState
        self.ignoreUndoCloseEvent = False

        # Assemble the view hierarchy.
        l = QtWidgets.QGridLayout(self.root)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.dendrites, 0, 0)
        self.root.setFocus()
        self.setCentralWidget(self.root)

        # Top level menu:
        self.topMenu = TopMenu(self)
        self.statusBar().showMessage("") # Force it to be visible, so we can use later.

    def closeEvent(self, event):
        if not self.ignoreUndoCloseEvent:
            self.parent().removeStackWindow(self.windowIndex)

    def updateState(self, newFilePath, newUiState):
        self.imagePath = newFilePath
        self.uiState = newUiState
        self.dendrites.updateState(newUiState)
        self.actionHandler.updateUIState(newUiState)
        _IMG_CACHE.handleNewUIState(newUiState)
        self.updateTitle()

    def updateWindowIndex(self, windowIndex):
        self.windowIndex = windowIndex
        self.updateTitle()

    def updateTitle(self):
        self.setWindowTitle(util.createTitle(self.windowIndex, self.imagePath))

    def redraw(self):
        self.dendrites.redraw()

    def keyPressEvent(self, event):
        try:
            if self.parent().childKeyPress(event, self):
                return
            ctrlPressed = (event.modifiers() & QtCore.Qt.ControlModifier)
            shftPressed = (event.modifiers() & QtCore.Qt.ShiftModifier)

            # Actions here all apply even if the stack's tree is hidden:
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
            elif (key == ord('W')):
                self.actionHandler.pan(0, -1)
            elif (key == ord('A')):
                self.actionHandler.pan(-1, 0)
            elif (key == ord('S')):
                self.actionHandler.pan(0, 1)
            elif (key == ord('D')):
                self.actionHandler.pan(1, 0)

            if self.uiState.hideAll:
                return

            # Actions only apply if the stack's tree is visible:
            if (key == ord('F')):
                if self.dendrites.uiState.showAnnotations:
                    self.dendrites.uiState.showAnnotations = False
                    self.dendrites.uiState.showIDs = True
                elif self.dendrites.uiState.showIDs:
                    self.dendrites.uiState.showAnnotations = False
                    self.dendrites.uiState.showIDs = False
                else:
                    self.dendrites.uiState.showAnnotations = True
                    self.dendrites.uiState.showIDs = False
                self.redraw()
            elif (key == ord('Q')):
                self.actionHandler.getAnnotation(self)
            elif (key == QtCore.Qt.Key_Delete):
                toDelete = self.uiState.currentPoint()
                if toDelete is None:
                    print ("Need to select a point before you can delete...")
                else:
                    self.fullActions.deletePoint(self.windowIndex, toDelete, laterStacks=shftPressed)
                    self.parent().redrawAllStacks() # HACK - auto redraw on change
        except Exception as e:
            print ("Whoops - error on keypress: " + str(e))
            traceback.print_exc()
            # TODO: add this back in if the app feels stable?
            # raise
