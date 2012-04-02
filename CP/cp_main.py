# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

from dircache import listdir
from os.path import join
from PIL import Image, ImageOps, ImageFilter

outpath = "/home/basar/Personal/Martin_Seeger/CellProfiler_work/output"
path = "/home/basar/Personal/Martin_Seeger/CellProfiler_work/"

def extract_id(filename):
    return infilename.split("_")[-2:-1][0]

lout = listdir(outpath)
lin  = listdir(path)
for infilename in lout:
    if infilename.startswith("MAX_"):
        print extract_id(infilename) # file ID for matching with loc file
        mask = Image.open(join(outpath, infilename))
        mask.show()
        print mask.getcolors()   
        for locfilename in lin:
            if locfilename.endswith(".loc"):
                #print extract_id(locfilename)
                pass

        
        # maske anwenden:
        # mit .loc file mergen
        # nur punkte filtern/einzeichnen, fuer die maske == true
        # test
        
