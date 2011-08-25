import os
from os import listdir
from os.path import join, split, exists
import numpy as np
import pylab as pl


#MACHINE = "sstoma-pokrzywa"
#MACHINE = "sstoma-smeik"
MACHINE = "martin-uschan"
#MACHINE = "MJS Windows"
#MACHINE = "MJS Linux"

if MACHINE == "sstoma-smeik":
    SIC_CELLID = "/home/sstoma/svn/sstoma/src/11_01_25_cellId/cell"
    SIC_ROOT = '/local/home/sstoma/images/11-06-18-sic,matthias'
    SIC_FIJI = '/home/sstoma/bin/Fiji.app/fiji-linux64'
    SIC_SPOTTY = ''
elif MACHINE == "sstoma-pokrzywa":
    SIC_CELLID = "/Users/stymek/src/cell_id-1.4.3-HACK/cell"
    SIC_ROOT = '/Volumes/image-data/images/11-01-10-mateo,aouefa,dataanalysis-test'
    SIC_FIJI = 'fiji-macosx'
    SIC_SPOTTY = ''
elif MACHINE == "martin-uschan":
    SIC_CELLID = "/home/basar/Personal/Martin_Seeger/imaging/cell_id-143_hack/cell"
    SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
    SIC_FIJI = '/home/basar/Personal/Martin_Seeger/imaging/Fiji.app/fiji-linux64'
    SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/src/spotty.R'
elif MACHINE == "MJS Windows":
    SIC_CELLID = r'C:/Program Files (x86)/VCell-ID/bin/vcellid.exe' #TODO: working? or Progra~2 hack?
    SIC_ROOT = r'C:/Users/MJS/My Dropbox/Studium/Berufspraktikum/working_directory'
    SIC_FIJI = r'C:/Program Files/Fiji.app/fiji-win64.exe'
    SIC_SPOTTY = ''
elif MACHINE == "MJS Linux":
    SIC_CELLID = "/home/mjs/Berufspraktikum/imaging/cell_id-1.4.3_hack/cell"
    SIC_ROOT = '/home/mjs/Berufspraktikum/working_directory' 
    SIC_FIJI = '/usr/bin/fiji' #'/home/mjs/Berufspraktikum/Fiji.app/fiji-linux64' # <- this one does not work
    SIC_SPOTTY = ''


SIC_PROCESSED = "processed" # folder with processed images, images may be changed, symlinks are used to go down with the size 


def aggregate_spots(path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Aggregate all spots in current directory into matrix and write into one .csv file'''
    print "Aggregating spots..."
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
                    spot = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), float(splitline[4]), float(splitline[5]), float(splitline[6]), float(splitline[7])]
                    # this is: spot = [FileID, CellID, x, y, pixels, f.tot, f.median, f.mad]
                    spots.append(spot)
                    outfile.write("\t".join(splitline[:-1]))
                    outfile.write("\n")
    outfile.close()
    print "Finished aggregating spots."
    return spots


def column(matrix, i):
    return [row[i] for row in matrix]


def histogram_intensities(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Building histogram of spot intensities..."

    #intensities = column(spots, 5)
    intensities = [i for i in column(spots, 5) if i < 20000]

    pl.figure()
    n, bins, patches = pl.hist(intensities, 150, normed=0, histtype='stepfilled')
    pl.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
    pl.xlabel("Intensity")
    pl.ylabel("Frequency")
    pl.grid(True)

    pl.savefig(join(path, 'plot_histogram.png'))
    print "Finished building histogram of spot intensities."


def scatterplot_intensities(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Building scatterplot of spot intensities..."

    intensities = column(spots, 5)
    background = column(spots, 6)
    pl.figure()
    area = 3**2 # radius

    pl.scatter(background, intensities, s=area, marker='o', c='r')
    pl.xlabel("Background (median intensity) of cell")
    pl.ylabel("Spot intensity (background subtracted)")
    pl.xlim(xmin=500)
    pl.xlim(xmax=600)
    pl.ylim(ymin=0)
    pl.ylim(ymax=3000)
    pl.grid(True)

    pl.savefig(join(path, 'plot_scatterplot.png'))
    print "Finished building scatterplot of spot intensities."
    

def make_plots(spots):
    histogram_intensities(spots)
    scatterplot_intensities(spots)
    pl.show()
    

if __name__ == '__main__':
    spots = aggregate_spots()
    make_plots(spots)
