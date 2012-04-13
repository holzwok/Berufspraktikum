from ij import IJ
from ij.process import ImageStatistics as IS
from ij.gui import Roi, Line, PolygonRoi  
from ij.process import FloatProcessor

imp = IJ.getImage()
ip = imp.getProcessor().convertToFloat() # type 'ij.ImagePlus'
pixels = ip.getPixels()			 # type 'array'
options = IS.MEAN | IS.MEDIAN | IS.MIN_MAX
stats = IS.getStatistics(ip, options, imp.getCalibration())

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

# Print image details
print "title:", imp.title
width  = imp.width
height = imp.height
print "number of slices:", imp.getNSlices()
print "number of channels:", imp.getNChannels()
print "number of time frames:", imp.getNFrames()
types = {ImagePlus.COLOR_RGB : "RGB",
         ImagePlus.GRAY8 : "8-bit",
         ImagePlus.GRAY16 : "16-bit",
         ImagePlus.GRAY32 : "32-bit",
         ImagePlus.COLOR_256 : "8-bit color"}
print "image type:", types[imp.type]

brightestpixellist = all_indices(stats.max, list(pixels))
print "pixels with max. value:", brightestpixellist

for bp in brightestpixellist:
    x = bp%imp.width
    y = bp/imp.width
    print x, y

# Fill a polygonal region of interest
# with a value of -3
xs = [234, 174, 162, 102, 120, 123, 153, 177, 171,
      60, 0, 18, 63, 132, 84, 129, 69, 174, 150,
      183, 207, 198, 303, 231, 258, 234, 276, 327,
      378, 312, 228, 225, 246, 282, 261, 252]
ys = [48, 0, 60, 18, 78, 156, 201, 213, 270, 279,
      336, 405, 345, 348, 483, 615, 654, 639, 495,
      444, 480, 648, 651, 609, 456, 327, 330, 432,
      408, 273, 273, 204, 189, 126, 57, 6]
proi = PolygonRoi(xs, ys, len(xs), Roi.POLYGON)
fp = FloatProcessor(width, height, pixels, None)  
fp.setRoi(proi)
fp.setValue(2)
fp.fill(proi.getMask())  # Attention!

imp.show()
