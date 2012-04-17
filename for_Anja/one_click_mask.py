# 1 - Obtain an image
blobs = IJ.getImage()
# Make a copy with the same properties as blobs image:
imp = blobs.createImagePlus()
ip = blobs.getProcessor().duplicate()
print "OK"
imp.setProcessor("Mask", ip)
 
# 2 - Apply a threshold: only zeros and ones
# Set the desired threshold range: keep from 0 to 74
ip.setThreshold(147, 147, ImageProcessor.NO_LUT_UPDATE)
# Call the Thresholder to convert the image to a mask
IJ.run(imp, "Convert to Mask", "")
 
# 3 - Apply watershed
# Create and run new EDM object, which is an Euclidean Distance Map (EDM)
# and run the watershed on the ImageProcessor:
#EDM().toWatershed(ip)
 
# 4 - Show the watersheded image:
imp.show()