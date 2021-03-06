import numpy as np
import scipy.io as sio

from pydynamo_brain.model import *
from pydynamo_brain.util import deltaSz

# Read a single branch from the matlab arrays containing per-point data
def parseMatlabBranch(fullState, pointsXYZ, annotations):
    branch = Branch(id=fullState.nextBranchID())
    for xyz, annotation in zip(pointsXYZ, annotations):
        assert xyz.shape == (3,)
        xyz = xyz - 1 # Matlab uses 1-based indices
        nextPoint = Point(
            id = fullState.nextPointID(),
            location = tuple(xyz * 1.0),
            annotation = ("" if len(annotation) == 0 else annotation[0])
        )
        branch.addPoint(nextPoint)
    return branch

# Read transform definition from the stack info
def parseTransform(infoState):
    t = Transform()
    if infoState.shape == (1,):
        infoState = infoState[0]
    t.rotation = infoState['R'][0][0].tolist()
    t.translation = infoState['offset'][0][0].T[0].tolist()
    t.scale = (infoState['xres'][0][0][0][0], infoState['yres'][0][0][0][0], infoState['zres'][0][0][0][0])
    return t

# Read a single tree, by reading in all its branches and hooking them up
def parseMatlabTree(fullState, saveState, removeOrphanBranches=True):
    tree = Tree()
    branchList = saveState['tree'][0]
    if branchList.shape == (1,):
        branchList = branchList[0]

    for i in range(branchList.shape[1]):
        # HACK: Matlab uses branch index as ID:
        fullState._nextBranchID = i

        if len(branchList[0, i]) > 0:
            # Load in branch:
            branchData = branchList[0, i][0]
            branch = parseMatlabBranch(fullState,
                branchData[0].T,  # XYZ position
                branchData[2][0], # Annotations
            )

            # ... and remove first point as it is duplicated data from parent:
            rootPoint = branch.points[0]
            branch.removePointLocally(rootPoint)
            branch.setParentPoint(rootPoint)
            if i == 0: # First branch is special, as first node is tree root
                tree.rootPoint = rootPoint
                tree.rootPoint.parentBranch = None
        else:
            # No branch data? Not sure what caused this in matlab...
            branch = Branch(fullState.nextBranchID())
        tree.addBranch(branch)

    # For each point, hook up its child branches to it:
    for i in range(branchList.shape[1]):
        if len(branchList[0, i]) > 0:
            childListForPoints = branchList[0, i][0][1][0] # Child index list
            for j, childListForPoint in enumerate(childListForPoints):
                for childIdx in np.nditer(childListForPoint, ['refs_ok', 'zerosize_ok']):
                    if tree.branches[childIdx - 1].parentPoint is not None:
                        oldParent = tree.branches[childIdx - 1].parentPoint
                        newParent = tree.branches[i].points[j - 1]
                        moved = deltaSz(oldParent.location, newParent.location)
                        if moved > 0.01:
                            print("WARNING: Branch %d parent location has moved %f" % (childIdx - 1, moved))
                            print("%s to %s" % (
                                str(tree.branches[childIdx - 1].parentPoint.location),
                                str(tree.branches[i].points[j - 1].location)
                            ))
                            # HACK - add branch to children of parent, but keep old parent on branch
                            tree.branches[i].points[j - 1].children.append(tree.branches[childIdx - 1])
                            tree.branches[childIdx - 1].reparentTo = tree.branches[i].points[j - 1]
                            continue
                    tree.branches[childIdx - 1].setParentPoint(tree.branches[i].points[j - 1])

    if removeOrphanBranches:
        tree.branches = [b for b in tree.branches if b.parentPoint is not None]

    tree.transform = parseTransform(saveState['info'][0])
    return tree

# Load an existing dynamo matlab file, and convert it into the python dynamo format.
def importFromMatlab(matlabPath, removeOrphanBranches=True):
    fullState = FullState()
    filePaths, treeData = [], []

    mat = sio.loadmat(matlabPath)
    saveStates = None
    if 'saved' in mat.keys():
        # Original microscope code
        saveStates = mat['saved'][0]['Dynamo'][0]['state'][0][0]
    elif 'savedata' in mat.keys():
        # Just matlab dynamo code
        saveStates = mat['savedata'][0]['state'][0]
    else:
        raise Exception("Unrecognized matlab content")

    for i in range(saveStates.shape[1]):
        saveState = saveStates[0, i][0]
        filePath = saveState['info'][0]['filename'][0][0][0]
        filePaths.append(filePath)
        tree = parseMatlabTree(fullState, saveState, removeOrphanBranches)
        # Note: Pull out scale from transform, move it to global scale:
        fullState.projectOptions.pixelSizes = tree.transform.scale
        tree.transform.scale = (1, 1, 1)
        treeData.append(tree)
    fullState.addFiles(filePaths, treeData)
    return fullState
