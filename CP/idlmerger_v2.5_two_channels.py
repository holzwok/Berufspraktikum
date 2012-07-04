# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

#mskpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#locpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
# please do not delete the following (use comment # to disable)
mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\WT_SIC1_stR610_CLN2_stQ570\mask"
locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\WT_SIC1_stR610_CLN2_stQ570"
maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
token_1 = "NG"
token_2 = "Qusar610"
tokens = [token_1, token_2]
spotoutfile = "all_spots_within_cells.txt" # "all_spots_within_cells.txt" file is created in loc folder
celloutfile = "all_cells.txt" # is also created in loc folder
fileoutfile = "all_files.txt" # is also created in loc folder
folderoutfile = "folder_summary.txt" # is also created in loc folder
spotfrequenciesfile = "spot_frequencies" # is also created in loc folder

from dircache import listdir
from os.path import join
from PIL import Image #@UnresolvedImport
import numpy as np
import matplotlib.pyplot as plt
import cPickle

def extract_loc_id(filename):
    tmp = filename.replace(".loc", "").split("_")
    #filename.split("_")[-12:-1][0] # index btwn 12th and 1st "_" from the right
    #print "loc id: ", "_".join(tmp[:-1])
    return "_".join(tmp[:-1])

def extract_msk_id(filename):
    tmp = filename.replace("_mask_cells.tif", "").split("_")
    #filename.split("_")[-14:-3][0] # index btwn 14th and 3th "_" from the right
    #print "mask id:", "_".join(tmp[:-1])
    return "_".join(tmp[:-1])

def median(numericValues):
    theValues = sorted(numericValues)
    if len(theValues) % 2 == 1:
        return theValues[(len(theValues)+1)/2-1]
    else:
        lower = theValues[len(theValues)/2-1]
        upper = theValues[len(theValues)/2]
    return (float(lower + upper)) / 2  

