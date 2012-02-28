#!/usr/bin/env python
"""Processing of SIC data.

DATA SETUP
1. Sorting files and preparing of symlinks. The purpose of this is to have both DIC and NIBA files in the $SIC_ROOT/$SIC_PROCESSED directory.
a/ orig files are placed in $SIC_ROOT/orig
* initial setup
b/ NIBA files are copied to $SIC_ROOT/processed
* copy_NIBA_files_to_processed
c/ DIC files are linked to $SIC_ROOT/$SIC_PROCESSED
* link_DIC_files_to_processed or copy_DIC_files_to_processed 


2. Editing NIBA files.
The purpose of this operation is to convert NIBA stacks to 2D binary mask images
and to create a tab-delimited file (*.xls) containing the positions of centers of dots.
These operations are performed with FIJI batch processing script:
* $SIC_ROOT/$SIC_SCRIPTS/$SIC_FIND_DOTS_SCRIPT 
run it on a folder:
$SIC_ROOT/$SIC_PROCESSED (contains NIBA files)


3. Coloring the processed NIBA files
...obsolete?

4. Symlinks cont.


5. Finding cells in images.
The purpose of this operation is to create lists of pixels building up each cell in each DIC image.
Additionally, to ease the inspection of results the images where each cell is bounded with white circle are generated.
To perform this task, cell-id was used, however the source code required editing to access and write the lists into files
To use cell-id, a special file name convention has to be used. Therefore:
a/ symlinks are created in $SIC_ROOT/$SIC_LINKS
* create_symlinks
b/ cell-id config files with correct name correspondence are created
* prepare_b_and_f_single_files
c/ cell-id is run and creates files
* script: run_analysis


6. Gathering and processing the data from FIJI and cell-id processing
"""

# Module documentation variables:
__authors__="""Szymon Stoma, Martin Seeger"""
__contact__=""
__license__="Cecill-C"
__date__="2012"
__version__="0.9"
__docformat__= "restructuredtext en"


import time, datetime
tic = time.time()
import re
import os
from os import listdir, rename, path, mkdir, access, name, R_OK, F_OK, remove
from shutil import copyfile, copytree, rmtree
from os.path import join, split, exists
from shutil import copy
from string import replace
from copy import deepcopy
from subprocess import call
import pylab as pl
import pickle
if os.name != 'nt':
    from os import symlink #@UnresolvedImport
elif os.name == 'nt':
    import pywintypes #@UnresolvedImport @UnusedImport
    from win32com.client import Dispatch #@UnresolvedImport @UnusedImport

import set_cell_id_parameters as scip
import plot_functions as pf 
from global_vars import SIC_ROOT, SIC_ORIG, SIC_SCRIPTS, SIC_PROCESSED,\
    SIC_RESULTS, FIJI_STANDARD_SCRIPT, FIJI_SLICE_SCRIPT, SIC_FIJI, PARAM_DICT,\
    SIC_CELLID_PARAMS, FIJI_TRACK_SCRIPT, SIC_FILE_CORRESPONDANCE, SIC_CELLID,\
    SIC_BF_LISTFILE, SIC_F_LISTFILE, POSI_TOKEN, FIJI_HEADERS, GMAX, SIC_SPOTTY,\
    NIBA_ID, DIC_ID, CELLID_FP_TOKEN, TIME_TOKEN, RAD2, n_RNA, SIC_DATA_PICKLE,\
    SIC_MEDIAN


