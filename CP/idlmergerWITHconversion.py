# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport

mskpath = "//Ts412-molbp/shared/Aouefa/mRNA/mask"
locpath = "//Ts412-molbp/shared/Aouefa/mRNA/loc"
maskfilename_token = "cln2"
locfilename_token = ".loc"
spotoutfile = "all_spots_within_cells.loc"

def extract_id(filename):
    return filename.split("_")[-2:-1][0]

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
    print intensities
    med = median(intensities)
    print "median intensity of", len(intensities), "detected spots is", med, "."
    RNA = [int(0.5+intensity/med) for intensity in intensities]
    return RNA

def create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, spotoutfile):
    print "creating spotfile..."
    lout = listdir(mskpath)
    lin  = listdir(locpath)
    spot_ID = 0
    intensities = []
    outfilelines = []

    with open(join(locpath, spotoutfile), 'w') as f:
        f.write("\t".join(["x", "y", "intensity", "frame_ID", "cell_ID", "spot_ID", "file_ID", "mRNA"]))
        f.write("\n")
        for infilename in lout:
            if infilename.startswith(maskfilename_token):
                mask = Image.open(join(mskpath, infilename)).convert("RGB")
                maskpixels = mask.load()
                #mask.show()
                colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
                colordict = dict(enumerate(colorlist))    
                inverse_colordict = dict((v,k) for k, v in colordict.items())
                #print inverse_colordict
                for locfilename in lin:
                    if locfilename.endswith(locfilename_token):
                        if extract_id(locfilename)==extract_id(infilename): # for matching image IDs
                            for spot in loc_spots(join(locpath, locfilename)):
                                x = spot[0]
                                y = spot[1]
                                intensity = spot[2]
                                frame_ID = spot[3]
                                cell_ID = inverse_colordict[maskpixels[spot[0], spot[1]]] # cell_ID but also color_ID
                                file_ID = extract_id(locfilename)
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
            f.write(outfileline)
    print "done."

if __name__ == '__main__':
    create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, spotoutfile)

