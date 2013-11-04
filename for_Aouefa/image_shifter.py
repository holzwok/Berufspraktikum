import numpy
import os
import tifffile as tff

from dircache import listdir
from Tkinter import Tk
from tkFileDialog import askdirectory
    
        
def shift(file, shift_x, shift_y):
    fullname = os.path.join(dirname, file)
    print "shifting image", fullname
    
    tiffimg = tff.TIFFfile(fullname)
    img = tiffimg.asarray()
    img = numpy.roll(img, shift_x, axis=1)
    img = numpy.roll(img, shift_y, axis=2)

    shiftedname = os.path.join(dirname, "shifted_"+file)
    tff.imsave(shiftedname, img)

        
if __name__=="__main__":
    x = int(input("Enter x shift: "))
    y = int(input("Enter y shift: "))
    
    reference = str(raw_input("Enter reference token for files that are not shifted (enter <space> to keep BF as reference): "))
    if reference.isspace() or not reference:
        reference = "BF"

    #dirname = "/home/basar/shared/20130808_Alignment_BF_fluo"
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    dirname = askdirectory(title='Choose directory with .tif files') # show an "Open" dialog box and return the path to the selected file
    
    l = listdir(dirname)
    
    files_to_shift = [filename for filename in l if reference not in filename]
    
    for shiftme in files_to_shift:
        shift(shiftme, x, y) 