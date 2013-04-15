import os
import csv

from Tkinter import Tk
from tkFileDialog import askdirectory

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
fulltxtpath = askdirectory(title='Choose directory with txt files') # show an "Open" dialog box and return the path to the selected file
#fulltxtpath = r"C:\Users\MJS\git\Berufspraktikum\for_Gabi\crf"

txtfiles = [os.path.join(fulltxtpath, filename) for filename in os.listdir(fulltxtpath) if filename.endswith(".txt") or filename.endswith(".TXT")]
all_data = None

for txtfile in txtfiles:
    with open(txtfile, 'r') as f:
        read_data = [line.strip() for line in f.read().split('\n')]
        func = lambda x, y : x + "\t" + y + "\t" # what to do to two list elements
        if not all_data: # first time
            all_data = read_data
        else: # all other times
            all_data = map(func, all_data, read_data)

# post-processing:
all_data = [elem.strip()+"\n" for elem in all_data]

outfile = open(os.path.join(fulltxtpath, "combined.csv"), "w")

for elem in all_data:
    #print elem,
    outfile.write(elem)

outfile.close()
