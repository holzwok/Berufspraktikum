import Image
import os
from dircache import listdir
from scipy import misc

x = -3
y = 14

'''
for filename in l:
    if filename.endswith(".TIF") or filename.endswith(".tif"):
        #print filename
        fullname = os.path.join(dirname, filename)

        im = Image.open(fullname)
        #im.show()
        
        filegroup_id = "_".join(filename.split("_")[:-1])
        filetype_id = filename.split("_")[-1]
        
        #print filegroup_id
        #print filetype_id
        # TODO: BF files are not to be shifted, all other files are to be shifted
'''
        
def shift(file, shift_x, shift_y):
        fullname = os.path.join(dirname, file)
        lena = misc.imread(fullname)
        print type(lena)
        print lena.shape, lena.dtype
        
if __name__=="__main__":

    dirname = "/home/basar/shared/20130808_Alignment_BF_fluo"
    l = listdir(dirname)

    reference = "BF"
    
    shiftable_files = [filename for filename in l if reference not in filename]
    
    print shiftable_files
    
    print l[0]
    shift(l[0], x, y) 