def loc_spots(locfile):
    print "localising spots in", locfile, "..."
    spotlist = []
    for line in open(locfile):
        spot = line.split()
        spot = [float(x) for x in spot] # x, y, intensity, frame ID
        spotlist.append(spot)
    #print "done."
    #print spotlist
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
    lout = listdir(mskpath)
    lin  = listdir(locpath)
    
    # read in spots data:
    print "reading spots data..."
    for infilename in lout:
        if maskfilename_token in infilename:
            #print infilename
            mask = Image.open(join(mskpath, infilename)).convert("RGB")
            maskpixels = mask.load()
            #mask.show()
            colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
            colordict = dict(enumerate(colorlist))    
            inverse_colordict = dict((v,k) for k, v in colordict.items())
            for locfilename in lin:
                if locfilename.endswith(locfilename_token):
                    #print "locfilename =", locfilename
                    if extract_loc_id(locfilename)==extract_msk_id(infilename): # for matching image IDs
                        print "found mask file for .loc file:", locfilename
                        spots = loc_spots(join(locpath, locfilename))
                        print "found", len(spots), "spots. some might be outside of cells."
                        cellsperfile.append(len(colorlist)-1) # this is the number of cells in the image infilename
                        for spot in spots:
                            x = spot[0]
                            y = spot[1]
                            intensity = spot[2]
                            frame_ID = spot[3]
                            cell_ID = inverse_colordict[maskpixels[spot[0], spot[1]]] # cell_ID but also color_ID
                            spot_ID = 0 # move this line up to create a global spot_ID
                            #file_ID = extract_loc_id(locfilename)
                            file_ID = locfilename.replace(".loc", "")
                            if cell_ID != 0: # excluding black (= outside of cells)
                                spot_ID += 1
                                intensities.append(intensity) # this is the "global" intensities list
                                spotwritelist.append([str(i) for i in [x, y, intensity, frame_ID, cell_ID, spot_ID, file_ID]])
    RNAs = calculate_RNA(intensities)
    for i, sublist in enumerate(spotwritelist):
        spotwritelist[i].append(str(RNAs[i]))
        #print spotwritelist[i]

    # create cells data structure (including spotless cells):
    cellsperfileiter = iter(cellsperfile)
    celldict = {}
    filedict = {}
    folderlist = []

    for locfilename in lin:
        if locfilename.endswith(locfilename_token) and not locfilename==spotoutfile:
            file_ID = locfilename.replace(".loc", "")
            #print "file_ID =", file_ID
            filedict[file_ID] = [0, 0] # spots, RNAs
            for cellnumber in range(1, cellsperfileiter.next()+1):
                ID = "_".join(file_ID.split("_")[:-1])+"_"+str(cellnumber)
                #print "ID oben =", ID
                # celldict[ID] will be for each cell [filename, sum(intensities), count(spots), sum(RNAs)] (as strings)
                celldict[ID] = [str("_".join(file_ID.split("_")[:-1])), 0.0, 0.0, 0, 0, 0, 0] # file_ID, intensity_NG, intensity_Qusar, spots_NG, spots_Qusar, RNAs_NG, RNAs_Qusar
                
    # read in cell level data:
    for sublist in spotwritelist:
        # this is super inefficient since we would only have to loop over cells not spots, whatever
        print "================================"
        print "x, y, intensity, frame_ID, cell_ID, spot_ID, file_ID =", sublist
        cell_ID_prefix = "_".join(sublist[6].split("_")[:-1]) # we skip the NG, Qusar token to aggregate across NG, Qusar
        ID = cell_ID_prefix + "_" + sublist[4] # cell_ID
        print "ID =", ID
        comparetoken = sublist[6].split("_")[-1]
        print comparetoken
        # 1: 1, 3, 5
        if token_1 in comparetoken:
            celldict[ID][1] = str(sum(float(linedata[2]) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # intensities_NG
            celldict[ID][3] = str(sum(int(1) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # spots, each line contributes one
            celldict[ID][5] = str(sum(int(linedata[7]) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # RNAs
        # 2: 2, 4, 6
        if token_2 in comparetoken:
            celldict[ID][2] = str(sum(float(linedata[2]) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # intensities_Qusar
            celldict[ID][4] = str(sum(int(1) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # spots, each line contributes one
            celldict[ID][6] = str(sum(int(linedata[7]) for linedata in spotwritelist if str("_".join(sublist[6].split("_")[:-1]))+"_"+str(linedata[4])==ID)) # RNAs
        print celldict[ID]
        
    # create spot counts per cell:
    spotfrequencies = dict((token, {}) for token in tokens)
    for spotcount in celldict.values(): # loop over cells
        #print spotcount
        if not spotcount[3] in spotfrequencies[token_1]:
            spotfrequencies[token_1][spotcount[3]] = [1]
        else:
            spotfrequencies[token_1][spotcount[3]][0] += 1
        if not spotcount[4] in spotfrequencies[token_2]:
            spotfrequencies[token_2][spotcount[4]] = [1]
        else:
            spotfrequencies[token_2][spotcount[4]][0] += 1
    totalfrequency = {}
    for token in tokens:            # loop over tokens
        #print token
        totalfrequency[token] = sum([elem[0] for elem in spotfrequencies[token].values()])
        for frequency in spotfrequencies[token]:
            spotfrequencies[token][frequency].append(spotfrequencies[token][frequency][0]/float(totalfrequency[token]))
        #print spotfrequencies[token]

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
    
    print "dumping results...",
    cPickle.dump(spotwritelist, file("spotlist.pkl", "w"))
    cPickle.dump(celldict, file("celldict.pkl", "w"))
    cPickle.dump(filedict, file("filedict.pkl", "w"))
    cPickle.dump(folderlist, file("folderlist.pkl", "w"))
    cPickle.dump(spotfrequencies, file("spotfrequencies.pkl", "w"))
    print "done."
    
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
        f.write("\t".join(["file_ID", "cell_ID", "total_intensity_NG", "total_intensity_Qusar", "number_of_spots_NG", "number_of_spots_Qusar", "total_mRNA_NG", "total_mRNA_Qusar"]))
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
        
def plot_and_store_spot_frequency(token):
    spotfrequencies = cPickle.load(file("spotfrequencies.pkl"))
    #for tk in tokens:
    #    print spotfrequencies[tk]
    plotvals = [elem[0] for elem in spotfrequencies[token].values()]
    totalspots = sum(plotvals)
    with open(join(locpath, spotfrequenciesfile), 'w') as f:
        print "writing to", join(locpath, spotfrequenciesfile+token+".txt")
        f.write("\t".join(["number_of_spots", "absolute_frequency", "relative_frequency_(percent)"]))
        f.write("\n")
        for i, val in enumerate(plotvals):
            f.write("\t".join([str(i), str(val), str(100.0*val/totalspots)]))
            f.write("\n")

    N = len(plotvals)
    ind = np.arange(N)    # x locations for the groups
    width = 0.5           # width of the bars: can also be len(x) sequence
    
    plt.figure()
    p1 = plt.bar(ind, plotvals, width, color='b')

    plt.ylabel('Frequencies')
    plt.title('Frequency of spots per cell ('+token+')')
    plt.xticks(ind+width/2., ind)
    plt.yticks(np.arange(0, max(plotvals)*1.2, 10))
    print "done."
    plt.draw()
    plt.savefig(join(locpath, "figure1"+token+".png"))
    #plt.show()

def scatter_plot_two_modes():
    x = []  
    y = []
    celldict = cPickle.load(file("celldict.pkl"))
    for cell in celldict:
        #print celldict[cell]
        x.append(int(celldict[cell][3]))
        y.append(int(celldict[cell][4]))
    plt.figure()

    # scatterplot code starts here
    plt.scatter(x, y, color='tomato')    
    # scatterplot code ends here
    plt.title('Spot frequencies per cell: comparison')
    plt.xlabel(token_1)
    plt.ylabel(token_2)
    print "done."
    plt.savefig(join(locpath, "figure2.png"))
    plt.draw()
    #plt.show()


if __name__ == '__main__':
    read_data()
    create_spotfile()
    create_cellfile()
    create_file_level_file()
    create_folder_level_file()
    plot_and_store_spot_frequency(token_1)
    plot_and_store_spot_frequency(token_2)
    scatter_plot_two_modes()
    plt.show()
