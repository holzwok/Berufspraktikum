from ij import IJ
from ij.io import FileSaver
from os import path

imp = IJ.getImage()
fs = FileSaver(imp)

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
          