# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport
import fileinput

mskpath = "C:/Users/MJS/git/Berufspraktikum/CP/mask"
locpath = "C:/Users/MJS/git/Berufspraktikum/CP/"
maskfilename_token = "CLB5"
locfilename_token = ".loc"
spotoutfile = "all_spots_within_cells.loc" # "all_spots_within_cells.loc" file is created in loc folder
celloutfile = "all_cells.txt" # is also created in loc folder

def extract_loc_id(filename):
    return filename.split("_")[-2:-1][0] # index btwn 2nd and 1st "_" from the right

def extract_msk_id(filename):
    return filename.split("_")[-4:-3][0] # index btwn 4th and 3th "_" from the right

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

def create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, spotoutfile):
    print "creating spotfile..."
    lout = listdir(mskpath)
    lin  = listdir(locpath)
    intensities = []
    outfilelines = []

    with open(join(locpath, spotoutfile), 'w') as f:
        f.write("\t".join(["x", "y", "intensity", "frame_ID", "cell_ID", "spot_ID", "file_ID", "mRNA"]))
        f.write("\n")
        for infilename in lout:
            if maskfilename_token in infilename:
                mask = Image.open(join(mskpath, infilename)).convert("RGB")
                maskpixels = mask.load()
                #mask.show()
                colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
                colordict = dict(enumerate(colorlist))    
                inverse_colordict = dict((v,k) for k, v in colordict.items())
                #print inverse_colordict
                for locfilename in lin:
                    if locfilename.endswith(locfilename_token):
                        if extract_loc_id(locfilename)==extract_msk_id(infilename): # for matching image IDs
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
                                    intensities.append(intensity) # this is the "global" intensities
                                    writelist = [str(i) for i in [x, y, intensity, frame_ID, cell_ID, spot_ID, file_ID]]
                                    outfileline = "\t".join(writelist)
                                    outfilelines.append(outfileline)
                                    #print outfileline
        RNAs = calculate_RNA(intensities)
        for i, outfileline in enumerate(outfilelines):
            outfileline = outfileline+"\t"+str(RNAs[i])+"\n"
            #print outfileline,
            f.write(outfileline)
    print "done."


def create_cellfile(locpath, spotoutfile, celloutfile):
    print "creating cellfile..."
    celldict = {}
    cell_IDs = set()
    data = []
    with open(join(locpath, spotoutfile), 'r') as f:
        for i, line in enumerate(f):
            if i:
                linedata = line.split()
                data.append(linedata)
                cell_ID = str(linedata[6])+"."+str(linedata[4])
                celldict[cell_ID] = [0.0, 0, 0] # intensity, spots, RNAs
                cell_IDs.add(cell_ID)

    for ID in cell_IDs:
        celldict[ID][0] = str(sum(float(linedata[2]) for linedata in data if str(linedata[6])+"."+str(linedata[4])==ID)) # intensities
        celldict[ID][1] = str(sum(int(linedata[5]) for linedata in data if str(linedata[6])+"."+str(linedata[4])==ID)) # spots
        celldict[ID][2] = str(sum(int(linedata[7]) for linedata in data if str(linedata[6])+"."+str(linedata[4])==ID)) # RNAs

    with open(join(locpath, celloutfile), 'w') as f:
        print "writing to", join(locpath, celloutfile)
        f.write("\t".join(["cell_ID", "number_of_spots", "total_intensity", "total_mRNA"]))
        f.write("\n")
        outfileline = ""
        for ID in cell_IDs:
            outfileline += ID+"\t"+"\t".join(celldict[ID])+"\n"
        f.write(outfileline)
    print "done."

if __name__ == '__main__':
    create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, spotoutfile)
    create_cellfile(locpath, spotoutfile, celloutfile)
