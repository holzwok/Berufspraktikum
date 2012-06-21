from dircache import listdir
from os.path import join
from ij import IJ
from ij.process import ImageStatistics as IS
from math import cos, sin, pi
import shelve

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
    #profplot.createWindow()  # enabling this creates a nice animation
    # get the data
    profarray = profplot.getProfile()
    return profarray

def max_positions(profarray, win=20):
    # smooth the data by calculating moving average
    movavg = moving_average(profarray, win)
    medi = median(movavg)
    print "median of profile:", medi

    # determine maximum
    maxpositions = dict() # will be dict(position:intensity) of maxima
    for pos, point in enumerate(movavg):
        if point > 1.5*medi and pos+win<len(profarray):
            if movavg[pos] > movavg[pos-1] and movavg[pos] > movavg[pos+1]: # this defines a maximum
                #print "local maximum at angle", alpha, "position", pos, "." 
                unsmoothed_max = max(profarray[pos-win/2:pos+win/2])
                unsmoothed_pos = [x for x in range(pos-win/2,pos+win/2) if profarray[x]==unsmoothed_max][0] # hack since there might be more than one pos with the max
                #print unsmoothed_pos, unsmoothed_max 
                maxpositions[unsmoothed_pos] = unsmoothed_max # hack because the list can have > 1 element
    #print "maxpositions =", maxpositions
    topvalues = sorted(maxpositions.values())[-2:] # top 2 intensities
    maxpositions = dict((k, v) for (k, v) in maxpositions.items() if v in topvalues) # dictionary with only <=2 largest
    return maxpositions.keys()


if __name__=="__main__":
    imagepath = "C:/Users/MJS/git/Berufspraktikum/for_Anja"
    
    filelist = listdir(imagepath)
    for imagename in filelist:
        if imagename.endswith(".tif"):
            print "opening image:", join(imagepath, imagename)
            imp = open_image(join(imagepath, imagename)) # type 'ij.ImagePlus', current image
            ip = imp.getProcessor().convertToFloat()     # type 'ij.ImageProcessor'
            x, y = brightest_pixels(imp)
            width = imp.width
    
            length = 400/2 # length of intensity profile
            angular_accuracy = 20 # degrees
            tubewidth = width # to initialize, a tube cannot be wider than the whole image
            filename = join(imagepath, imagename+"_profiles.shl")
            profiles = shelve.open(filename, 'n')
            for alpha in range(0, 180, angular_accuracy):
                profarray = fetch_profile(imagename, ip, alpha, length, x, y)
                #print profarray
                profiles[str(alpha)] = profarray
                #maxpositions = max_positions(profarray)
                #print imagename, maxpositions
                #if len(maxpositions)==2:
                #    if abs(maxpositions[1]-maxpositions[0]) < tubewidth:
                #        tubewidth = abs(maxpositions[1]-maxpositions[0])
                #        print "updated tubewidth:", tubewidth
            #print "final tubewidth for image", imagename,":", tubewidth
            profiles.close()
    print "done."
