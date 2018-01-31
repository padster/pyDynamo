from PyQt5.QtGui import QPen, QPainter, QBrush, QFont, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF

import matplotlib.pyplot as plt
import numpy as np

"""
White dot = point on this plane
Green dot = current point
Solid line = line with end on this plne
Dashed line = line without end on this plane
Only draw ones with Z < 3 difference, UNLESS all are drawn
"""
class DendritePainter():
    # TODO - scale with zoom.
    NODE_CIRCLE_DIAMETER = 5
    NODE_CIRCLE_PEN = QPen(QBrush(Qt.black), 1, Qt.SolidLine)
    NODE_CIRCLE_BRUSH = QBrush(Qt.white)
    NODE_CIRCLE_SELECTED_BRUSH = QBrush(Qt.cyan)

    ANNOTATION_PEN = QPen(QBrush(Qt.yellow), 1, Qt.SolidLine)
    ANNOTATION_FONT = QFont("Arial", 12, QFont.Bold)
    ANNOTATION_OFFSET = 20
    ANNOTATION_HEIGHT = 40
    ANNOTATION_MAX_WIDTH = 512

    LINE_COLOR_COUNT = 7
    LINE_COLORS = plt.get_cmap('hsv')(np.arange(0.0, 1.0, 1.0/LINE_COLOR_COUNT))[:, :3]

    def __init__(self, painter, currentZ, uiState, zoomMapFunc):
        self.p = painter
        self.zAt = currentZ
        self.uiState = uiState
        self.zoomMapFunc = zoomMapFunc
        self.colorAt = 1 # Start at yellow, not red.

    def drawTree(self, tree):
        selectedPoint = self.uiState.currentPoint()
        for branch in tree.branches:
            self.drawBranchLines(branch)
            self.colorAt = (self.colorAt + 1) % self.LINE_COLOR_COUNT
        if tree.rootPoint is not None:
            self.drawPoint(tree.rootPoint, selectedPoint)
        for branch in tree.branches:
            self.drawBranchPoints(branch, selectedPoint)

    def drawBranchLines(self, branch):
        for i in range(len(branch.points)):
            previousPoint = branch.parentPoint if i == 0 else branch.points[i-1]
            lastX, lastY, lastZ = self.zoomedLocation(previousPoint.location)
            thisX, thisY, thisZ = self.zoomedLocation(branch.points[i].location)
            linePen = self.getLinePen(lastZ, thisZ)
            if linePen is not None:
                self.p.setPen(linePen)
                self.p.drawLine(lastX, lastY, thisX, thisY)

    def drawBranchPoints(self, branch, selectedPoint):
        for i in range(len(branch.points)):
            self.drawPoint(branch.points[i], selectedPoint)

    def drawPoint(self, point, selectedPoint):
        x, y, z = self.zoomedLocation(point.location)
        annotation = point.annotation
        if z == self.zAt:
            self.drawCircleThisZ(x, y, point == selectedPoint)
            if annotation != "":
                self.drawAnnotation(x, y, annotation)

    def drawCircleThisZ(self, x, y, isSelected):
        self.p.setPen(self.NODE_CIRCLE_PEN)
        self.p.setBrush(self.NODE_CIRCLE_SELECTED_BRUSH if isSelected else self.NODE_CIRCLE_BRUSH)
        self.p.drawEllipse(QPointF(x, y), self.NODE_CIRCLE_DIAMETER, self.NODE_CIRCLE_DIAMETER)

    def drawAnnotation(self, x, y, text):
        if not self.uiState.showAnnotations:
            return
        self.p.setFont(self.ANNOTATION_FONT)
        self.p.setPen(self.ANNOTATION_PEN)
        textRect = QRectF(
            x + self.ANNOTATION_OFFSET, y - self.ANNOTATION_HEIGHT / 2,
            self.ANNOTATION_MAX_WIDTH, self.ANNOTATION_HEIGHT
        )
        self.p.drawText(textRect, Qt.AlignVCenter, text)

    def getLinePen(self, z1, z2):
        inZ1, inZ2 = z1 == self.zAt, z2 == self.zAt
        near1, near2 = self.isNearZ(z1), self.isNearZ(z2)
        if inZ1 or inZ2:
            color = self.LINE_COLORS[self.colorAt]
            color = QColor.fromRgbF(color[0], color[1], color[2])
            return QPen(QBrush(color), self.uiState.parent().lineWidth, Qt.SolidLine)
        elif near1 or near2 or self.uiState.drawAllBranches:
            color = self.LINE_COLORS[self.colorAt]
            color = QColor.fromRgbF(color[0], color[1], color[2])
            return QPen(QBrush(color), self.uiState.parent().lineWidth, Qt.DashLine)
        else:
            return None

    def zoomedLocation(self, xyz):
        x, y, z = xyz
        zoomedXY = self.zoomMapFunc(x, y)
        return (zoomedXY.x(), zoomedXY.y(), z)


    # HACK - utilities
    def isNearZ(self, z):
        return abs(z - self.zAt) < 3
