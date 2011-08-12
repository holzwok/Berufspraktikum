from os import listdir
from os.path import join, split
from subprocess import call

SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/imaging/scripts/spotty.R'
SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed"

path=join(SIC_ROOT, SIC_PROCESSED)

xc = 0
yc = 0

l = listdir(path)
for fn in l:
    if fn.find("INT") != -1:
        print "Spotty calling:", fn
        call(['Rscript', SIC_SPOTTY, '--args', str(xc), str(yc), join(path, fn)])
print "Spotty finished."