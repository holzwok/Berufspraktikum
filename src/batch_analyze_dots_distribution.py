from os import listdir
from os.path import join, split
from subprocess import call

SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/src/spotty.R'
SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed"

path=join(SIC_ROOT, SIC_PROCESSED)

l = listdir(path)
for fn in l:
    if fn.find("SPOTS") != -1:
        print "Spotty file found:", fn
        
print "Finished."