def prepare_structure(path=SIC_ROOT,
                      skip=[SIC_ORIG, SIC_SCRIPTS, "orig", "orig1", "orig2", "orig3", "orig4", "orig5", "orig6"],
                      create_dirs=[SIC_PROCESSED],
                      check_for=[join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT),
                        join(SIC_ROOT, SIC_ORIG)],
                      fiji=SIC_FIJI
                      ):
    '''Remove obsolete directories, create required directories and check requirements'''
    print "----------------------------------------------------"
    print "Preparing structure..."

    def remove_old_dirs(path, skip):
        print "Working in path:", path
        i = SIC_PROCESSED
        if exists(join(path, i)):
            print "Removing:", join(path, i)
            rmtree(join(path, i))
        # disabled on request by Aouefa, 20111024
        '''
        l = listdir(path)
        for i in sorted(l):
            # removing everything which is not a SIC_ORIG or SIC_SCRIPTS
            if i not in skip and not i.startswith("orig"):
                rmtree(join(path, i))
                print "Removing:", join(path, i)
            else:
                print "Skipping:", join(path, i)
        '''
    def create_required_dirs(path, create_dirs):
        for i in create_dirs:
            # creating required directories if not yet existing
            if not access(join(path, i), F_OK):
                mkdir(join(path, i))
                print "Creating:", join(path, i)
    def check_reqs(check_for):
        print "Checking requirements..."
        for i in check_for:
            if access(i, R_OK):
                print "Found:", i, "... OK"
            else:
                print "File not present, aborting:", i
                raise Exception()
        # The following is necessary under Windows as command line FIJI will only accept macros in FIJI_ROOT/macros/
        # It is not strictly required but harmless under Linux/Debian
        try:
            print "Copying", join(path, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), "to", join(os.path.dirname(fiji), "macros", FIJI_STANDARD_SCRIPT)
            copyfile(join(path, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), join(os.path.dirname(fiji), "macros", FIJI_STANDARD_SCRIPT))
        except:
            print "Unable to copy FIJI macro."
        print "Finished checking requirements."

    remove_old_dirs(path, skip)
    create_required_dirs(path, create_dirs)
    check_reqs(check_for)
    # TODO: this must be done somewhere
    #scip.set_parameters(PARAM_DICT, join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS))
    #with open(join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS), 'r') as pfile:
    #    print "Using cell-ID parameters:"
    #    print pfile.read()
    print "Finished preparing structure."
    

def copy_NIBA_files_to_processed(path=join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED), niba=NIBA_ID):
    '''Copy NIBA files to processed'''
    print "----------------------------------------------------"
    print "Copying NIBA files to processed..."
    l = listdir(path)
    for i in sorted(l):
        # Only file names containing NIBA_ID and not containing 'thumb' are copied
        if i.find(niba) != -1 and i.find('thumb') == -1:
            print "Copying", join(path, i), "to", join(dest, i)
            copyfile(join(path, i), join(dest, i))
    print "Finished copying NIBA files to processed."


# use this method if you want to symlink DIC files
# otherwise use copy_DIC_files_to_processed
def link_DIC_files_to_processed(path = join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED), dic=DIC_ID):
    '''Link DIC files to processed'''
    print "----------------------------------------------------"
    print "Linking DIC files to processed..."
    l = listdir(path)
    for i in sorted(l):
        if i.find(dic) != -1 and i.find('thumb') == -1: # link only files whose name contains DIC_ID and not thumb
            print "Linking", join(path, i), "to", join(dest, i)
            if os.name != 'nt':
                if exists(join(dest, i)): os.remove(join(dest, i))
                symlink(join(path, i), join(dest, i))
            else:
                # TODO: for Windows, create shortcuts instead of symlinks
                print "Operating system is Windows, calls to symlink will not work."
    print "Finished linking DIC files to processed."
        

def copy_DIC_files_to_processed(path = join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED), dic=DIC_ID):
    '''Copy DIC files to processed'''
    print "----------------------------------------------------"
    print "Copying DIC files to processed..."
    l = listdir(path)
    for i in sorted(l):
        if i.find(dic) != -1 and i.find('thumb') == -1: # link only files whose name contains DIC_ID and not thumb
            print "Copying", join(path, i), "to", join(dest, i)
            copyfile(join(path, i), join(dest, i))
    print "Finished copying DIC files to processed."
        

