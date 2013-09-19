import Image
import os
from dircache import listdir

dirname = "/home/basar/shared/20130808_Alignment_BF_fluo"

x = -3
y = 14

l = listdir(dirname)

'''
for filename in l:
    if filename.endswith(".TIF") or filename.endswith(".tif"):
        print filename
        fullname = os.path.join(dirname, filename)

        im = Image.open(fullname)
        #im.show()
        
        filegroup_id = "_".join(filename.split("_")[:-1])
        filetype_id = filename.split("_")[-1]
        
        print filegroup_id
        print filetype_id
'''

print l[0]
