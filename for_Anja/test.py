from dircache import listdir
from os.path import join
from ij import IJ
from ij.process import ImageStatistics as IS
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

def open_image(imagename):
    imp = IJ.openImage(imagename)
    imp.show()
    return imp

def brightest_pixels(imp):
    ip = imp.getProcessor().convertToFloat()
    pixels = ip.getPixels() # type 'array'
    options = IS.MEAN | IS.MEDIAN | IS.MIN_MAX
    stats = IS.getStatistics(ip, options, imp.getCalibration())
    # Print image details
    #print "number of slices:", imp.getNSlices()
    #print "number of channels:", imp.getNChannels()
    #print "number of time frames:", imp.getNFrames()
    brightestpixellist = all_indices(stats.max, list(pixels))
    #print "pixels with max. value:", brightestpixellist
    for bp in brightestpixellist:
        x = bp % imp.width
        y = bp / imp.width
    #print "max. brightness coordinates:", x, y
    # note that this chooses for x, y the last element in the brightestpixelist which is OK if there is only one element
    # TODO: would be nicer to loop over this list or specify which element to pick
    return x, y

def fetch_profile(imagename, ip, alpha, length, x, y):
    vecx, vecy = length * cos(alpha * pi/180), length * sin(alpha * pi/180)
    roi = Line(x-vecx, y-vecy, x+vecx, y+vecy)

    myimp = ImagePlus("Profile_"+imagename+str(alpha), ip)
    myimp.setRoi(roi)
    #ip.draw(roi) # enabling this creates artifacts - careful!

    # create ProfilePlot
    profplot = ProfilePlot(myimp)
    profplot.createWindow()  # enabling this creates a nice animation
    # get the data
    profarray = profplot.getProfile()
    return profarray

def smoothed_max_positions(profarray, win=10):
    # smooth the data by calculating moving average
    movavg = moving_average(profarray, win)
    medi = median(movavg)
    print "median of profile:", medi

    # determine maximum
    maxpositions = []
    for pos, point in enumerate(movavg):
        if point > 2.0*medi:
            if movavg[pos] > movavg[pos-1] and movavg[pos] > movavg[pos+1]:
                #print "local maximum at angle", alpha, "position", pos, "." 
                unsmoothed_max = max(profarray[pos:pos+win])
                unsmoothed_pos = [x for x in range(pos,pos+win) if profarray[x]==unsmoothed_max]
                #print unsmoothed_pos, unsmoothed_max#, profarray[pos:pos+win]
                maxpositions.append(unsmoothed_pos)
    print "maxpositions =", maxpositions
    return maxpositions

def measure_width(imp, x, y, angular_accuracy=5):
    '''measures width of tube at point x, y'''
    print "measuring width of", imp.title, "..."
    width = imp.width
    height = imp.height
    tubewidth = width # to initialize, a tube cannot be wider than the whole image
    length = 400/2

    print "done."


if __name__=="__main__":
    imagepath = "C:/Users/MJS/git/Berufspraktikum/for_Anja"
    
    filelist = listdir(imagepath)
    for imagename in filelist:
        if imagename.endswith("1.tif"): # FIXME
            imp = open_image(join(imagepath, imagename)) # type 'ij.ImagePlus', current image
            ip = imp.getProcessor().convertToFloat()     # type 'ij.ImageProcessor'
            x, y = brightest_pixels(imp)
    
            length = 400/2 # length of intensity profile
            angular_accuracy = 30 # degrees
            for alpha in range(0, 180, angular_accuracy):
                profarray = fetch_profile(imagename, ip, alpha, length, x, y)
                #print profarray
                print "alpha =", alpha
                maxpositions = smoothed_max_positions(profarray)
                #print imagename, alpha, maxpositions

            measure_width(imp, x, y)
            