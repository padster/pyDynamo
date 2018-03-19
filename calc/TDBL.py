"""
.. module:: analysis
"""

import util

def TDBL(tree,
    excludeAxon=True,
    excludeBasal=True,
    includeFilo=True,
    filoDist=10
):
    """Calculate total dendritic branch length for a dendritic arbor.

    :param tree: Tree model to calculate TDBL for.
    :param excludeAxon: Whether Axon lengths should be ignored.
    :param excludeAxon: Whether Basal dendrites should be ignored.
    :param includeFilo: Whether Filo lengths should be included.
    :param filoDist: Maximum length to be considered a Filo.
    """
    if not tree.rootPoint:
        return 0
    return _tdblPoint(tree.rootPoint, excludeAxon, excludeBasal, includeFilo, filoDist)


def _tdblPoint(point, excludeAxon, excludeBasal, includeFilo, filoDist):
    """Calculate TDBL for a single point, defined as the sum of TDBL of children off it.

    :param point: The point model to calculate TDBL for."""
    return sum([
        _tdblBranch(child, excludeAxon, excludeBasal, includeFilo, filoDist) for child in point.children
    ])


def _tdblBranch(branch, excludeAxon, excludeBasal, includeFilo, filoDist):
    """TDBL of a branch, which is the TDBL for children plus length along the branch.

    :param branch: The branch model to calculate TDBL for."""
    # If the branch is 1) Empty, or 2) Axon and 3) Basal when desired, skip
    if branch.isEmpty() or (excludeAxon and branch.isAxon()) or (excludeBasal and branch.isBasal()):
        return 0

    # Add all the child branches...
    tdblLength = sum([
        _tdblPoint(point, excludeAxon, excludeBasal, includeFilo, filoDist) for point in branch.points
    ])

    # ... then remove any points up to and including the last point marked 'soma'
    pointsWithRoot = [branch.parentPoint] + branch.points
    somaIdx = util.lastPointWithLabelIdx(pointsWithRoot, 'soma')

    # ... measure distance for entire branch, and up to last branchpoint:
    totalLength, totalLengthToLastBranch = branch.worldLengths(fromIdx=(somaIdx+1))

    # Use full distance only if including filo, or if the end isn't a filo.
    if includeFilo or (totalLength - totalLengthToLastBranch) > filoDist:
        tdblLength += totalLength
    else:
        tdblLength += totalLengthToLastBranch
    return tdblLength
