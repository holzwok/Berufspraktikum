from ij import IJ
from ij.process import ImageStatistics as IS
from ij.gui import Roi, Line  
from ij.process import FloatProcessor
from math import cos, sin, pi

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

def moving_average(data, win):
	if not win%2: # even
		return [sum(data[x-win/2:x+win/2])/win for x in range(win/2, len(data)-win/2+1)]
	else:         # odd
		return [sum(data[x-(win-1)/2:x+(win+1)/2]/win) for x in range((win-1)/2, len(data)-(win+1)/2+1)]

def median(numericValues):
	theValues = sorted(numericValues)
	if len(theValues)%2 == 1:
		return theValues[(len(theValues)+1)/2-1]
	else:
		lower = theValues[len(theValues)/2-1]
		upper = theValues[len(theValues)/2]
	return (float(lower + upper))/2  


imp = IJ.getImage()
ip = imp.getProcessor().convertToFloat() # type 'ij.ImagePlus'
pixels = ip.getPixels()			 # type 'array'

options = IS.MEAN | IS.MEDIAN | IS.MIN_MAX
stats = IS.getStatistics(ip, options, imp.getCalibration())

# Print image details
print "considering image:", imp.title
width  = imp.width
height = imp.height
#print "number of slices:", imp.getNSlices()
#print "number of channels:", imp.getNChannels()
#print "number of time frames:", imp.getNFrames()
tubewidth = width # to initialize, a tube cannot be wider than the whole image

brightestpixellist = all_indices(stats.max, list(pixels))
#print "pixels with max. value:", brightestpixellist

for bp in brightestpixellist:
	x = bp%imp.width
	y = bp/imp.width
	#print "max. brightness coordinates:", x, y

# note that the following chooses for x, y the last element in the brightestpixelist which is OK if there is only one element
# TODO: would be nicer to loop over this list or specify which element to pick

length = 400/2
angular_accuracy = 5 # degrees

for alpha in range(0, 180, angular_accuracy):
	myimp = ImagePlus("Profile_"+str(alpha), ip)
	vecx, vecy = length * cos(alpha * pi/180), length * sin(alpha * pi/180)
	roi = Line(x-vecx, y-vecy, x+vecx, y+vecy)
	myimp.setRoi(roi)
	#ip.draw(roi) # enabling this creates artifacts - careful!

	# create ProfilePlot
	profplot = ProfilePlot(myimp)
	#profplot.createWindow()  # enabling this creates a nice animation
	#print alpha, sum(profplot.getProfile())/len(profplot.getProfile()) # test: average of profile values as proxy for brightness

	# get the data
	profarray = profplot.getProfile()

	# smooth the data by calculating moving average
	win = 12 # window size for moving average, must be even
	movavg = moving_average(profarray, win)
	medi = median(movavg)
	#print "median of profile:", medi

	# determine maximum
	maxpositions = []
	for pos, point in enumerate(movavg):
		if point > 1.5*medi:
			if movavg[pos] > movavg[pos-1] and movavg[pos] > movavg[pos+1]:
				#print "local maximum at angle", alpha, "position", pos, "." 
				maxpositions.append(pos)
	#print "maxpositions =", maxpositions
	if len(maxpositions)==2:
		tubewidth = min(tubewidth, abs(maxpositions[1] - maxpositions[0]))
	
	# create plot
	#plot = Plot("alpha = "+str(alpha), "xlabel", "ylabel", range(win/2-1, len(movavg)-win/2), movavg)
	#plot.show()

print "width =", tubewidth, "pixels."
#ImagePlus("Profile", ip).show()
