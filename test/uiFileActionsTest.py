import os
import time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from ui import DynamoWindow

import util
from util.testableFilePicker import setNextTestPaths

def _pointNear(locA, locB):
    return util.deltaSz(locA, locB) < 1e-9

def _init(qtbot):
    dynamoWindow = DynamoWindow(None, ["dynamo.py"])
    dynamoWindow.show()
    qtbot.addWidget(dynamoWindow)
    return dynamoWindow

def run(qtbot):
    dW = _init(qtbot)

    scan1Path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "scan1.tif")
    swc1Path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "scan1Auto.swc")
    scan2Path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "scan1.tif")

    # Click to open new stack:
    setNextTestPaths([scan1Path])
    qtbot.mouseClick(dW.initialMenu.buttonN, Qt.LeftButton)
    qtbot.waitUntil(lambda: len(dW.stackWindows) == 1)
    sW = dW.stackWindows[0]

    assert len(dW.fullState.filePaths) == 1
    assert len(dW.fullState.trees) == 1
    assert len(dW.fullState.landmarks) == 1
    assert len(dW.fullState.uiStates) == 1
    assert dW.fullState.trees[0].rootPoint is None
    assert len(dW.fullState.trees[0].branches) == 0

    # Import SWC from file:
    setNextTestPaths(swc1Path)
    qtbot.keyClick(sW, 'i', Qt.ControlModifier)

    assert dW.fullState.trees[0].rootPoint.id == '00000000'
    assert (229.0, 211.0, 25.0) == dW.fullState.trees[0].rootPoint.location
    assert (277.04, 288.029, 20.1444) == dW.fullState.trees[0].branches[5].points[2].location

    assert 23 == len(dW.fullState.trees[0].branches)
    assert 194 == len(dW.fullState.trees[0].flattenPoints())

    # qtbot.waitSignal(timeout=5000, raising=False)

    # Add file for next stack:
    setNextTestPaths([scan2Path])
    qtbot.keyClick(sW, 'n')
    qtbot.waitUntil(lambda: len(dW.stackWindows) == 2)

    assert len(dW.fullState.filePaths) == 2
    assert len(dW.fullState.trees) == 2
    assert len(dW.fullState.landmarks) == 2
    assert len(dW.fullState.uiStates) == 2
    assert dW.fullState.trees[1].rootPoint is None
    assert 0 == len(dW.fullState.trees[1].branches)

    # Copy points across:
    dW.stackWindows[1].setFocus(True)
    qtbot.waitUntil(lambda: dW.stackWindows[1].hasFocus(), timeout=10000)

    qtbot.keyClick(dW.stackWindows[1], 'i')
    qtbot.waitUntil(lambda: 23 == len(dW.fullState.trees[1].branches), timeout=10000)
    assert 23 == len(dW.fullState.trees[1].branches)
    assert 194 == len(dW.fullState.trees[1].flattenPoints())

    # Register, make sure points have moved!
    qtbot.keyClick(dW.stackWindows[1], 'r')
    assert _pointNear(
        (229.0112843123887, 211.00676163998858, 25.0),
        dW.fullState.trees[1].rootPoint.location)
    assert _pointNear(
        (277.5048473944195, 287.93487362244144, 20.1444),
        dW.fullState.trees[1].branches[5].points[2].location)

    hilighted = [p.id for p in dW.fullState.trees[1].flattenPoints() if p.hilighted]
    assert ['0000006c', '0000002b'] == hilighted
    return True
