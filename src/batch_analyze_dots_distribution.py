import os
from os import listdir
from os.path import join, split, exists

SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed"

path=join(SIC_ROOT, SIC_PROCESSED)
outfile = join(path, "all_spots.xls")

if exists(outfile): os.remove(outfile)

with open(outfile, "a") as outfile:
    # Write file header
    outfile.write("\t".join(["FileID", "CellID", "x", "y", "pixels", "f.tot", "f.median", "f.mad"]))
    outfile.write("\n")

    l = listdir(path)
    for filename in l:
        if filename.find("SPOTS") != -1:
            print "Spotty file found:", filename
            f = open(join(path, filename), 'r')
            ls = f.readlines()
            for line in ls[1:]:
                splitline = line.split(" ")
                splitline.insert(0, splitline[-1].strip()) # fetches last item (here: file ID) and prepends
                #print "\t".join(splitline[:-1])
                outfile.write("\t".join(splitline[:-1]))
                outfile.write("\n")
outfile.close()
        
print "Finished."