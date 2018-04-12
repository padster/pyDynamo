import libtiff
import numpy as np

from tifffile import TiffFile

libtiff.libtiff_ctypes.suppress_warnings()

def asMatrix(asList, nRows):
    nCols = int(len(asList) / nRows)
    assert nRows * nCols == len(asList), "List wrong size for matrix conversion"
    return [asList[i:i+nCols] for i in range(0, len(asList), nCols)]

def tiffRead(path):
    # First use tifffile to get channel data (not supported by libtiff?)
    shape = None
    with TiffFile(path) as tif:
        shape = tif.asarray().shape
    nChannels = shape[0] if len(shape) == 4 else 1

    stack = []
    tif = libtiff.TIFF.open(path, mode='r')
    stack = asMatrix([np.array(img) for img in tif.iter_images()], nChannels)
    tif.close()
    ## MEGA HACK
    stack = np.array(stack)
    stack = np.swapaxes(stack, 0, 1)
    stack = list(stack)
    return stack
