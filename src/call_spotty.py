from os import listdir
from os.path import join, split
from subprocess import call


from global_vars import SIC_ROOT, SIC_CELLID, SIC_FIJI, SIC_SPOTTY


SIC_PROCESSED = "processed"

path=join(SIC_ROOT, SIC_PROCESSED)

xc = 0
yc = 0
G = 3

l = listdir(path)
for fn in l:
    if fn.find("INT") != -1:
        print "Spotty calling:", fn
        call(['Rscript', SIC_SPOTTY, '--args', str(xc), str(yc), str(G), join(path, fn)])
        
print "Spotty finished."