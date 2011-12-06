#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from os.path import join
from subprocess import call, Popen, PIPE, STDOUT
import Image

from global_vars import SIC_PROCESSED, SIC_ROOT

def generate_density_plots(path=join(SIC_ROOT, SIC_PROCESSED)):
    # Executes the following command:
    # >Rscript plot_spot.R --args cellID_file boundary_file interior_file out_name
    
    print "----------------------------------------------------"
    print "Generating density plots..."
    defaultviewer = "eog" # Eye of Gnome, for Linux/Gnome environment
    rscriptname = "plot_spot.R"

    l = listdir(path)
    for filename in sorted(l):
        if filename.endswith("_all"):
            print "Considering file:", filename
            cellID_file = filename
            boundary_file = filename[:-4]+".tif_BOUND.txt"
            interior_file = filename[:-4]+".tif_INT.txt"
            out_name = filename[:-4]+"_density"
            execstring = ['Rscript', rscriptname, '--args', join(path, cellID_file), join(path, boundary_file), join(path, interior_file), join(path, out_name)]
            print "External call:", " ".join(execstring)
            call(execstring)
            Image.open(join(path, out_name)).show()
            # Open picture in default viewer
            #Popen([defaultviewer, join(path, out_name)], stdout=PIPE, stderr=STDOUT)

    print "Finished generating density plots."


def draw_spots_in_images(filename, x=200, y=150, path=join(SIC_ROOT, SIC_PROCESSED), markerwidth = 2*2):
    print "----------------------------------------------------"
    print "Drawing spot..."
    #defaultviewer = "eog" # Eye of Gnome, for Linux/Gnome environment

    execstring = "convert %s -fill red -strokewidth 10 -draw line_0,0_0,0 %s" % (join(path, filename), join(path, filename))
    execsubstring = execstring.split()
    for j in range(len(execsubstring)):
        if execsubstring[j] == "line_0,0_0,0":
            execsubstring[j] = 'line %s,%s %s,%s' % (x+markerwidth/2, y, x-markerwidth/2, y)
    print "External call:", " ".join(execsubstring)
    call(execsubstring)
    
    execstring = "convert %s -fill red -strokewidth 10 -draw line_1,1_1,1 %s" % (join(path, filename), join(path, filename))
    execsubstring = execstring.split()
    for j in range(len(execsubstring)):
        if execsubstring[j] == "line_1,1_1,1":
            execsubstring[j] = 'line %s,%s %s,%s' % (x, y+markerwidth/2, x, y-markerwidth/2)
    print "External call:", " ".join(execsubstring)
    call(execsubstring)

    Image.open(join(path, filename)).show()
    # Open picture in default viewer
    #Popen([defaultviewer, join(path, filename)], stdout=PIPE, stderr=STDOUT)
    print "Finished drawing spot."

    
if __name__ == '__main__':
    #generate_density_plots()
    path=join(SIC_ROOT, SIC_PROCESSED)
    '''
    # the following works just fine:
    l = listdir(path)
    for filename in sorted(l):
        if "out" in filename:
            print "Considering file:", filename
            draw_spots_in_images(filename, x=100, y=150)            
    '''     
    infofile = "all_spots.xls"
    with open(join(path, infofile), "r") as readfile:
        for line in readfile:
            #if not readfile.isfirstline():
                print line
            

