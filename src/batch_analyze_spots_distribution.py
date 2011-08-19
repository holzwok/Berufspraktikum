import os
from os import listdir
from os.path import join, split, exists
import numpy as np
import pylab as pl


SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed"


def aggregate_spots(path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Aggregate all spots in current directory into matrix and write into one .csv file'''
    outfile = join(path, "all_spots.xls")
    if exists(outfile): os.remove(outfile)
    
    with open(outfile, "a") as outfile:
        # Write file header
        outfile.write("\t".join(["FileID", "CellID", "x", "y", "pixels", "f.tot", "f.median", "f.mad"]))
        outfile.write("\n")
    
        l = listdir(path)
        spots = []
        for filename in l:
            if filename.find("SPOTS") != -1:
                print "Spotty file found:", filename
                f = open(join(path, filename), 'r')
                ls = f.readlines()
                for line in ls[1:]: # we start at 1 because we do not need another header
                    splitline = line.split(" ")
                    splitline.insert(0, splitline[-1].strip()) # fetches last item (here: file ID) and prepends
                    #print "\t".join(splitline[:-1])
                    # for the matrix, strings are converted into ints and floats
                    spot = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), int(splitline[4]), int(splitline[5]), float(splitline[6]), float(splitline[7])]
                    spots.append(spot)
                    outfile.write("\t".join(splitline[:-1]))
                    outfile.write("\n")
    outfile.close()
    print "Finished."
    return spots


def analyze_intensities(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Analyzing spot intensities..."
    def column(matrix, i):
        return [row[i] for row in matrix]

    #intensities = column(spots, 5)
    intensities = [i for i in column(spots, 5) if i < 60000]

    n, bins, patches = pl.hist(intensities, 50, normed=0, histtype='stepfilled')
    pl.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
    pl.ylabel("Frequency")
    pl.xlabel("Intensity")
    pl.grid(True)
    pl.savefig(join(path, 'histogram.png'))
    pl.show()
        
    print "Finished analyzing spot intensities."

if __name__ == '__main__':
    spots = aggregate_spots()
    analyze_intensities(spots)
