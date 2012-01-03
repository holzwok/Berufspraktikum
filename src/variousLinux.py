'''
from os import remove
from os.path import join, exists
from shutil import copy
from string import replace

from global_vars import SIC_PROCESSED, SIC_ROOT

def replace_decimal_separators(path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Replacing decimal separators..."
    infile = join(path, "all_spots.xls")
    
    file_content = open(infile, "r").read()
    file_content_replaced = replace(file_content, ".", ",")
    file_content_replaced = replace(file_content_replaced, "f,", "f.") # HACK
    file_content_replaced = replace(file_content_replaced, ",tif", ".tif") # HACK
        
    if exists(infile+"~"): remove(infile+"~")
    if exists(infile): copy(infile, infile+"~")
    
    with open(infile, "w") as outfile:
        outfile.write(file_content_replaced)
    outfile.close()
    print "Finished replacing decimal separators."
    
if __name__ == '__main__':
    replace_decimal_separators()
'''

import os
print os.getcwd()