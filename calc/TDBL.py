import util

# Calculate total dendritic branch length for a dendritic arbor.
def TDBL(tree,
    excludeAxon=True,
    excludeBasal=True,
    includeFilo=True,
    filoDist=10
):
    if tree.rootPoint:
        return _tdblPoint(tree.rootPoint, excludeAxon, excludeBasal, includeFilo, filoDist)
    return 0

# TDBL for a single point, calculated as the TDBL of children off it.
def _tdblPoint(point, excludeAxon, excludeBasal, includeFilo, filoDist):
    totalLength = 0
    for childBranch in point.children:
        totalLength += _tdblBranch(childBranch, excludeAxon, excludeBasal, includeFilo, filoDist)
    return totalLength

# TDBL of a branch, the TDBL for all children plus length along the branch.
# Optional filters can be applied to remove parts based on annotations.
def _tdblBranch(branch, excludeAxon, excludeBasal, includeFilo, filoDist):
    pointsWithRoot = [branch.parentPoint] + branch.points

    # 1) If the branch has not been created yet, or is empty, abort
    if len(pointsWithRoot) < 2:
        return 0
    # 2) If the branch contains an 'axon' label, abort
    if excludeAxon and _lastPointWithLabel(pointsWithRoot, 'axon') >= 0:
        return 0
    # 3) If the branch is a basal dendrite, abort
    if excludeBasal and _lastPointWithLabel(pointsWithRoot, 'basal') >= 0:
        return 0

    # Add all the child branches...
    totalLength = 0
    for point in branch.points:
        totalLength += _tdblPoint(point, excludeAxon, excludeBasal, includeFilo, filoDist)

    # ... then remove any points up to and including the last point marked 'soma'
    somaIdx = _lastPointWithLabel(pointsWithRoot, 'soma')
    if somaIdx >= 0:
        pointsWithRoot = pointsWithRoot[somaIdx+1:]

    # ... and find the last branchpoint
    lastChild = _lastPointWithChildren(pointsWithRoot)

    # ... then measure distances up to and past branch point.
    x, y, z = branch._parentTree.worldCoordPoints(pointsWithRoot)
    totalDist = 0
    toLastBranchDist = 0
    for i in range(len(pointsWithRoot) - 1):
        locA = (x[i  ], y[i  ], z[i  ])
        locB = (x[i+1], y[i+1], z[i+1])
        pointDist = util.deltaSz(locA, locB)
        totalDist += pointDist
        if i < lastChild:
            toLastBranchDist += pointDist

    # Use full distance only if including filo, or it's large enough:
    if includeFilo or (totalDist - toLastBranchDist) > filoDist:
        totalLength += totalDist
    else:
        totalLength += toLastBranchDist
    return totalLength

# Return the index of the last point whose label contains given text, or -1 if not found.
def _lastPointWithLabel(points, label):
    lastPointIdx = -1
    for i, point in enumerate(points):
        if point.annotation.find(label) != -1:
            lastPointIdx = i
    return lastPointIdx

# Return the index of the last point with child branches, or -1 if not found.
def _lastPointWithChildren(points):
    lastPointIdx = -1
    for i, point in enumerate(points):
        if len(point.children) > 0:
            lastPointIdx = i
    return lastPointIdx
