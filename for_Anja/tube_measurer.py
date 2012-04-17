from ij import IJ
from ij.process import ImageStatistics as IS
from ij.gui import Roi, Line  
from ij.process import FloatProcessor
from math import cos, sin, pi

imp = IJ.getImage()
ip = imp.getProcessor().convertToFloat() # type 'ij.ImagePlus'
pixels = ip.getPixels()			 		 # type 'array'

options = IS.MEAN | IS.MEDIAN | IS.MIN_MAX
stats = IS.getStatistics(ip, options, imp.getCalibration())

def all_indices(value, qlist):
	# returns list of indices of elements in qlist that have value
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
#print "number of slices:", imp.getNSlices()
#print "number of channels:", imp.getNChannels()
#print "number of time frames:", imp.getNFrames()

brightestpixellist = all_indices(stats.max, list(pixels))
#print "pixels with max. value:", brightestpixellist

for bp in brightestpixellist:
    x = bp%imp.width
    y = bp/imp.width
    print x, y

fp = FloatProcessor(width, height, pixels, None)
ip.setValue(8000.0)

# note that the following chooses for x, y the last element in the brightestpixelist
# TODO: nicer would be to loop over this list or somehow specify which element to pick

length = 400/2
for alpha in range(0, 180, 10):
	myimp = ImagePlus("bla_"+str(alpha), ip)
	vecx, vecy = length * cos(alpha * pi/180), length * sin(alpha * pi/180)
	roi = Line(x+vecx, y+vecy, x-vecx, y-vecy)
	myimp.setRoi(roi)
	#ip.draw(roi) # enabling this creates artifacts - careful!
	proplot = ProfilePlot(myimp)
	proplot.createWindow()  # enabling this creates a nice animation
	print alpha, sum(proplot.getProfile())/len(proplot.getProfile()) # test: average of profile values as proxy for brightness
	#print proplot.getProfile()[0:10]

ImagePlus("Profile", ip).show()
