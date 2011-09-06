#!/usr/bin/env python

import os
from os import listdir
from os.path import join, split, exists
import re
import pylab as pl
import numpy as np
from scipy import interpolate
from quantile import quantile
from global_vars import *


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
                spot = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]),\
                            float(splitline[4]), float(splitline[5]), float(splitline[6]), float(splitline[7]),\
                            float(splitline[8]), n_RNA(float(splitline[6])), float(time)]
                # note that currently n_RNA depends on the subtracted signal splitline[6]. This can be changed any time.
                # this is: spot = [FileID, CellID, x, y, pixels, f.tot, f.sig, f.median, f.mad, n_RNA, time, FileID_old]
                spots.append(spot)

    print "Finished reading spots."
    return spots


def column(matrix, i):
    return [row[i] for row in matrix]


def histogram_intensities(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Building histogram of spot intensities..."

    #intensities = column(spots, 5)
    intensities = [i for i in column(spots, 6) if i < 20000]

    pl.figure()
    n, bins, patches = pl.hist(intensities, 150, normed=0, histtype='stepfilled')
    pl.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
    pl.xlabel("Intensity")
    pl.ylabel("Frequency")
    pl.xlim(xmin=0)
    pl.xlim(xmax=5000)
    pl.grid(True)

    pl.savefig(join(path, 'plot_intensity_histogram.png'))
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
    

def spots_per_cell_distribution(spots, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Building histogram for spots per cell distribution..."
    cells_spots = {}
    # Loop through images
    l = listdir(path)
    for filename in l:
        if filename.find("_all") != -1:
            # Per image, add cells to dict with unique key and initialize spot count with 0
            for id, line in enumerate([line for line in open(join(path, filename))][1:]):
                cells_spots[filename[:-3]+'{:04}'.format(id)] = 0

    # Loop through spots
    for spot in spots:
        spot_ID = spot[0]+'_{:04}'.format(int(spot[1]))
        # Where spot is found, increase corresponding counter
        cells_spots[spot_ID] += 1
    counts = cells_spots.values()
    
    # Generate the histogram
    pl.figure()
    pl.xlabel("Frequency")
    pl.ylabel("Number of spots per cell")
    
    hist, bins = np.histogram(counts, bins=max(counts))
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:] - 1)/2
    pl.gca().set_xticks(range(99)) # gca() == get current axis, not nice but works, no cell has > 99 spots
    pl.bar(center, hist, align='center', width=width)

    pl.savefig(join(path, 'plot_spot_frequency_histogram.png'))
    print "Finished building histogram for spots per cell distribution."


