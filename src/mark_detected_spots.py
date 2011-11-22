#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from os.path import join
from subprocess import call

from global_vars import SIC_PROCESSED, SIC_ROOT

def mark_spots(path=join(SIC_ROOT, SIC_PROCESSED)):
    # Executes the following command:
    # >Rscript plot_spot.R --args cellID_file boundary_file interior_file out_name
    
    rscriptname = "plot_spot.R"
    cellID_file = ""
    boundary_file = ""
    interior_file = ""
    out_name = "karlheinz"

    l = listdir(path)
    for filename in sorted(l):
        if "INT" in filename:
            print "Calling plot_spot.R on", filename
            call(['Rscript', rscriptname, '--args', join(path, cellID_file), join(path, boundary_file), join(path, interior_file), join(path, out_name)])
    print "Finished executing plot_spot.R."

    
if __name__ == '__main__':
    mark_spots()
