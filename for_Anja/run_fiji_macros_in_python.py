from ij.gui import ProfilePlot

# Obtain current image
img = IJ.getImage()

imp = img.createImagePlus()
width  = imp.width
height = imp.height

ip = imp.getProcessor() #.duplicate()
print ip

#pixels = ip.getPixels()
 
types = {ImagePlus.COLOR_RGB : "RGB",  
         ImagePlus.GRAY8 : "8-bit",  
         ImagePlus.GRAY16 : "16-bit",  
         ImagePlus.GRAY32 : "32-bit",  
         ImagePlus.COLOR_256 : "8-bit color"}  
  
print "image type:", types[imp.type]  

line = IJ.makeLine(222, 100, 315, 412)
line = Line(222, 100, 315, 412)
#fp = FloatProcessor(width, height, pixels, None)
#ip.setRoi(line)

#test = ProfilePlot(imp) #.getProfile()

#IJ.run(imp, "Plot Profile", "") # geht fast
 
imp.show()
print "OK"