def plot_time2ratio_between_one_dot_number_and_cell_number(data, black_list=BF_REJECT_POS+GFP_REJECT_POS):
    print "Plotting time ratios..."
    pl.figure()
    time2one_dot = {}
    time2mult_dot = {}
    time2not_discovered = {}
    time2number_of_cells = {}
    time2ratioA = {}
    time2ratioB = {}
    time2ratioC = {}
    
    filename2hist = data["filename2hist"]
    filename2cells = data["filename2cells"]
    filename2cell_number = data["filename2cell_number"]
    for fn, d in filename2hist.iteritems():
            sfn = fn.split("_")
            time = float(re.search("[0-9]+", sfn[2]).group(0))
            #sofn = data["o2n"][fn.replace("-max", "-mask-colored")].split("_") # e.g. = ['BF', 'P0', 'T30.tif'] ??
            sofn = data["o2n"][fn].split("_") # e.g. = ['BF', 'P0', 'T30.tif']
            pos = int(re.search("[0-9]+", sofn[1]).group(0))
            
            ## filtering
            # now we need to decide if we filter out the image; decision is based on:
            # 1. if not "too many" dots were found (it is likely that it is a mistake)
            # * SIC_MAX_DOTS_PER_IMAGE is critical value
            # 2. if the ratio of dots in the cells to dots outside of the cells is
            # smaller than SIC_ALLOWED_INSIDE_OUTSIDE_RATIO then the image is discarded
            # 3. Number of missed cells is greater than SIC_MAX_MISSED_CELL_PER_IMAGE
            # 4. Number of cells is greater than SIC_MAX_MISSED_CELL_PER_IMAGE
            # 5. Filter the position from black_list
            
            tot_dots_in_cells = sum(filename2hist[fn][0].itervalues())
            tot_dots_outside_cells = filename2hist[fn][1]
            #print data["o2n"][fn], tot_dots_in_cells, tot_dots_outside_cells
            #1
            if  tot_dots_in_cells+tot_dots_outside_cells > SIC_MAX_DOTS_PER_IMAGE: continue
            #2
            if tot_dots_in_cells / max(1,float(tot_dots_outside_cells)) < SIC_ALLOWED_INSIDE_OUTSIDE_RATIO: continue
            #3
            if tot_dots_outside_cells > SIC_MAX_MISSED_CELL_PER_IMAGE: continue
            #4
            if filename2cell_number[fn] > SIC_MAX_CELLS_PER_IMAGE: continue
            #5
            if pos in black_list: continue
            ## end of filtering
            
            time2one_dot[time] = time2one_dot.get(time, 0)+filename2hist[fn][0].get(1, 0) # we add the one dots
            time2mult_dot[time] = time2mult_dot.get(time, 0)
            for i in range(10):
                time2mult_dot[time] += i*filename2hist[fn][0].get(i, 0)
            time2not_discovered[time] = time2not_discovered.get(time, 0)+filename2hist[fn][1] # not discovered
            time2number_of_cells[time] = time2number_of_cells.get(time, 0)+filename2cell_number[fn]
    for i in time2one_dot.keys():
        time2ratioA[i] = time2one_dot[i] / float(time2number_of_cells[i])
        time2ratioB[i] = time2not_discovered[i] / float(time2number_of_cells[i])
        time2ratioC[i] = time2mult_dot[i] / float(time2number_of_cells[i])
    
    data1 = [(k, v) for k, v in time2ratioA.items()]
    data1.sort()
    data1x, data1y = zip(*data1) # this unzips data1 from a list of tuples into 2 tuples
    data1x = [data1x[0]-1] + list(data1x) + [data1x[-1]+1]
    data1y = [data1y[0]] + list(data1y) + [data1y[-1]]
    data1tck = interpolate.splrep(data1x, data1y, k=2)
    data1xi = np.arange(min(data1x), max(data1x), 1)
    data1yi = interpolate.splev(data1xi, data1tck, der=0)

    data2 = [(k, v) for k, v in time2ratioB.items()]
    data2.sort()
    data2x, data2y = zip(*data2)
    
    data3 = [(k, v) for k, v in time2number_of_cells.items()]
    data3.sort()
    data3x, data3y = zip(*data3)
    
    data4 = [(k, v) for k, v in time2not_discovered.items()]
    data4.sort()
    data4x, data4y = zip(*data4)
    
    data5 = [(k, v) for k, v in time2ratioC.items()]
    data5.sort()
    data5x, data5y = zip(*data5)
    data5x = [data5x[0]-1] + list(data5x) + [data5x[-1]+1]
    data5y = [data5y[0]] + list(data5y) + [data5y[-1]]
    data5tck = interpolate.splrep(data5x, data5y, k=2)
    data5xi = np.arange(min(data5x), max(data5x), 1)
    data5yi = interpolate.splev(data5xi, data5tck, der=0)
    
    pl.subplot(221)
    pl.plot(data1x, data1y, 'or',)
    #print data1x, data1y
    pl.xlabel("Time [s]")
    #pl.ylabel("1dot/#cell")

    pl.subplot(221)
    pl.plot(data5x,data5y,'og')
    pl.xlabel("Time [s]")
    #pl.ylabel("1-10dot / #cell")
    pl.plot( data1xi, data1yi, "r", data5xi, data5yi, "g")
    #print data1xi, data1yi
    pl.legend(["1dot/#cell", "1-10dot/#cell"])
    
    pl.subplot(222)
    pl.plot(data2x, data2y)
    #print data2x, data2y
    pl.xlabel("Time [s]")
    pl.ylabel("Missed/#cell")
    
    pl.subplot(223)
    pl.plot(data3x, data3y)
    #print data3x, data3y
    pl.xlabel("Time [s]")
    pl.ylabel("#cell")
 
    pl.subplot(224)
    pl.plot(data4x, data4y)
    #print data4x, data4y
    pl.xlabel("Time [s]")
    pl.ylabel("#missed dots")
    
    pl.show()
    print "Finished plotting time ratios."


def make_plots(spots):
    histogram_intensities(spots)
    scatterplot_intensities(spots)
    spots_per_cell_distribution(spots)
    pl.show()
    

if __name__ == '__main__':
    spots = read_spots()
    make_plots(spots)
