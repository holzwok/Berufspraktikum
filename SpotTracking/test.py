import re
import os
from dircache import listdir

path = "C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Project Tracking Chris" # change this as desired
#path = os.getcwd()

l = listdir(path)
for infilename in l:
    if infilename.endswith(".xls"):
        print infilename
        try:
            print min(map(int, re.findall(r'\d+', infilename))) #extract integers, map them to ints, take minimum
        except:
            continue
        