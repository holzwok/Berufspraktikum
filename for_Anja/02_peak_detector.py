import shelve
import numpy as np
from scipy import signal
from os.path import join
from dircache import listdir

if __name__=="__main__":
    imagepath = "C:/Users/MJS/git/Berufspraktikum/for_Anja"
    filelist = listdir(imagepath)

    for imagename in filelist:
        if imagename.endswith(".tif"):
            filename = join(imagepath, imagename+"_profiles.shl")
            profiles = shelve.open(filename)
            for key in sorted(profiles):
                data = profiles[key]
                print data
                print signal.find_peaks_cwt(data, np.arange(1, 20))