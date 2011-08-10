
from posix import listdir, mkdir
from posixpath import join
from subprocess import call, Popen

SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed" # folder with processed images, images may be changed, symlinks are used to go down with the size 
SIC_CELLID = '/home/basar/Personal/Martin_Seeger/cell'  #'/home/basar/Personal/Martin_Seeger/imaging/cell_id-1.4.3-HACK/cell' 
SIC_SCRIPTS = "scripts"
SIC_CELLID_PARAMS = "parameters.txt"

path = join(SIC_ROOT, SIC_PROCESSED)
cellid = SIC_CELLID
options_fn=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)

l = listdir(path)
for i in l:
    if i.startswith("GFP") and i.endswith(".path"):
        bf = join(path, i.replace("GFP", "BF"))
        ff = join(path, i)
        out = join(path, i[:-5])
        #mkdir(out)
        s = "%s -b %s -f %s -p %s -o %s" % (cellid, bf, ff, options_fn, out)
        #print "# ext. call:", s
        #call(s.split()) #doesn't work 
        Popen([cellid], shell=True) #, "-b", bf, "-f", ff, "-p", options_fn, "-o", out]) #doesn't work either
        #call(s) #doesn't work either
        #call(cellid + ' -b ' + bf + ' -f ' + ff + ' -p ' + options_fn + ' -o ' + out)
