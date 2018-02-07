import attr

from .tree import *
from .uiState import *

@attr.s
class FullState:
    # Paths to *.tif image files.
    filePaths = attr.ib(default=attr.Factory(list))

    # Image-specific tree data, one for each of the files above
    trees = attr.ib(default=attr.Factory(list))

    # Image-specific options, one for each of the files above
    uiStates = attr.ib(default=attr.Factory(list))

    # Size of 3D volume, needs to be the same between stacks
    volumeSize = attr.ib(default=None)

    # Shared UI position in the Z plane
    zAxisAt = attr.ib(default=0)

    # Shared UI Option for dendrite line width
    lineWidth = attr.ib(default=3)

    # Keep track of the highest point ID created, used for making more unique identifiers.
    _currentPointID = 0

    # Keep track of the highest branch ID created, used for making more unique identifiers.
    _currentBranchID = 0

    # Get the index of a state, or -1 if it's not contained.
    def indexForState(self, uiState):
        try:
            return self.uiStates.index(uiState)
        except:
            return -1

    # TODO: active window
    # TODO: add new window off active

    def addFiles(self, filePaths):
        for path in filePaths:
            self.filePaths.append(path)
            nextTree = Tree() # TODO: add nextTree as child of prevTree
            self.trees.append(nextTree)
            self.uiStates.append(UIState(parent=self, tree=nextTree))

    def toggleLineWidth(self):
        if self.lineWidth == 4:
            self.lineWidth = 1
        else:
            self.lineWidth += 1

    def changeZAxis(self, delta):
        self.zAxisAt = snapToRange(self.zAxisAt + delta, 0, self.volumeSize[0] - 1)

    def updateVolumeSize(self, volumeSize):
        # TODO: Something better when volume sizes don't match? ...
        if self.volumeSize is None:
            self.volumeSize = volumeSize

    def nextPointID(self):
        newID = '%08x' % self._currentPointID
        self._currentPointID += 1
        return newID

    def nextBranchID(self):
        newID = '%04x' % self._currentBranchID
        self._currentBranchID += 1
        return newID

    ##
    ## ANALOGOUS methods
    ## TODO: fix up ID system, do properly.
    ##

    def convertLocation(self, sourceLocation, sourceID, targetID):
        # given a point, pass it through the transformation from source to
        # target, with the branch base as the translation reference source
        # and landmarks as the rotation reference. return the position.
        noRotation = True # all(all(state{targetID}.info.R == eye(3))) || isempty(state{targetID}.info.R)
        if sourceID == targetID or noRotation:
            return sourceLocation
        # TODO - rotation logic, see matlab.
        return sourceLocation # HACK - support rotations

    def analogousPoint(self, sourcePoint, sourceID, targetID):
        # TODO - rotation logic, see matlab.
        if sourceID == targetID:
            return sourcePoint
        return self.uiStates[targetID]._tree.getPointByID(sourcePoint.id)

    def analogousBranch(self, sourceBranch, sourceID, targetID):
        if sourceBranch == None or sourceID == targetID:
            return sourceBranch
        return self.uiStates[targetID]._tree.getBranchByID(sourceBranch.id)
