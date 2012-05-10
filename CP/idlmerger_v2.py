# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

mskpath = "C://Users//MJS//git//Berufspraktikum//CP//mask"
locpath = "C://Users//MJS//git//Berufspraktikum//CP"
maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
spotoutfile = "all_spots_within_cells.loc" # "all_spots_within_cells.loc" file is created in loc folder
celloutfile = "all_cells.txt" # is also created in loc folder

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport
import cPickle

def extract_loc_id(filename):
    return filename.replace(".loc", "")
    #filename.split("_")[-12:-1][0] # index btwn 12th and 1st "_" from the right

def extract_msk_id(filename):
    return filename.replace("_mask_cells.tif", "")
    #filename.split("_")[-14:-3][0] # index btwn 14th and 3th "_" from the right

def loc_spots(locfile):
    spotlist = []
    for line in open(locfile):
        spot = line.split()
        spot = [float(x) for x in spot] # x, y, intensity, frame ID
        spotlist.append(spot)
    return spotlist

def calculate_RNA(intensities):
    def median(numericValues):
        theValues = sorted(numericValues)
        if len(theValues) % 2 == 1:
            return theValues[(len(theValues)+1)/2-1]
        else:
            lower = theValues[len(theValues)/2-1]
            upper = theValues[len(theValues)/2]
        return (float(lower + upper)) / 2  
    med = median(intensities)
    print "median intensity of", len(intensities), "detected spots is", med, "."
    RNA = [int(0.5+intensity/med) for intensity in intensities]
    return RNA

def read_data():
    print "reading data..."
    intensities = []
    spotwritelist = []
    cellsperfile = []
    lout = listdir(mskpath)
    lin  = listdir(locpath)
    
    # read in spots data:
    for infilename in lout:
        if maskfilename_token in infilename:
            mask = Image.open(join(mskpath, infilename)).convert("RGB")
            maskpixels = mask.load()
            #mask.show()
            colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
            colordict = dict(enumerate(colorlist))    
            inverse_colordict = dict((v,k) for k, v in colordict.items())
            cellsperfile.append(len(colorlist)-1) # this is the number of cells in the image infilename
            for locfilename in lin:
                if locfilename.endswith(locfilename_token):
                    if extract_loc_id(locfilename)==extract_msk_id(infilename): # for matching image IDs
                        #print "Considering file", locfilename
                        for spot in loc_spots(join(locpath, locfilename)):
                            x = spot[0]
                            y = spot[1]
                            intensity = spot[2]
                            frame_ID = spot[3]
                            cell_ID = inverse_colordict[maskpixels[spot[0], spot[1]]] # cell_ID but also color_ID
                            spot_ID = 0 # move this line up to create a global spot_ID
                            file_ID = extract_loc_id(locfilename)
                            if cell_ID != 0: # excluding black (= outside of cells)
                                spot_ID += 1
                                intensities.append(intensity) # this is the "global" intensities list
                                spotwritelist.append([str(i) for i in [x, y, intensity, frame_ID, cell_ID, spot_ID, file_ID]])
    RNAs = calculate_RNA(intensities)
    for i, sublist in enumerate(spotwritelist):
        spotwritelist[i].append(str(RNAs[i]))
        #print spotwritelist[i]

    # create cells data structure (including spotless cells):
    cellsperfile = iter(cellsperfile)
    celldict = {}
    for infilename in lout:
        if maskfilename_token in infilename:
            for cellnumber in range(1, cellsperfile.next()+1):
                ID = infilename.replace("_mask_cells.tif", "")+"_"+str(cellnumber)
                celldict[ID] = [infilename.replace("_mask_cells.tif", ""), 0.0, 0, 0] # file_ID, intensity, spots, RNAs
                
    # read in cells data:
    for sublist in spotwritelist:
        ID = sublist[6]+"_"+sublist[4]
        celldict[ID][1] = str(sum(float(linedata[2]) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # intensities
        celldict[ID][2] = str(sum(int(linedata[5]) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # spots
        celldict[ID][3] = str(sum(int(linedata[7]) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # RNAs

    cPickle.dump(spotwritelist, file("spotlist.pkl", "w"))
    cPickle.dump(celldict, file("celldict.pkl", "w"))
    
def create_spotfile():
    spotwritelist = cPickle.load(file("spotlist.pkl"))
    with open(join(locpath, spotoutfile), 'w') as f:
        print "writing to", join(locpath, spotoutfile)
        f.write("\t".join(["x", "y", "intensity", "frame_ID", "cell_ID", "spot_ID", "file_ID", "mRNA"]))
        f.write("\n")
        for sublist in spotwritelist:
            nextline = "\t".join(sublist)
            f.write(nextline)
            f.write("\n")
    print "done."
                        
def create_cellfile():
    celldict = cPickle.load(file("celldict.pkl"))
    with open(join(locpath, celloutfile), 'w') as f:
        print "writing to", join(locpath, celloutfile)
        f.write("\t".join(["cell_ID", "total_intensity", "number_of_spots", "total_mRNA"]))
        f.write("\n")
        for ID in celldict:
            nextline = celldict[ID][0]+"\t"+ID+"\t"+"\t".join([str(elem) for elem in celldict[ID][1:]])+"\n"
            f.write(nextline)
    print "done."
    
if __name__ == '__main__':
    read_data()
    create_spotfile()
    create_cellfile()
