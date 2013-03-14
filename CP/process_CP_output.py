import scipy.io
import numpy as np
from os.path import join, exists

path = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_Cell_Cycle_Segmentation\no_stacks"
matfile = "DefaultOUT.mat"

matfilepath = join(path, matfile)

if exists(matfilepath):
    mat = scipy.io.loadmat(matfilepath, squeeze_me=True, struct_as_record=True)
    '''
    for key in mat:
        print key
        print mat[key]
        print
    #print type(mat)
    '''
    #print type(mat['handles'])
    #print mat['handles']
    hdls = mat['handles'].item()
    for i, elem in enumerate(hdls):
        print i
        print elem
else:
    print "file not found:", matfilepath
