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

    print "Finished generating density plots."

    
if __name__ == '__main__':
    # TODO: doesn't work, just a reminder to get size/width/height
    import Image
    image = Image("sample_image.jpg")
    print image.fileName()
    print image.magick()
    print image.size().width()
    print image.size().height()
    
    # TODO: also get imagemagic to work
    #s = "convert %s -negate -depth 16 -type Grayscale -evaluate multiply 0.5 -fill white -draw point_200,200 %s" % (join(path, fn), join(path, fn[:-4] + "-colored" + ".tif"))


    generate_density_plots()
