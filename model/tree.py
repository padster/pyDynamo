import attr
import util

from util import SAVE_META

@attr.s
class Point():
    # Identifier of point, can be shared across stacks.
    id = attr.ib(metadata=SAVE_META)

    # Node position as an (x, y, z) tuple.
    location = attr.ib(metadata=SAVE_META) # (x, y, z) tuple

    # Branch this point belongs to
    parentBranch = attr.ib(default=None, repr=False, cmp=False)

    # Text annotation for node.
    annotation = attr.ib(default="", cmp=False, metadata=SAVE_META)

    # Branches coming off the node.
    children = attr.ib(default=attr.Factory(list))

    # Not sure...?
    hilighted = attr.ib(default=None, cmp=False) # Not used yet

    def isRoot(self):
        return self.parentBranch is None

@attr.s
class Branch():
    # Identifier of a branch, can be shared across stacks.
    id = attr.ib(metadata=SAVE_META)

    # Tree the branch belongs to
    _parentTree = attr.ib(default=None, repr=False, cmp=False)

    # Node this branched off, or None for root branch
    parentPoint = attr.ib(default=None, repr=False, cmp=False, metadata=SAVE_META)

    # Points along this dendrite branch, in order.
    points = attr.ib(default=attr.Factory(list), metadata=SAVE_META)

    # Not sure...?
    isEnded = attr.ib(default=False, cmp=False) # Not used yet

    # Not sure...?
    colorData = attr.ib(default=None, cmp=False) # Not used yet

    def indexForPoint(self, pointTarget):
        for idx, point in enumerate(self.points):
            if point.id == pointTarget.id:
                return idx
        return -1

    def addPoint(self, point):
        self.points.append(point)
        point.parentBranch = self
        return len(self.points) - 1

    def insertPointBefore(self, point, index):
        self.points.insert(index, point)
        point.parentBranch = self
        return index

    def removePointLocally(self, point):
        if point not in self.points:
            print ("Deleting point not in the branch? Whoops")
            return
        index = self.points.index(point)
        self.points.remove(point)
        return self.parentPoint if index == 0 else self.points[index - 1]

    def setParentPoint(self, parentPoint):
        self.parentPoint = parentPoint
        self.parentPoint.children.append(self)

@attr.s
class Tree():
    # Soma, initial start of the main branch.
    rootPoint = attr.ib(default=None, metadata=SAVE_META)

    # All branches making up this dendrite tree.
    branches = attr.ib(default=attr.Factory(list), metadata=SAVE_META)

    # HACK - make faster, index points by ID
    def getPointByID(self, pointID):
        for point in self.flattenPoints():
            if point.id == pointID:
                return point
        return None

    def getBranchByID(self, branchID):
        for branch in self.branches:
            if branch.id == branchID:
                return branch
        return None

    def addBranch(self, branch):
        self.branches.append(branch)
        branch._parentTree = self
        return len(self.branches) - 1

    def removeBranch(self, branch):
        if branch not in self.branches:
            print ("Deleting branch not in the tree? Whoops")
            return
        if len(branch.points) > 0:
            print ("Removing a branch that still has stuff on it? use uiState.removeBranch.")
            return
        self.branches.remove(branch)

    def removePointByID(self, pointID):
        pointToRemove = self.getPointByID(pointID)
        if pointToRemove is not None:
            return pointToRemove.parentBranch.removePointLocally(pointToRemove)
        else:
            return None

    def movePoint(self, pointID, newLocation, moveDownstream):
        pointToMove = self.getPointByID(pointID)
        assert pointToMove is not None, "Trying to move an unknown point ID"
        delta = util.locationMinus(newLocation, pointToMove.location)
        if moveDownstream:
            self._recursiveMovePointDelta(pointToMove, delta)
        else:
            # Non-recursive, so just move this one point:
            pointToMove.location = newLocation

    def _recursiveMovePointDelta(self, point, delta):
        point.location = util.locationPlus(point.location, delta)
        # First, move any branches coming off this point, by moving their first point
        for branch in self.branches:
            if branch.parentPoint.id == point.id and len(branch.points) > 0:
                self._recursiveMovePointDelta(branch.points[0], delta)
        # Next, move the next point on this branch (which will recursively do likewise...)
        if point.parentBranch is not None:
            nextIdx = point.parentBranch.indexForPoint(point) + 1
            assert nextIdx > 0, "Moving a point on a branch that doesn't know the point is there?"
            if nextIdx < len(point.parentBranch.points):
                self._recursiveMovePointDelta(point.parentBranch.points[nextIdx], delta)

    def flattenPoints(self):
        if self.rootPoint is None:
            return []
        result = [self.rootPoint]
        for branch in self.branches:
            result.extend(branch.points)
        return result

    def closestPointTo(self, targetLocation, zFilter=False):
        # TODO - need to fix for world coordinates?
        closestDist, closestPoint = None, None
        for point in self.flattenPoints():
            if zFilter and point.location[2] != targetLocation[2]:
                continue
            dist = util.deltaSz(targetLocation, point.location)
            if closestDist is None or dist < closestDist:
                closestDist, closestPoint = dist, point
        return closestPoint

    def worldCoordPoints(self, points):
        SCALE = [0.3070, 0.3070, 1.5] # HACK: Store in state instead
        x = [p.location[0] * SCALE[0] for p in points]
        y = [p.location[1] * SCALE[1] for p in points]
        z = [p.location[2] * SCALE[2] for p in points]
        return x, y, z


#
# Debug formatting for converting trees to string representation
#
def printPoint(tree, point, pad="", isFirst=False):
    print (pad + ("-> " if isFirst else "   ") + str(point))
    pad = pad + "   "
    for branch in tree.branches:
        if branch.parentPoint == point:
            printBranch(tree, branch, pad)

def printBranch(tree, branch, pad=""):
    if branch.points[0] == branch.parentPoint:
        print ("BRANCH IS OWN PARENT? :(")
        return
    print (pad + "-> Branch " + branch.id + " = ")
    for point in branch.points:
        printPoint(tree, point, pad)

def printTree(tree):
    printPoint(tree, tree.rootPoint)
