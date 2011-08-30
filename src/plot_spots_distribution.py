#!/usr/bin/env python

import os
from os import listdir
from os.path import join, split, exists
import re
import pylab as pl

from quantile import quantile
from identify_machine import SIC_ROOT, SIC_CELLID, SIC_FIJI, SIC_SPOTTY


SIC_PROCESSED = "processed" # folder with processed images, images may be changed, symlinks are used to go down with the size 


def read_spots(path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Read all spots in current directory into matrix (like aggregate_spots() except without file handling)'''
    print "Reading spots..."

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
                splitline.pop()
                # for the matrix, strings are converted into ints and floats
                time = re.search("[0-9]+", splitline[0].split("_")[-1]).group(0) # this is the time in minutes 
                splitline.append(time)
                #print splitline
                spot = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), float(splitline[4]), float(splitline[5]), float(splitline[6]), float(splitline[7]), float(time)]
                # this is: spot = [FileID, CellID, x, y, pixels, f.tot, f.median, f.mad, time]
                spots.append(spot)

    print "Finished reading spots."
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
    pl.xlim(xmin=0)
    pl.xlim(xmax=5000)
    pl.grid(True)

    pl.savefig(join(path, 'plot_histogram.png'))
    print "Finished building histogram of spot intensities."


def scatterplot_intensities(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Building scatterplot of spot intensities_unsubtracted..."

    intensities_unsubtracted, intensities_subtracted, background = column(spots, 5), column(spots, 6), column(spots, 7) 
    #ib = [(i, j) for (i, j) in zip(column(spots, 5), column(spots, 7)) if i < 2000]
    #intensities_unsubtracted, background = zip(*ib)

    area = 3**2 # radius

    pl.figure()
    pl.scatter(background, intensities_unsubtracted, s=area, marker='o', c='r')
    pl.xlabel("Background (median intensity) of cell")
    pl.ylabel("Spot intensity (background unsubtracted)")

    pl.xlim(xmin=quantile(background, 0.05)-100)
    pl.xlim(xmax=quantile(background, 0.95)+100)
    pl.ylim(ymin=0)
    pl.ylim(ymax=6000)
    pl.grid(True)

    pl.savefig(join(path, 'plot_scatterplot_intensities_unsubtracted.png'))

    pl.figure()
    pl.scatter(background, intensities_subtracted, s=area, marker='o', c='r')
    pl.xlabel("Background (median intensity) of cell")
    pl.ylabel("Spot intensity (background subtracted)")

    pl.xlim(xmin=quantile(background, 0.05)-100)
    pl.xlim(xmax=quantile(background, 0.95)+100)
    pl.ylim(ymin=0)
    pl.ylim(ymax=2000)
    pl.grid(True)
    
    pl.savefig(join(path, 'plot_scatterplot_intensities_subtracted.png'))

    print "Finished building scatterplots."
    

def make_plots(spots):
    histogram_intensities(spots)
    scatterplot_intensities(spots)
    pl.show()
    

if __name__ == '__main__':
    spots = read_spots()
    make_plots(spots)
