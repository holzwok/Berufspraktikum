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
import re

p = re.compile('\d+')
m = p.match('0123tempo')
print m.group()


from itertools import groupby

things = [["animal", "bear"], ["animal", "duck"], ["plant", "cactus"], ["vehicle", "speed boat"], ["vehicle", "school bus"]]

categories = []

for key, group in groupby(things, lambda x: x[0]):
    print "new group:"
    categories.append(key)
    print group
    for thing in group:
        print (thing[0], thing[1], key)

print categories

categories2 = [key[0] for key in groupby(things, lambda x: x[0])]
print categories2

animals = [thing[1] for thing in things if thing[0]=='animal']

print animals

print '{:04}'.format(21)
'''