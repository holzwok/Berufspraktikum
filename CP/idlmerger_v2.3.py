# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

mskpath = "C://Users//MJS//git//Berufspraktikum//CP//mask"
locpath = "C://Users//MJS//git//Berufspraktikum//CP"
maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
spotoutfile = "all_spots_within_cells.loc" # "all_spots_within_cells.loc" file is created in loc folder
celloutfile = "all_cells.txt" # is also created in loc folder
fileoutfile = "all_files.txt" # is also created in loc folder
folderoutfile = "folder_summary.txt" # is also created in loc folder
spotfrequenciesfile = "spot_frequencies.txt" # is also created in loc folder

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport
import numpy as np
import matplotlib.pyplot as plt

import cPickle

def extract_loc_id(filename):
    return filename.replace(".loc", "")
    #filename.split("_")[-12:-1][0] # index btwn 12th and 1st "_" from the right

def extract_msk_id(filename):
    return filename.replace("_mask_cells.tif", "")
    #filename.split("_")[-14:-3][0] # index btwn 14th and 3th "_" from the right

def median(numericValues):
    theValues = sorted(numericValues)
    if len(theValues) % 2 == 1:
        return theValues[(len(theValues)+1)/2-1]
    else:
        lower = theValues[len(theValues)/2-1]
        upper = theValues[len(theValues)/2]
    return (float(lower + upper)) / 2  

def loc_spots(locfile):
    spotlist = []
    for line in open(locfile):
        spot = line.split()
        spot = [float(x) for x in spot] # x, y, intensity, frame ID
        spotlist.append(spot)
    return spotlist

def calculate_RNA(intensities):
    med = median(intensities)
    print "median intensity of", len(intensities), "detected spots is", med, "."
    RNA = [int(0.5+intensity/med) for intensity in intensities]
    return RNA

def read_data():
    print "reading data..."
    intensities = []
    spotwritelist = []
    cellsperfile = []
    spotfrequencies = {}
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
    filedict = {}
    folderlist = []
    for infilename in lout:
        if maskfilename_token in infilename:
            file_ID = infilename.replace("_mask_cells.tif", "")
            filedict[file_ID] = [0, 0] # spots, RNAs
            for cellnumber in range(1, cellsperfile.next()+1):
                ID = file_ID+"_"+str(cellnumber)
                celldict[ID] = [infilename.replace("_mask_cells.tif", ""), 0.0, 0, 0] # file_ID, intensity, spots, RNAs
                
    # read in cell level data:
    for sublist in spotwritelist:
        ID = sublist[6]+"_"+sublist[4]
        celldict[ID][1] = str(sum(float(linedata[2]) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # intensities
        celldict[ID][2] = str(sum(int(1) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # spots, each line contributes one
        celldict[ID][3] = str(sum(int(linedata[7]) for linedata in spotwritelist if str(linedata[6])+"_"+str(linedata[4])==ID)) # RNAs

    # create spot counts per cell:
    for spotcount in celldict.values():
        if not spotcount[2] in spotfrequencies:
            spotfrequencies[spotcount[2]] = [1]
        else:
            spotfrequencies[spotcount[2]][0] += 1
    totalfrequency = sum([elem[0] for elem in spotfrequencies.values()])
    for frequency in spotfrequencies:
        spotfrequencies[frequency].append(spotfrequencies[frequency][0]/float(totalfrequency))
    #print spotfrequencies

    # read in file level data:
    for sublist in spotwritelist:
        file_ID = sublist[6]
        filedict[file_ID][0] = str(sum(int(1) for linedata in spotwritelist if str(linedata[6])==file_ID)) # spots, each line contributes one
        filedict[file_ID][1] = str(sum(int(linedata[7]) for linedata in spotwritelist if str(linedata[6])==file_ID)) # RNAs

    # read in folder level data:
    folderlist.append(str(len(spotwritelist))) # spots, each line contributes one
    folderlist.append(str(sum(int(linedata[7]) for linedata in spotwritelist))) # RNAs
    folderlist.append(str(median(intensities))) # median intensity
    #print folderlist
    
    cPickle.dump(spotwritelist, file("spotlist.pkl", "w"))
    cPickle.dump(celldict, file("celldict.pkl", "w"))
    cPickle.dump(filedict, file("filedict.pkl", "w"))
    cPickle.dump(folderlist, file("folderlist.pkl", "w"))
    cPickle.dump(spotfrequencies, file("spotfrequencies.pkl", "w"))
    
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
        f.write("\t".join(["file_ID", "cell_ID", "total_intensity", "number_of_spots", "total_mRNA"]))
        f.write("\n")
        for ID in celldict:
            nextline = celldict[ID][0]+"\t"+ID+"\t"+"\t".join([str(elem) for elem in celldict[ID][1:]])+"\n"
            f.write(nextline)
    print "done."

def create_file_level_file():
    filedict = cPickle.load(file("filedict.pkl"))
    #print filedict
    with open(join(locpath, fileoutfile), 'w') as f:
        print "writing to", join(locpath, fileoutfile)
        f.write("\t".join(["file_ID", "number_of_spots", "total_mRNA"]))
        f.write("\n")
        for file_ID in filedict:
            nextline = file_ID +"\t"+"\t".join([str(elem) for elem in filedict[file_ID]])+"\n"
            f.write(nextline)
    print "done."

def create_folder_level_file():
    folderlist = cPickle.load(file("folderlist.pkl"))
    with open(join(locpath, folderoutfile), 'w') as f:
        print "writing to", join(locpath, folderoutfile)
        f.write("\t".join(["number_of_spots", "total_mRNA", "median_intensity"]))
        f.write("\n")
        nextline = "\t".join(folderlist)+"\n"
        f.write(nextline)
    print "done."
        
def plot_and_store_spot_frequency():
    spotfrequencies = cPickle.load(file("spotfrequencies.pkl"))
    plotvals = [elem[0] for elem in spotfrequencies.values()]
    totalspots = sum(plotvals)
    with open(join(locpath, spotfrequenciesfile), 'w') as f:
        print "writing to", join(locpath, spotfrequenciesfile)
        f.write("\t".join(["number_of_spots", "absolute_frequency", "relative_frequency_(percent)"]))
        f.write("\n")
        for i, val in enumerate(plotvals):
            f.write("\t".join([str(i), str(val), str(100.0*val/totalspots)]))
            f.write("\n")

    N = len(plotvals)
    ind = np.arange(N)    # x locations for the groups
    width = 0.5           # width of the bars: can also be len(x) sequence
    
    p1 = plt.bar(ind, plotvals, width, color='b')

    plt.ylabel('Frequencies')
    plt.title('Frequency of spots per cell')
    plt.xticks(ind+width/2., ind)
    plt.yticks(np.arange(0, max(plotvals)*1.2, 1))
    print "done."
    
    plt.show()


if __name__ == '__main__':
    read_data()
    create_spotfile()
    create_cellfile()
    create_file_level_file()
    create_folder_level_file()
    plot_and_store_spot_frequency()
    