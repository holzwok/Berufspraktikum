from os.path import join
locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger"
celloutfile = "all_cells.txt" # is also created in loc folder

import csv

def import_text(filename, separator):
    for line in csv.reader(open(filename), delimiter=separator, 
                           skipinitialspace=True):
        if line:
            yield line

NG = [data[5] for data in import_text(join(locpath, celloutfile), '\t')][1:]
print NG