# use this method only if you want to hand the entire brightfield stack to cell-ID
# otherwise use run_fiji_standard_mode_select_quarter_slices for better cell recognition
def run_fiji_standard_mode(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), niba=NIBA_ID, fiji=SIC_FIJI):
    '''Run FIJI for stack projection'''
    print "----------------------------------------------------"
    print "Running FIJI..."
    l = listdir(path)
    for fn in sorted(l):
        print "Looking in:", fn
        # file name containing NIBA
        if fn.find(niba+".TIF") != -1: # run fiji only for files whose name contains NIBA_ID+".TIF"
            print "External call:", [fiji, join(path, fn), "-macro", script_filename, "-batch"]
            call([fiji, join(path, fn), "-macro", script_filename, "-batch"])
    print "Finished running FIJI."


def run_fiji_standard_mode_select_quarter_slices(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), slice_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_SLICE_SCRIPT), niba=NIBA_ID, dic=DIC_ID, fiji=SIC_FIJI):
    '''Run FIJI for stack projection'''
    print "----------------------------------------------------"
    print "Running FIJI (quarter stack mode)..."
    l = listdir(path)
    for fn in sorted(l):
        print "Looking in:", fn
        # file name containing NIBA
        if fn.find(niba+".TIF") != -1: # run fiji only for files whose name contains NIBA_ID+".TIF"
            print "External call:", " ".join([fiji, join(path, fn), "-macro", script_filename, "-batch"])
            call([fiji, join(path, fn), "-macro", script_filename, "-batch"])
        if fn.find(dic+".TIF") != -1: # run fiji only for files whose name contains DIC_ID+".TIF"
            # now delete all slices except the one 1/4 into the stack
            print "External call:", " ".join([fiji, join(path, fn), "-macro", slice_filename, "-batch"])
            call([fiji, join(path, fn), "-macro", slice_filename, "-batch"])
    def replace_stacks_by_single_slices():
        print "Replacing stacks by single slices..."
        l = listdir(path)
        for filename in sorted(l):
            if dic in filename and "_quarter_slice" in filename:
                cut = len("_quarter_slice.tif")
                if exists(join(path, filename[:-cut])): 
                    os.remove(join(path, filename[:-cut]))
                    print "Removed", filename[:-cut]
                    os.rename(join(path, filename), join(path, filename[:-cut]))
                    print "Renamed", filename, "to", filename[:-cut]
    replace_stacks_by_single_slices()
    print "Finished running FIJI."


