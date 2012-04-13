from ij import IJ
from ij.process import ImageStatistics as IS

imp = IJ.getImage()
ip = imp.getProcessor().convertToFloat()
pixels = list(ip.getPixels())
print type(pixels)
print pixels[11000:11100]
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
print "width:", imp.width
print "height:", imp.height
print "number of pixels:", imp.width * imp.height
print "number of slices:", imp.getNSlices()
print "number of channels:", imp.getNChannels()
print "number of time frames:", imp.getNFrames()

types = {ImagePlus.COLOR_RGB : "RGB",
         ImagePlus.GRAY8 : "8-bit",
         ImagePlus.GRAY16 : "16-bit",
         ImagePlus.GRAY32 : "32-bit",
         ImagePlus.COLOR_256 : "8-bit color"}

print "image type:", types[imp.type]

print "pixels with max. value:", all_indices(stats.max, pixels)
