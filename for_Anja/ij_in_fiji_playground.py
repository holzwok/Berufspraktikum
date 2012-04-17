from ij import IJ
from ij.io import FileSaver
from ij.process import ImageStatistics as IS
import os
from os import path

imp = IJ.getImage()
fs = FileSaver(imp)

# Print image details
print "width:", imp.width
print "height:", imp.height
print "number of pixels:", imp.width * imp.height

# Get its ImageProcessor
ip = imp.getProcessor()

options = IS.MEAN | IS.MEDIAN | IS.MIN_MAX
stats = IS.getStatistics(ip, options, imp.getCalibration())

# print statistics on the image
print "Mean:", stats.mean
print "Median:", stats.median
print "Min and max:", stats.min, "-", stats.max
          
# Grab currently active image
imp = IJ.getImage()
ip = imp.getProcessor().convertToFloat()
pixels = ip.getPixels()

# Compute the mean value (sum of all divided by number of pixels)
#mean = reduce(lambda a, b: a + b, pixels) / len(pixels)

# Get a list of pixels above the mean
pix_above = filter(lambda a: a==stats.mean, pixels)

print "pixels with max. value:", pix_above



'''
# A known folder to store the image at:
folder = "/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/for_Anja"

# Test if the folder exists before attempting to save the image:
if path.exists(folder) and path.isdir(folder):
    print "folder exists:", folder
    filepath = folder + "/" + "testpic.tif"
    if path.exists(filepath):
        print "File exists! Not saving the image, would overwrite a file!"
    elif fs.saveAsTiff(filepath):
        print "File saved successfully at ", filepath
else:
	print "Folder does not exist or it's not a folder!"
'''       