def create_map_image_data(filename=join(SIC_ROOT, SIC_PROCESSED, SIC_FILE_CORRESPONDANCE), path=join(SIC_ROOT, SIC_PROCESSED), niba=NIBA_ID, dic=DIC_ID):
    '''Create map image data'''
    print "----------------------------------------------------"
    print "Creating map image data..."
    f = open(filename, 'w')
    l = listdir(path)
    o2n = {}
    niba2dic = {}
    dic2niba = {}

    # creating new names and maps: NIBA <-> DIC
    for i in sorted(l):
        # First do the niba + ".TIF" files
        if i.endswith(niba + ".TIF"):
            print "Mapping:", i
            nfn = i.split("_") # split filename at '_'
            try:
                time = re.search("[0-9]+", nfn[-3]).group(0) # this is the substring of nfn[-3] containing 1 or several decimal digits ('min' is ignored)
            except:
                time = "0" 
            if nfn[-2] == "": pos = "0"
            else: pos = nfn[-2]
            nn = "GFP_" + POSI_TOKEN + str(pos) + "_" + TIME_TOKEN + time + ".tif" # new name
            o2n[i + CELLID_FP_TOKEN] = nn
            #corresponding_dic = nfn[0] + "_" + nfn[1] + "_" + nfn[2] + "_" + nfn[3] + "_" + re.sub(" [0-9]", "", nfn[4].replace(niba[1:],dic[1:])) # old, works on conforming filenames 
            nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba, dic).replace(".tif", ".TIF"))
            #nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba[1:], dic[1:]).replace(".tif", ".TIF")) # this sucks because it assumes that niba and dic start with the same letter
            corresponding_dic = "_".join(nfn) 
            print "Corresponding_dic:", corresponding_dic
            niba2dic[i + CELLID_FP_TOKEN] = corresponding_dic   # 1:1 mapping
            if dic2niba.has_key(corresponding_dic):             # 1:n mapping
                dic2niba[corresponding_dic].append(i + CELLID_FP_TOKEN)
            else:
                dic2niba[corresponding_dic] = [i + CELLID_FP_TOKEN]

            # we have met this DIC first time so we need to add it to the maps
            bff = "BF_" + POSI_TOKEN + str(pos) + "_" + TIME_TOKEN + time + ".tif"
            o2n[corresponding_dic] = bff
            
        # Second do the NIBA + "-0001.TIF" etc. files
        if i.find(niba+"-") != -1: # only sliced images should contain the string niba+"-"
            print "Mapping:", i
            nfn = i.split("_")
            try:
                time = re.search("[0-9]+", nfn[-3]).group(0) # this is the substring of nfn[-3] containing 1 or several decimal digits ('min' is ignored)
            except:
                time = "0" 
            if nfn[-2] == "": pos = "0"
            else: pos = nfn[-2]
            slice_counter = nfn[-1][-8:-4]    # this assumes that filenames of slices end like '0001.TIF'
            nn = "GFP_" + POSI_TOKEN + str(pos) + slice_counter + "_" + TIME_TOKEN + time + ".tif" # new name
            o2n[i] = nn
            nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba, dic).replace("-"+slice_counter, '').replace(".tif", ".TIF")) 
            #nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba[1:], dic[1:]).replace("-"+slice_counter, '').replace(".tif", ".TIF")) 
            corresponding_dic = "_".join(nfn) 
            print "Corresponding_dic:", corresponding_dic
            niba2dic[i] = corresponding_dic         # 1:1 mapping
            if dic2niba.has_key(corresponding_dic): # 1:n mapping
                dic2niba[corresponding_dic].append(i)
            else:
                dic2niba[corresponding_dic] = [i]

    # checking if all required DIC files are present
    for i in dic2niba:
        if i not in sorted(l):
            print "Warning: required DIC file not found:", i

    # generating rename file
    for i in o2n.keys():
        f.write(i + " ")
        f.write(o2n[i])
        f.write("\n")
    f.close()
    
    d = dict()
    tempd = {
        "niba2dic" : niba2dic,
        "dic2niba" : dic2niba,
        "o2n" : o2n,
    }
    d.update(tempd)
    pickle.dump(d, file(join(path, SIC_DATA_PICKLE), "w"))


    print "Finished creating map image data."
    return niba2dic, dic2niba, o2n


def create_symlinks(old2new, sourcepath=join(SIC_ROOT, SIC_PROCESSED), targetpath=join(SIC_ROOT, SIC_PROCESSED)):
    '''Create symlinks'''
    # TODO: Create Windows version
    print "----------------------------------------------------"
    print "Creating symlinks..."
    for old in old2new.keys():
        print "Linking", old, "to", old2new[old]
        try:
            symlink(join(sourcepath, old), join(targetpath, old2new[old]))
        except:
            print "There was a problem with linking!"
            print "Check whether original filenames allow for unique cell ID filenames."
    #import pdb; pdb.set_trace()
    print "Finished creating symlinks."


