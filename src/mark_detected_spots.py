#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from os.path import join
from subprocess import call, Popen

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
            # Open picture in default viewer
            Popen([defaultviewer, join(path, out_name)])

    print "Finished executing plot_spot.R."

    
if __name__ == '__main__':
    generate_density_plots()
