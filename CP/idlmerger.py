# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport

mskpath = "/home/basar/Personal/Martin_Seeger/CellProfiler_work/output"
locpath = "/home/basar/Personal/Martin_Seeger/CellProfiler_work/"
maskfilename_token = "MAX_"
locfilename_token = ".loc"
outfile = "all_spots_within_cells.loc"

def extract_id(filename):
    return filename.split("_")[-2:-1][0]

def loc_spots(locfile):
    spotlist = []
    for line in open(locfile):
        spot = line.split()
        spot = [float(x) for x in spot] # x, y, intensity, frame ID
        spotlist.append(spot)
    return spotlist

def create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, outfile):
    print "creating spotfile..."
    lout = listdir(mskpath)
    lin  = listdir(locpath)
    spot_ID = 0
    with open(join(locpath, outfile), 'w') as f:
        f.write("\t".join(["x", "y", "intensity", "frame_ID", "cell_ID", "spot_ID", "file_ID"]))
        f.write("\n")
        for infilename in lout:
            if infilename.startswith(maskfilename_token):
                mask = Image.open(join(mskpath, infilename))
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
                                    writelist = [str(i) for i in [x, y, intensity, frame_ID, cell_ID, spot_ID, file_ID]]
                                    f.write("\t".join(writelist))
                                    f.write("\n")
    print "done."

if __name__ == '__main__':
    create_spotfile(mskpath, locpath, maskfilename_token, locfilename_token, outfile)