def prepare_b_and_f_single_files(niba2dic, o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "----------------------------------------------------"
    print "Writing BF and F single files..."
    for i in niba2dic.keys():
        bf = open(join(path, o2n[niba2dic[i]][:-3] + "path"), "w") # we cut out last 3 chars from the file name and replace them by 'path'
        ff = open(join(path, o2n[i][:-3] + "path"), "w")
        ff.write(join(path, o2n[i]) + '\n')
        bf.write(join(path, o2n[niba2dic[i]]) + '\n')
        ff.close()
        bf.close()
    print "Finished writing BF and F single files."


def run_cellid(path = join(SIC_ROOT, SIC_PROCESSED),
               cellid=SIC_CELLID,
               bf_fn=join(SIC_ROOT, SIC_PROCESSED, SIC_BF_LISTFILE),
               f_fn=join(SIC_ROOT, SIC_PROCESSED, SIC_F_LISTFILE),
               options_fn=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS),
               output_prefix=join(SIC_ROOT, SIC_PROCESSED)
               ):
    print "----------------------------------------------------"
    print "Running Cell-ID..."
    #s = "convert %s -negate -channel G -evaluate multiply 0. -channel B -evaluate multiply 0. %s" % (join(path,fn), join(path,fn[:-4]+"-colored"+".tif"))
    # TODO: bf_fn, f_fn never used (currently single files are used instead of list files)
    l = listdir(path)
    for ffname in sorted(l):
        if ffname.startswith("GFP") and ffname.endswith(".path"):
            print "Considering file:", ffname
            #bf = join(path, ffname.replace("GFP", "BF")) # this fails if DIC:NIBA is 1:n relationship (i.e. for slices)
            ffcomponents = ffname.split("_")
            if len(ffcomponents[-2]) - len(POSI_TOKEN) >= 5: # if the position counter has 5 digits (i.e. ffname is a slice file not a max file) 
                ffcomponents[-2] = ffcomponents[-2][:-4]     # then we cut off the position counter (because the BF does not have one)
            bfname = "_".join(["BF", ffcomponents[-2], ffcomponents[-1]])
            bf = join(path, bfname)
            ff = join(path, ffname)
            out = join(output_prefix, ffname[:-5])
            s = "%s -b %s -f %s -p %s -o %s" % (cellid, bf, ff, options_fn, out)
            print "External call:", s
            # The following may not work if the pathname is 'complicated' (e.g. contains dots).
            # Try moving the cell executable to a 'nicely' named directory in this case or rename path.
            call(s.split())
    print "Finished running Cell-ID."
        
        
def load_fiji_results_and_create_mappings(path=join(SIC_ROOT, SIC_PROCESSED), headers=FIJI_HEADERS):
    '''Load FIJI results and create mappings'''
    print "----------------------------------------------------"
    print "Loading FIJI results and creating mappings..."
    l = listdir(path)
    s = set() 
    for i in sorted(l):
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF
        # loop through all .xls files
        if not i.find(".xls") == -1:
            f = open(join(path, i), 'r')
            ls = f.readlines()
            
            # old version:
            #for line in ls:
            # an error suddenly appeared one day caused by this point, perhaps triggered by a FIJI update
            for line in ls[1:]:
                s.add(tuple(line.split()))
                # A problem is a space in the label
                #  	Label	XM	YM
                #1	Sic1_GFP3_142min_1_w2NIBA2.TIF-avg.tif	327.264706	13.500000
    # headers are set manually here

    d = pickle.load(file(join(path, SIC_DATA_PICKLE)))
    tempd = {
        "headers" : headers,
        "data" : s
    }
    d.update(tempd)
    pickle.dump(d, file(join(path, SIC_DATA_PICKLE), "w"))

    print "Finished loading FIJI results and creating mappings."
    return (headers, s)


def find_index(ind_desc='', headers=()):
    for i in range(len(headers)):
        if not headers[i].find(ind_desc) == -1:
            return i
    raise Exception(" !: Index description not found in headers!")

    
