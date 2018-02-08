from .tree import *

class FullStateActions():
    def __init__(self, fullState):
        self.state = fullState

    def selectPoint(self, localIdx, point):
        for state in self.state.uiStates:
            state.selectPointByID(point.id)

    def addPointToCurrentBranchAndSelect(self, localIdx, location):
        localState = self.state.uiStates[localIdx]
        newPoint = localState.addPointToCurrentBranchAndSelect(location)
        newPointBranchID = None if newPoint.isRoot() else newPoint.parentBranch.id

        for i in range(localIdx + 1, len(self.state.uiStates)):
            state = self.state.uiStates[i]
            newLocation = self.state.convertLocation(location, localIdx, i)
            state.addPointToCurrentBranchAndSelect(newLocation, newPoint.id, newPointBranchID)

    def addPointToNewBranchAndSelect(self, localIdx, location):
        localState = self.state.uiStates[localIdx]
        currentSource = localState.currentPoint()
        newPoint, newBranch = localState.addPointToNewBranchAndSelect(location)

        for i in range(localIdx + 1, len(self.state.uiStates)):
            state = self.state.uiStates[i]
            newLocation = self.state.convertLocation(location, localIdx, i)
            state.selectPointByID(currentSource.id)
            state.addPointToNewBranchAndSelect(newLocation, newPoint.id, newBranch.id)

    def addPointMidBranchAndSelect(self, localIdx, location):
        localState = self.state.uiStates[localIdx]
        currentSource = localState.currentPoint()
        currentBranch = localState.currentBranch()

        newPoint, isAfter = localState.addPointMidBranchAndSelect(location)

        for i in range(localIdx + 1, len(self.state.uiStates)):
            state = self.state.uiStates[i]
            newLocation = self.state.convertLocation(location, localIdx, i)
            newBranch = self.state.analogousBranch(currentBranch, localIdx, i)
            newSource = self.state.analogousPoint(currentSource, localIdx, i)
            state.addKnownPointMidBranchAndSelect(
                newLocation, newBranch, newSource, isAfter, newPoint.id
            )

    def deletePoint(self, localIdx, point):
        # TODO: Delete point vs delete entire branch of point
        for i in range(localIdx, len(self.state.uiStates)):
            state = self.state.uiStates[i].deletePointByID(point.id)
