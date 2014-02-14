import re
import shutil
import os, sys
from os import path

path = "\\\\Biodata\\molbp\\GabiSchreiber\\Kopie von 140114_MS2_T49_T50_T54_T55\\Export\\Sic1_T49_3xYFP_1.4%LP_1.ptu\\"
dirs = os.listdir(path)

filedict = dict((int(file.split("-")[-1]), file) for file in dirs) # get the last number in the directory name and use it as a key in the dictionary

fulltiflist = []

# populate the full tif list by walking through all directories
for key in sorted(filedict.iterkeys()):
    prefix = os.path.join(path, filedict[key])

    imagelist = [file for file in os.listdir(os.path.join(path, filedict[key])) if file.endswith(".tif")] # unsorted list of images

     # function to extract number from filename
    def extractkey(filename):
        if re.findall('\d+', filename):
            return int(re.findall('\d+', filename)[0])
        else:
            return 0

    sortedimagelist = sorted(imagelist, key=extractkey)
    fullsortedimagelist = [os.path.join(prefix, file) for file in sortedimagelist] # enhance the sorted images by prefixes
    #print fullsortedimagelist

    fulltiflist.extend(fullsortedimagelist)

# convenience function to slice a list into equal-sized pieces, starting with the second, fourth etc.
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i+1:i+n+1:2]

# list containing list of filenames by stack
mychunks = list(chunks(fulltiflist, 26))

for chunk in mychunks:
    print chunk
    print

# make output folder
if not os.path.exists(os.path.join(path, "output")):
    os.makedirs(os.path.join(path, "output"))

for i, chunk in enumerate(mychunks):
    # create numbered output folder
    subfolder = os.path.join(path, "output", "stack_"+str(i))
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    # copy files into output folders
    for j, src in enumerate(chunk):
        shutil.copy2(src, os.path.join(subfolder, str("%.2d" %j)+".tif"))
        #shutil.copy2(src, subfolder)