def create_mappings_filename2pixel_list(ds, path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Create mappings filename2pixel list'''
    print "----------------------------------------------------"
    print "Creating mappings filename2pixel list..."
    headers, data = ds
    res = {}    
    for l in data:
        label = l[find_index("Label", headers)]
        x = int(float(l[find_index("XM", headers)]))
        y = int(float(l[find_index("YM", headers)]))
        #label = label[:-8]
        if res.has_key(label):
            tl = res[label]
            tl.append((x, y))
            res[label] = tl
        else:
            res[label] = [(x, y)]

    d = pickle.load(file(join(path, SIC_DATA_PICKLE)))
    tempd = {
        "filename2pixel_list" : res
    }
    d.update(tempd)
    pickle.dump(d, file(join(path, SIC_DATA_PICKLE), "w"))

    print "Finished creating mappings filename2pixel list."
    return res


def load_cellid_files_and_create_mappings_from_bounds(
        filename2pixellist,
        original_name2cellid_name,
        path = join(SIC_ROOT, SIC_PROCESSED)
    ):
    '''Load cellid files and create mappings from bounds'''
    print "--------------------------------------------------------"
    print "Loading cellid files and create mappings from bounds..."
    
    l = listdir(path)
    filename2cells = {}         # mapping of {origin_filename : [cell_ids of pixels containing a dot or -1 for pixels containing no dot]} 
    cellid_name2original_name = dict((v, k) for k, v in original_name2cellid_name.iteritems())
    filename2cell_number = {}   # mapping of filename to the number of discovered cells
    filename2hist = {}          # mapping of filename to hist
    
    for i in sorted(l):
        # files containing cell BOUNDs
        if i.find("BOUND") != -1 and i.find("GFP") != -1:
            print "Processing:", i
            cellid2center = {}    # mapping of {cellid : (x, y, pixelcount)} where x, y will be center-of-mass coordinates
            # now we find pixels interesting for our file
            cellid_filename = i[:-10] # e.g. cellid_filename = "GFP_P0_T30.tif", cutting off "_BOUND.txt" 
            origin_filename = cellid_name2original_name[cellid_filename].replace("NIBA.TIF"+CELLID_FP_TOKEN, "NIBA.TIF-max.tif",) # e.g. origin_filename = "Sic1_GFP3_30min_3_w2NIBA.TIF-max.tif"
            filename2cells[origin_filename] = []
            cell_nb = set() # keeps track of the cellids per BOUND file
            
            f = open(join(path, i), "r")
            # reading the boundary position for each cell
            for line in f.readlines():
                ls = line.split()
                if len(ls) == 3:
                    x, y, cellid = map(int, ls) # row of BOUND file converted to int: x(pixel), y(pixel), cellID
                    if cellid2center.has_key(cellid):
                        (ox, oy, nb) = cellid2center[cellid]
                        cell_nb.add(cellid)
                        cellid2center[cellid] = (ox+x, oy+y, nb+1)
                    else:
                        cellid2center[cellid] = (x, y, 1)
            f.close()
            
            # finding cell centers by normalizing the sum of the position vectors (divide by pixel count)
            for cid, val in cellid2center.iteritems():
                cellid2center[cid] = (val[0]/float(val[2]), val[1]/float(val[2]), val[2])
            
            # finding to which cell belongs a point
            # the following has_key() statement had to be inserted because certain .tif files do not run under the find_dots.ijm macro and would otherwise generate a key error here.
            if filename2pixellist.has_key(origin_filename):
                search_px = filename2pixellist[origin_filename]
                for px in search_px:
                    hit = False
                    # for each pixel px in the search_px list, check whether it is within distance RAD of one of the cell centers
                    # if this is the case, record a hit and continue with next pixel
                    for cid, centercoord in cellid2center.iteritems():
                        if pow((px[0] - centercoord[0]), 2) + pow((px[1] - centercoord[1]), 2) < RAD2: 
                            filename2cells[origin_filename].append(cid)
                            hit = True
                            break
                    if not hit:
                        filename2cells[origin_filename].append(-1)

            #filename2cells[origin_filename] = filename2cells[origin_filename] # + [-1] * missed #(len(search_px) - len(filename2cells[origin_filename])) # unnecessary
            #print filename2cells[origin_filename]
            
            # at this point, filename2cells[origin_filename] is a list of cell_ids or -1 with length of the list = number of pixels in origin_filename
            # now, the original author decides to repurpose this variable to contain something completely different...
            # ... which makes the code not especially easy to read
            
            # aggregate the cells histogram
            for orig_filename, cellid_list in filename2cells.iteritems():
                b = {}
                for cell in cellid_list:
                    b[cell] = b.get(cell, 0) + 1
                filename2cells[orig_filename] = b
            # at this point, filename2cells[origin_filename] becomes = {cellid or -1 : count of dot_pixels} with length of the dict = number of cell_ids in origin_filename + 1 
            #print "filename2cells[origin_filename] =", filename2cells[origin_filename]
            
            # make histogram
            d = filename2cells[origin_filename]
            td = dict()
            if d.has_key(-1):
                not_found = d.pop(-1) # this makes not_found = number of dot_pixels outside of cells AND removes the key:value pair from the dict d!  
            else:
                not_found = 0
            for cid, j in d.iteritems():
                td[j] = td.get(j, 0) + 1
            filename2hist[origin_filename] = (td, not_found) # ({count:number_of_cells_with_count}, not_found)
            #print "filename2hist[origin_filename] =", filename2hist[origin_filename] 
            
            # cell number
            filename2cell_number[origin_filename] = len(cell_nb)
            
    du = pickle.load(file(join(path, SIC_DATA_PICKLE)))
    tempd = {
        "filename2cells" : filename2cells,
        "filename2hist" : filename2hist,
        "filename2cell_number" : filename2cell_number,
    }
    du.update(tempd)
    pickle.dump(du, file(join(path, SIC_DATA_PICKLE), "w"))

    print "Finished loading cellid files and creating mappings from bounds."
    return filename2cells, filename2hist, filename2cell_number    


def cluster_with_spotty(path=join(SIC_ROOT, SIC_PROCESSED), spotty=SIC_SPOTTY, G=GMAX):
    '''Apply spotty (R script) for clustering pixels into dots (better results than FIJI)'''
    print "--------------------------------------------------------"
    print "Clustering with", spotty.split('/')[-1], '...'

    xc = 0
    yc = 0

    l = listdir(path)
    for fn in sorted(l):
        if fn.find("INT") != -1:
            print "Spotty calling:", fn
            #call(['Rscript', spotty, '--args', str(xc), str(yc), join(path, fn)])         # old, works for spotty.R
            call(['Rscript', spotty, '--args', str(xc), str(yc), str(G), join(path, fn)])  # new, works for spottyG.R
    print "Finished with clustering."


def cluster_with_median(path=join(SIC_ROOT, SIC_PROCESSED), G=GMAX):
    '''Apply median clustering (R script) for clustering pixels into dots'''
    print "--------------------------------------------------------"
    print "Clustering with", SIC_MEDIAN.split('/')[-1], '...'

    xc = 0
    yc = 0

    l = listdir(path)
    for fn in sorted(l):
        if fn.find("INT") != -1:
            print "Median clustering:", fn
            call(['Rscript', SIC_MEDIAN, '--args', str(xc), str(yc), str(G), join(path, fn)])  # new, works for spottyG.R
            
    print "Finished with clustering."


def aggregate_spots(o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Aggregate all spots in current directory into matrix and write into one .csv file'''
    print "--------------------------------------------------------"
    print "Aggregating spots..."
    outfile = join(path, "all_spots.xls")
    if exists(outfile): os.remove(outfile)
    
    n2o = dict([[v,k] for k,v in o2n.items()]) # inverts o2n dictionary

    with open(outfile, "a") as outfile:
        # Write file header
        outfile.write("\t".join(["FileID", "CellID", "x", "y", "pixels", "f.tot", "f.sig", "f.median", "f.mad", "RNA_molecules", "time", "FileID_old"]))
        outfile.write("\n")
    
        l = listdir(path)
        spots = []
        newspots = []
        for filename in sorted(l):
            if filename.find("SPOTS") != -1:
                print "Spotty file found:", filename
                f = open(join(path, filename), 'r')
                ls = f.readlines()
                for line in ls[1:]: # we start at 1 because we do not need another header
                    splitline = line.split(" ")
                    splitline.insert(0, splitline[-1].strip()) # fetches last item (here: file ID) and prepends
                    splitline.pop()
                    splitline.append(str(n_RNA(float(splitline[6]))))
                    time = re.search("[0-9]+", splitline[0].split("_")[-1]).group(0) # this is the time in minutes 
                    splitline.append(time)
                    splitline.append(n2o[splitline[0]+".tif"])
                    #print splitline
                    # for the matrix, strings are converted into ints and floats
                    spotlist = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]),\
                                float(splitline[4]), float(splitline[5]), float(splitline[6]), float(splitline[7]),\
                                float(splitline[8]), n_RNA(float(splitline[6])), float(time), n2o[splitline[0]+".tif"]]
                    # note that currently n_RNA depends on the subtracted signal splitline[6]. This can be changed any time.
                    # this is: spotlist = [FileID, CellID, x, y, pixels, f.tot, f.sig, f.median, f.mad, n_RNA, time, FileID_old]
                    
                    #newspot = spot.spot(splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), float(splitline[4]), float(splitline[5])) # TODO: work in progress
                    spots.append(spotlist)
                    #newspots.append(newspot) # TODO: work in progress
                    outfile.write("\t".join(splitline[:]))
                    outfile.write("\n")
    outfile.close()
    print "Finished aggregating spots."
    
    d = pickle.load(file(join(path, SIC_DATA_PICKLE)))
    tempd = {
        "spots" : spots
    }
    d.update(tempd)
    pickle.dump(d, file(join(path, SIC_DATA_PICKLE), "w"))

    return spots


