import math
import numpy as np

from PyQt5 import QtCore, QtWidgets

import files
import util

from .actions.dendriteCanvasActions import DendriteCanvasActions
from .dendriteVolumeCanvas import DendriteVolumeCanvas
from .np2qt import np2qt
from .QtImageViewer import QtImageViewer

_IMG_CACHE = files.ImageCache()

class StackWindow(QtWidgets.QMainWindow):
    def __init__(self, windowIndex, imagePath, fullActions, uiState, parent):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.windowIndex = windowIndex
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

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
        # Re-enable for layout testing:
        # self.dendrites.setStyleSheet("border: 1px solid red;")
        self.actionHandler = DendriteCanvasActions(self.dendrites, imagePath, uiState)
        self.fullActions = fullActions
        self.uiState = uiState
        self.ignoreUndoCloseEvent = False

        # Assemble the view hierarchy.
        l = QtWidgets.QGridLayout(self.root)
        # l.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.dendrites, 0, 0) #, QtCore.Qt.AlignCenter)
        self.root.setFocus()
        # self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.root.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setCentralWidget(self.root)

        # Top level menu:
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('Quit &Window', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_W)
        self.menuBar().addMenu(self.file_menu)
        self.edit_menu = QtWidgets.QMenu('&Edit', self)
        self.edit_menu.addAction('Undo', self.undo, QtCore.Qt.CTRL + QtCore.Qt.Key_Z)
        self.edit_menu.addAction('Redo', self.redo, QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_Z)
        self.menuBar().addMenu(self.edit_menu)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Shortcuts', self.actionHandler.showHotkeys, QtCore.Qt.Key_F1)
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

    def fileQuit(self):
        self.close()

    def showHotkeys(self):
        self.actionHandler.showHotkeys()

    def undo(self):
        self.parent().updateUndoStack(isRedo=False, originWindow=self)

    def redo(self):
        self.parent().updateUndoStack(isRedo=True, originWindow=self)

    def keyPressEvent(self, event):
        try:
            if self.parent().childKeyPress(event, self):
                return
            ctrlPressed = (event.modifiers() & QtCore.Qt.ControlModifier)
            shftPressed = (event.modifiers() & QtCore.Qt.ShiftModifier)

            # TODO: add menu items for some of these too.
            key = event.key()
            if (key == ord('3')):
                self.actionHandler.launch3DView()
            elif (key == ord('4')):
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
                self.actionHandler.pan(0, 1)
            elif (key == ord('D')):
                self.actionHandler.pan(1, 0)
            elif (key == ord('F')):
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
            elif (key == ord('V')):
                self.dendrites.uiState.drawAllBranches = not self.dendrites.uiState.drawAllBranches
                self.redraw()
            elif (key == ord('H')):
                self.dendrites.uiState.showHilighted = not self.dendrites.uiState.showHilighted
                self.redraw()
            elif (key == ord('Q')):
                self.actionHandler.getAnnotation(self)
            elif (key == ord('I')):
                if ctrlPressed:
                    filePath = self.getSWCFilePath()
                    if filePath is not None:
                        self.actionHandler.importPointsFromSWC(self.windowIndex, filePath)
                else:
                    self.actionHandler.importPointsFromLastStack(self.windowIndex)
                self.redraw()
            elif (key == ord('R')):
                self.actionHandler.registerImages(self.windowIndex)
                self.redraw()
            elif (key == QtCore.Qt.Key_Delete):
                self.fullActions.deletePoint(self.windowIndex, self.uiState.currentPoint(), laterStacks=shftPressed)
                self.parent().redrawAllStacks() # HACK - auto redraw on change
        except Exception as e:
            print ("Whoops - error on keypress: " + str(e))
            raise # POIUY

    def getSWCFilePath(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self,
            "Import SWC file", "", "SWC file (*.swc)"
        )
        return filePath
