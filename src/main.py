#!/usr/bin/env python
"""Processing of SIC data.

DATA DESCRIPTION:
I assume that the original files are named in such a way:
Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w[1|2][DIC|NIBA].TIF

* Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w[1|2]DIC.TIF
contain the information from brightfield. These are stacks. 

* Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w[2|1]NIBA.TIF
contain the information from fp channel. These are stacks. In the images clusters of fp could be observed and we assume that they correspond to a single particle.

* [0-9]+min[a-Z]* describes the time of the experiment


DATA SETUP
1. Sorting files and preparing of symlinks. The purpose of this is to have both DIC and NIBA files in the $SIC_ROOT/$SIC_PROCESSED directory.
a/ orig files are placed in $SIC_ROOT/orig
* initial setup
b/ NIBA files are copied to $SIC_ROOT/processed
* copy_NIBA_files_to_processed
c/ DIC files are linked to $SIC_ROOT/$SIC_PROCESSED
* link_DIC_files_to_processed


2. Editing NIBA files.
The purpose of this operation is to convert NIBA stacks to 2D binary mask images
and to create a tab-delimited file (*.xls) containing the positions of centers of dots.
These operations are performed with FIJI batch processing script:
* $SIC_ROOT/$SIC_SCRIPTS/$SIC_FIND_DOTS_SCRIPT 
run it on a folder:
$SIC_ROOT/$SIC_PROCESSED (contains NIBA files)


3. Coloring the processed NIBA files
Only mask colors are colored. The image is processed in such a way that the dots are marked red on black background.
* color_processed_NIBA_files


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

from global_vars import SIC_ROOT, SIC_ORIG, SIC_SCRIPTS, SIC_PROCESSED,\
    SIC_RESULTS, SIC_LINKS, FIJI_STANDARD_SCRIPT, SIC_FIJI, PARAM_DICT,\
    SIC_CELLID_PARAMS, FIJI_TRACK_SCRIPT, SIC_FILE_CORRESPONDANCE, SIC_CELLID,\
    SIC_BF_LISTFILE, SIC_F_LISTFILE, POSI_TOKEN, FIJI_HEADERS, GMAX, SIC_SPOTTY,\
    NIBA_ID, DIC_ID, CELLID_FP_TOKEN, TIME_TOKEN, RAD2, n_RNA, SIC_DATA_PICKLE


# Module documentation variables:
__authors__="""Szymon Stoma, Martin Seeger"""
__contact__=""
__license__="Cecill-C"
__date__="2011"
__version__="0.9"
__docformat__= "restructuredtext en"


import time
tic = time.time()
import re
import os
from os import listdir, rename, path, mkdir, access, name, R_OK, F_OK
from shutil import copyfile, rmtree
from os.path import join, split, exists
from copy import deepcopy
from subprocess import call
import pylab as pl
import pickle
if os.name != 'nt':
    from os import symlink #@UnresolvedImport
elif os.name == 'nt':
    import pywintypes #@UnresolvedImport @UnusedImport
    from win32com.client import Dispatch #@UnresolvedImport @UnusedImport

import spot
import set_cell_id_parameters as scip
import plot_functions as pf 


def prepare_structure(path=SIC_ROOT,
                      skip=[SIC_ORIG, SIC_SCRIPTS, "orig", "orig1", "orig2", "orig3", "orig4", "orig5", "orig6"],
                      create_dirs=[SIC_PROCESSED, SIC_RESULTS, SIC_LINKS],
                      check_for=[join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT),
                        join(SIC_ROOT, SIC_ORIG)]
                      ):
    '''Remove obsolete directories, create required directories and check requirements'''
    print "Preparing structure..."
    def remove_old_dirs(path, skip):
        print "Working in path:", path
        l = listdir(path)
        for i in sorted(l):
            # removing everything which is not a SIC_ORIG or SIC_SCRIPTS
            if i not in skip and i[:3]!='orig':
                rmtree(join(path, i))
                print "Removing:", join(path, i)
            else:
                print "Skipping:", join(path, i)
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
        # TODO: do similar for FIJI_TRACK_SCRIPT
        try:
            print "Copying", join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), "to", join(os.path.dirname(SIC_FIJI), "macros", FIJI_STANDARD_SCRIPT)
            copyfile(join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), join(os.path.dirname(SIC_FIJI), "macros", FIJI_STANDARD_SCRIPT))
        except:
            print "Unable to copy FIJI macro."
        print "Finished checking requirements."

    remove_old_dirs(path, skip)
    create_required_dirs(path, create_dirs)
    check_reqs(check_for)
    scip.set_parameters(PARAM_DICT, join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS))
    with open(join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS), 'r') as pfile:
        print "Using cell-ID parameters:"
        print pfile.read()
    print "Finished preparing structure."
    

def copy_NIBA_files_to_processed(path=join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED), niba=NIBA_ID):
    '''Copy NIBA files to processed'''
    print "Copying NIBA files to processed..."
    l = listdir(path)
    for i in sorted(l):
        # Only file names containing NIBA_ID and not containing 'thumb' are copied
        if i.find(niba) != -1 and i.find('thumb') == -1:
            print "Copying", join(path,i), "to", join(dest,i)
            copyfile(join(path,i), join(dest,i))
    print "Finished copying NIBA files to processed."


def link_DIC_files_to_processed(path = join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED), dic=DIC_ID):
    '''Link DIC files to processed'''
    print "Linking DIC files to processed..."
    l = listdir(path)
    for i in sorted(l):
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA][ index3].TIF
        if i.find(dic) != -1 and i.find('thumb') == -1: # link only files whose name contains DIC_ID and not thumb
            print "Linking", join(path, i), "to", join(dest, i)
            if os.name != 'nt':
                symlink(join(path, i), join(dest, i))
            else:
                # TODO: for Windows, create shortcuts instead of symlinks
                print "Operating system is Windows, calls to symlink will not work."
    print "Finished linking DIC files to processed."
        

def run_fiji_standard_mode(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), niba=NIBA_ID):
    '''Run FIJI for stack projection'''
    print "Running FIJI..."
    l = listdir(path)
    for fn in sorted(l):
        print "Looking in:", fn
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF-mask.tif
        if fn.find(niba+".TIF") != -1: # run fiji only for files whose name contains NIBA_ID+".TIF"
            s = "%s %s -macro %s -batch" % (SIC_FIJI, join(path, fn), script_filename)
            print "External call:", s
            #sucht unter Windows nur in SIC_FIJI/macros/
            call([SIC_FIJI, join(path, fn), "-macro", script_filename, "-batch"])
    print "Finished running FIJI."


def run_fiji_track_spot_mode(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_TRACK_SCRIPT)):
    '''Run FIJI for tracking spots'''
    print "Running FIJI..."
    l = listdir(path)
    for fn in sorted(l):
        print "Looking in:", fn
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF-mask.tif
        if fn.find(NIBA_ID+".TIF") != -1: # run fiji only for files whose name contains NIBA_ID+".TIF"
            s = "%s %s -macro %s -batch" % (SIC_FIJI, join(path, fn), script_filename)
            print "External call:", s
            #sucht unter Windows nur in SIC_FIJI/macros/
            call([SIC_FIJI, join(path, fn), "-macro", script_filename, "-batch"])
    print "Finished running FIJI."


def create_map_image_data(filename=join(SIC_ROOT, SIC_PROCESSED, SIC_FILE_CORRESPONDANCE), path=join(SIC_ROOT, SIC_PROCESSED), niba=NIBA_ID, dic=DIC_ID):
    '''Create map image data'''
    print "Creating map image data..."
    f = open(filename, 'w')
    l = listdir(path)
    o2n = {}
    niba2dic = {}
    dic2niba = {}

    # creating new names and maps: NIBA <-> DIC
    for i in sorted(l):
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF
        
        # First do the niba + ".TIF" files (using the -max.tif files as images)
        if i.endswith(niba + ".TIF"):
            print "Mapping:", i
            nfn = i.split("_")                           # split filename at '_'
            try:
                time = re.search("[0-9]+", nfn[-3]).group(0) # this is the substring of nfn[-3] containing 1 or several decimal digits ('min' is ignored)
            except:
                time = "0" 
            if nfn[-2] == "": pos = "0"
            else: pos = nfn[-2]
            nn = "GFP_" + POSI_TOKEN + str(pos) + "_" + TIME_TOKEN + time + ".tif" # new name
            o2n[i + CELLID_FP_TOKEN] = nn
            #corresponding_dic = nfn[0] + "_" + nfn[1] + "_" + nfn[2] + "_" + nfn[3] + "_" + re.sub(" [0-9]", "", nfn[4].replace(niba[1:],dic[1:])) # old, works on conforming filenames 
            nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba[1:], dic[1:]).replace(".tif", ".TIF"))
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
            nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(niba[1:], dic[1:]).replace("-"+slice_counter, '').replace(".tif", ".TIF"))
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
    
    print "Finished creating map image data."
    return niba2dic, dic2niba, o2n


def create_symlinks(old2new, sourcepath=join(SIC_ROOT, SIC_PROCESSED), targetpath=join(SIC_ROOT, SIC_LINKS)):
    '''Create symlinks'''
    # TODO: Create Windows version
    print "Creating symlinks..."
    for old in old2new.keys():
        print "Linking", old, "to", old2new[old]
        try:
            symlink(join(sourcepath, old), join(targetpath, old2new[old]))
        except:
            print "Please check whether original filenames allow for unique cell ID filenames."
    print "Finished creating symlinks."


def prepare_b_and_f_single_files(niba2dic, o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
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
    print "Finished loading FIJI results and creating mappings."
    return (headers, s)


def find_index(ind_desc='', headers=()):
    for i in range(len(headers)):
        if not headers[i].find(ind_desc) == -1:
            return i
    raise Exception(" !: Index description not found in headers!")

    
def create_mappings_filename2pixel_list(ds):
    '''Create mappings filename2pixel list'''
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
    print "Finished creating mappings filename2pixel list."
    return res


def load_cellid_files_and_create_mappings_from_bounds(
        filename2pixellist,
        original_name2cellid_name,
        path = join(SIC_ROOT, SIC_PROCESSED),
        cellid_results_path=join(SIC_ROOT, SIC_LINKS) # not used?
    ):
    '''Load cellid files and create mappings from bounds'''
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
    print "Finished loading cellid files and creating mappings from bounds."
    return filename2cells, filename2hist, filename2cell_number    


def cluster_with_R(path=join(SIC_ROOT, SIC_PROCESSED), G=GMAX):
    '''Apply spotty (R script) for clustering pixels into dots (better results than FIJI)'''
    print "Clustering with", SIC_SPOTTY.split('/')[-1], '...'

    xc = 0
    yc = 0

    l = listdir(path)
    for fn in sorted(l):
        if fn.find("INT") != -1:
            print "Spotty calling:", fn
            #call(['Rscript', SIC_SPOTTY, '--args', str(xc), str(yc), join(path, fn)])         # old, works for spotty.R
            call(['Rscript', SIC_SPOTTY, '--args', str(xc), str(yc), str(G), join(path, fn)])  # new, works for spottyG.R
            
    print "Finished with clustering."


def aggregate_spots(o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Aggregate all spots in current directory into matrix and write into one .csv file'''
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
                    
                    newspot = spot.spot(splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), float(splitline[4]), float(splitline[5])) # TODO: work in progress
                    spots.append(spotlist)
                    newspots.append(newspot) # TODO: work in progress
                    outfile.write("\t".join(splitline[:]))
                    outfile.write("\n")
    outfile.close()
    print "Finished aggregating spots."
    return spots


def aggregate_and_track_spots(spots, niba2dic):
    '''
    Aggregate spots and group them together if they might be the same. 
    Criteria for spot identification:
    1. Spots must be in the same cell (have the same CellID)
    2. Between adjacent slices, spots must not move more than moved = sqrt(CRIT_DIST2_FROM_PREV)
       The point with minimum moved (if below threshold) is identified with the predecessor
    3. One of the identified spots must lie with sqrt(CRIT_DIST2_FROM_MAX) of a spot in the max projection
    '''
    CRIT_DIST2_FROM_PREV = 8*8 # maximum distance^2 from spot in previous slice in order to be identified
    CRIT_DIST2_FROM_MAX = 2*2  # maximum distance^2 from spot in max projection in order to be identified
    
    def dist2((x1, y1), (x2, y2)): 
        # square of Euclidean distance
        return (x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)
    
    def slice_distance(spot1, spot2):
        '''Signed distance in slices between spots'''
        slice1 = int(spot1[0].split("_")[1][-4:]) # slice number of spot1
        slice2 = int(spot2[0].split("_")[1][-4:]) # slice number of spot2
        return slice2-slice1
    
    def isWithinDistance(spot1, spot2):
        # TODO: this should be enhanced by CRIT_DIST2_FROM_MAX criterion 
        if dist2((spot1[2], spot1[3]), (spot2[2], spot2[3])) < CRIT_DIST2_FROM_PREV:
            return True
        else:
            return False
    
    def isClosestSuccessor(spot1, spot2, spots):
        # is spot2 the closest (minimum distance) successor (on the next slice) of spot 1
        if slice_distance(spot1, spot2) == 1:
            if dist2((spot1[2], spot1[3]), (spot2[2], spot2[3])) == min([dist2((spot1[2], spot1[3]), (spot[2], spot[3])) for spot in spots\
                                                                         if spot!=spot1 and slice_distance(spot1, spot) == 1]):
                return True
        else:
            return False
    
    def isClosestPredecessor(spot1, spot2, spots):
        # is spot2 the closest (minimum distance) predecessor (on the previous slice) of spot 1
        if slice_distance(spot1, spot2) == -1:
            if dist2((spot1[2], spot1[3]), (spot2[2], spot2[3])) == min([dist2((spot1[2], spot1[3]), (spot[2], spot[3])) for spot in spots\
                                                                         if spot!=spot1 and slice_distance(spot1, spot) == -1]):
                return True
        else:
            return False

    def onTrajectoryNew(spot1, spot2, spots):
        if spot1 == spot2:
            return 'Y' # yes
        elif dist2((spot1[2], spot1[3]), (spot2[2], spot2[3])) >= slice_distance(spot1, spot2)*slice_distance(spot1, spot2)*CRIT_DIST2_FROM_PREV:
            return 'N' # no
        elif isWithinDistance(spot1, spot2) and (isClosestSuccessor(spot1, spot2, spots) or isClosestSuccessor(spot2, spot1, spots))\
        and (isClosestPredecessor(spot1, spot2, spots) or isClosestPredecessor(spot2, spot1, spots)):
            return 'Y' # yes
        else:
            return 'M' # maybe
    
    def onTrajectory(spot1, spot2, spots):
        '''
        Functional programming implementation of spot trajectory:
        Two spots are on the same trajectory if one of the following is fulfilled:
        1. they are identical
        2. they are closest AND within critical distance AND on adjacent slices
        3. they share a common trajectory with a third, distinct spot
        '''
        if spot1 == spot2:
            return True
        elif dist2((spot1[2], spot1[3]), (spot2[2], spot2[3])) >= slice_distance(spot1, spot2)*slice_distance(spot1, spot2)*CRIT_DIST2_FROM_PREV:
            return False
        elif isWithinDistance(spot1, spot2) and (isClosestSuccessor(spot1, spot2, spots) or isClosestSuccessor(spot2, spot1, spots))\
        and (isClosestPredecessor(spot1, spot2, spots) or isClosestPredecessor(spot2, spot1, spots)):
            return True
        else:
            for spot3 in spots:
                if slice_distance(spot1, spot3)*slice_distance(spot3, spot2)>0: # i.e. only consider spots that are between slices of spot1 and spot2 
                    #print "\t\tRecursing on spot:", spot3
                    if len(spots)<=2:
                        return False 
                    spots1 = deepcopy(spots) 
                    spots2 = deepcopy(spots) 
                    if spot3!=spot1 and spot3!=spot2:
                        return (onTrajectory(spot3, spot1, spots2) and onTrajectory(spot3, spot2, spots1)) or (onTrajectory(spot1, spot3, spots2) and onTrajectory(spot2, spot1, spots1))
            return False
    
    stacks = sorted(list(set([niba2dic[spot[-1]] for spot in spots]))) # spot[-1] is the old file ID (can be -max.tif or belonging to slice)
    
    for stack in stacks:
        spotted_cells = sorted(list(set([spot[1] for spot in spots if niba2dic[spot[-1]]==stack and spot[-1].find(CELLID_FP_TOKEN)!=-1])))
        # condition 1 selects only cells in the current stack
        # condition 2 makes sure that only spots contained in the max projections are considered real (i.e. not those that are only in the slices)

        max_projection_spots = [spot for spot in spots if niba2dic[spot[-1]]==stack and spot[-1].find(CELLID_FP_TOKEN)!=-1]
        # this is the 'master spot list' containing only spots that are visible on the max projection

        for spotted_cell in spotted_cells:
            local_spots = [spot for spot in spots if niba2dic[spot[-1]]==stack and spot[1]==spotted_cell and spot not in max_projection_spots]
            # these are all spots in slices (not in max projection) in a given spotted cell in a given stack
            print "---------------------------------------------"
            print "Considering cell", spotted_cell, "in stack", stack
            print "---------------------------------------------"
            print "The following spots were found:"
            for spot in local_spots:
                print spot
            
            '''
            print "---------------------------------------------"
            num_spots = len(local_spots)                
            
            # Initialisation
            trajectory_matrix = [['M' for k in range(num_spots)] for l in range(num_spots)]
            
            for k in range(num_spots):
                print trajectory_matrix[k]
            print "---------------------------------------------"
            
            for k, spotk in enumerate(local_spots):
                for l, spotl in enumerate(local_spots):
                    trajectory_matrix[k][l] = onTrajectory(spotk, spotl, local_spots)
                    trajectory_matrix[l][k] = trajectory_matrix[k][l]

            for k in range(num_spots):
                print trajectory_matrix[k]
            print "---------------------------------------------"

            trajectory_matrix_string = "".join(trajectory_matrix[i][j] for i in range(num_spots) for j in range(num_spots))
            print trajectory_matrix_string.find('M') != -1 # are positions still undecided?
            '''

            '''
            for spot1 in local_spots:
                for spot2 in local_spots:
                    print "---------------------------------------------"
                    print spot1
                    print spot2
                    print "isWithinDistance(spot1, spot2):", isWithinDistance(spot1, spot2)
                    print "isClosestSuccessor(spot1, spot2, spots) or isClosestSuccessor(spot2, spot1, spots):", isClosestSuccessor(spot1, spot2, spots) or isClosestSuccessor(spot2, spot1, spots)
                    print "isClosestPredecessor(spot1, spot2, spots) or isClosestPredecessor(spot2, spot1, spots):", isClosestPredecessor(spot1, spot2, spots) or isClosestPredecessor(spot2, spot1, spots)
                    print "onTrajectory(spot1, spot2, local_spots):", onTrajectory(spot1, spot2, local_spots)
                    raw_input('Press Enter...')
            '''
            

            for spot1 in local_spots:
                print "---------------------------------------------"
                print spot1
                for spot in local_spots:
                    if onTrajectory(spot, spot1, local_spots) or onTrajectory(spot1, spot, local_spots):
                        print "\t", spot
            print "---------------------------------------------"


            print "---------------------------------------------"
            spot1 = ['GFP_P020005_T0', '8', 569.549866272399, 597.113272100496, 214.0, 534373.0, 208451.0, 1523.0, 252.042, 270.88895334572567, 0.0, 'Stack_02_w2NIBA-0005.tif']
            spot2 = ['GFP_P020006_T0', '8', 569.365923776806, 596.730425964634, 166.0, 425722.0, 162612.0, 1585.0, 257.2311, 211.31966016692243, 0.0, 'Stack_02_w2NIBA-0006.tif']
            print isWithinDistance(spot1, spot2)
            print (isClosestSuccessor(spot1, spot2, local_spots) or isClosestSuccessor(spot2, spot1, local_spots))
            print (isClosestPredecessor(spot1, spot2, local_spots) or isClosestPredecessor(spot2, spot1, local_spots))
            print onTrajectory(spot1, spot2, local_spots)  

            
            '''
            for spot1ID, spot1 in enumerate(local_spots):
                sliceID[spot1ID] = int(spot1[0].split("_")[1][-4:])
            for spot1ID, spot1 in enumerate(local_spots):
                for spot2ID, spot2 in enumerate(local_spots):
                    if spot2ID > spot1ID and sliceID[spot2ID] == sliceID[spot1ID]+1: # to make sure spots are compared only once
                        if isWithinDistance(spot1, spot2) and isClosestSuccessor(spot1, spot2, local_spots):
                            print "\t", "---------------------------------------------"
                            print "\t", "Found matching spots:"
                            print "\t", sliceID[spot1ID], spot1ID, spot1
                            print "\t", sliceID[spot2ID], spot2ID, spot2
                            print "\t", dist2((spot1[2], spot1[3]), (spot2[2], spot2[3]))
                        else:
                            print "\t", "---------------------------------------------"
                            print "\t", "Found non-matching spots:"
                            print "\t", sliceID[spot1ID], spot1ID, spot1
                            print "\t", sliceID[spot2ID], spot2ID, spot2
                            print "\t", dist2((spot1[2], spot1[3]), (spot2[2], spot2[3]))
            '''


def make_plots(spots, d):
    pf.histogram_intensities(spots)
    pf.scatterplot_intensities(spots)
    pf.spots_per_cell_distribution(spots)
    pf.plot_time2ratio_between_one_dot_number_and_cell_number(d)
    pl.show()
    

def run_setup():
    prepare_structure()
    copy_NIBA_files_to_processed()
    link_DIC_files_to_processed()
    run_fiji_standard_mode()

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
    cluster_with_R()

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
    pickle.dump(d, file(join(SIC_ROOT, SIC_RESULTS, SIC_DATA_PICKLE), "w"))

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
    

def run_stack_spot_tracker():
    prepare_structure()
    copy_NIBA_files_to_processed()
    link_DIC_files_to_processed()
    run_fiji_track_spot_mode()
    niba2dic, dic2niba, o2n = create_map_image_data()
    create_symlinks(o2n)
    prepare_b_and_f_single_files(niba2dic, o2n)
    run_cellid()
    headers, data = load_fiji_results_and_create_mappings()
    filename2pixel_list = create_mappings_filename2pixel_list((headers, data))
    filename2cells, filename2hist, filename2cell_number = load_cellid_files_and_create_mappings_from_bounds(filename2pixel_list, o2n)
    cluster_with_R()
    spots = aggregate_spots(o2n)
    aggregate_and_track_spots(spots, niba2dic)
    toc = time.time()
    print "Time since program started:", toc - tic, "s"


if __name__ == '__main__':
    #load_and_plot()
    run_all_steps_standard_mode()
    #run_stack_spot_tracker()