def replace_decimal_separators(path=join(SIC_ROOT, SIC_PROCESSED)):
    print "--------------------------------------------------------"
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

    
def rename_dirs(origdir = SIC_ORIG, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "--------------------------------------------------------"
    print "Duplicating processed directory."
    currentdaytime = datetime.datetime.now()
    currentdaytimestring = '_'+origdir+'_' + '%04d' % getattr(currentdaytime, 'year') + '%02d' % getattr(currentdaytime, 'month') + '%02d' % getattr(currentdaytime, 'day') + '_' + '%02d' % getattr(currentdaytime, 'hour') + '%02d' % getattr(currentdaytime, 'minute') + '%02d' % getattr(currentdaytime, 'second')
    copytree(path, path+currentdaytimestring)


def make_plots(spots, d):
    pf.histogram_intensities(spots)
    pf.scatterplot_intensities(spots)
    pf.spots_per_cell_distribution(spots)
    #pf.plot_time2ratio_between_one_dot_number_and_cell_number(d)
    pl.show()
    

def run_setup():
    prepare_structure()
    copy_NIBA_files_to_processed()
    link_DIC_files_to_processed()
    #run_fiji_standard_mode()
    run_fiji_standard_mode_select_quarter_slices()
    
    toc = time.time()
    print "Time since program started:", toc - tic, "s"
    #color_processed_NIBA_files()
    

def run_analysis():
    niba2dic, dic2niba, o2n = create_map_image_data()
    create_symlinks(o2n)
    prepare_b_and_f_single_files(niba2dic, o2n)

    run_cellid()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    headers, data = load_fiji_results_and_create_mappings()
    filename2pixel_list = create_mappings_filename2pixel_list((headers, data))
    filename2cells, filename2hist, filename2cell_number = load_cellid_files_and_create_mappings_from_bounds(filename2pixel_list, o2n)
    cluster_with_spotty()
    #cluster_with_median()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    spots = aggregate_spots(o2n)

    d = {
        "niba2dic" : niba2dic,
        "dic2niba" : dic2niba,
        "o2n" : o2n,
        "filename2pixel_list" : filename2pixel_list,
        "headers" : headers,
        "data" : data,
        "filename2cells" : filename2cells,
        "filename2hist" : filename2hist,
        "filename2cell_number" : filename2cell_number,
        "spots" : spots
    }
    pickle.dump(d, file(join(SIC_ROOT, SIC_PROCESSED, SIC_DATA_PICKLE), "w"))

    toc = time.time()
    print "Time since program started:", toc - tic, "s"
    
    make_plots(spots, d) # TODO: das geht auch ohne spots, denn d['spots'] == spots

    # returns results as a dict, in case they are needed somewhere
    return d


def run_all_steps_standard_mode():
    run_setup()
    d = run_analysis()

    
def load_and_plot():
    d = pickle.load(file(join(SIC_ROOT, SIC_RESULTS, SIC_DATA_PICKLE)))
    make_plots(d['spots'], d)  # TODO: das geht auch ohne spots, denn d['spots'] == spots
    

if __name__ == '__main__':
    #load_and_plot()
    run_all_steps_standard_mode()
    #cluster_with_median()
    #rename_dirs()