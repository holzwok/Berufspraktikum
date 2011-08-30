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
The resulting file needs to be saved as:
$SIC_ROOT/$SIC_RESULTS/$SIC_DOTS_COORDS #TODO: not implemented yet?


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
* script: run_analysis #TODO: call the script from python


6. Gathering and processing the data from FIJI and cell-id processing
"""


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
from subprocess import call
import pylab as pl
import pickle
if os.name != 'nt':
    from os import symlink #@UnresolvedImport
elif os.name == 'nt':
    import pywintypes #@UnresolvedImport @UnusedImport
    from win32com.client import Dispatch #@UnresolvedImport @UnusedImport
import plot_functions as pf 
from global_vars import * #@UnusedWildImport


def prepare_structure(path=SIC_ROOT,
                      skip=[SIC_ORIG, SIC_SCRIPTS, "orig", "orig1", "orig2", "orig3", "orig4"],
                      create_dirs=[SIC_PROCESSED, SIC_RESULTS, SIC_LINKS],
                      check_for=[join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT),
                        join(SIC_ROOT, SIC_ORIG),
                        join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)]
                      ):
    '''Remove obsolete directories, create required directories and check requirements'''
    print "Preparing structure..."
    def remove_old_dirs(path, skip):
        print "Working in path:", path
        l = listdir(path)
        for i in sorted(l):
            # removing everything which is not a SIC_ORIG or SIC_SCRIPTS
            if i not in skip:
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
    print "Finished preparing structure."
    

def copy_NIBA_files_to_processed(path=join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED)):
    '''Copy NIBA files to processed'''
    print "Copying NIBA files to processed..."
    l = listdir(path)
    for i in sorted(l):
        # Only file names containing NIBA_ID and not containing 'thumb' are copied
        if i.find(NIBA_ID) != -1 and i.find('thumb') == -1:
            print "Copying", join(path,i), "to", join(dest,i)
            copyfile(join(path,i), join(dest,i))
    print "Finished copying NIBA files to processed."


def link_DIC_files_to_processed(path = join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED)):
    '''Link DIC files to processed'''
    print "Linking DIC files to processed..."
    l = listdir(path)
    for i in sorted(l):
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA][ index3].TIF
        if i.find(DIC_ID) != -1 and i.find('thumb') == -1: # link only files whose name contains DIC_ID and not thumb
            print "Linking", join(path, i), "to", join(dest, i)
            if os.name != 'nt':
                symlink(join(path, i), join(dest, i))
            else:
                # TODO: for Windows, create shortcuts instead of symlinks
                print "Operating system is Windows, calls to symlink will not work."
    print "Finished linking DIC files to processed."
        

def run_fiji_standard_mode(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT)):
    '''Run FIJI for stack projection'''
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


def create_map_image_data( filename=join(SIC_ROOT, SIC_PROCESSED, SIC_FILE_CORRESPONDANCE), path=join(SIC_ROOT, SIC_PROCESSED)):
    '''Create map image data'''
    print "Creating map image data..."
    f = open(filename, 'w')
    l = listdir(path)
    o2n = {}
    niba2dic = {}
    dic2niba = {}
    pos = 0
    # creating new names and maps: NIBA <-> DIC
    for i in sorted(l):
        # file name containing NIBA_ID
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF
        if i.endswith(NIBA_ID + ".TIF"):
            print "Mapping:", i
            nfn = i.split("_")                           # split filename at '_'
            time = re.search("[0-9]+", nfn[-3]).group(0) # this is the substring of nfn[-3] containing 1 or several decimal digits ('min' is ignored)
            nn = "GFP_" + POSI_TOKEN + str(pos) + "_" + TIME_TOKEN + time + ".tif" # new name
            o2n[i + CELLID_FP_TOKEN] = nn
            #corresponding_dic = nfn[0] + "_" + nfn[1] + "_" + nfn[2] + "_" + nfn[3] + "_" + re.sub(" [0-9]", "", nfn[4].replace(NIBA_ID[1:],DIC_ID[1:])) # old, works on conforming filenames 
            nfn[-1] = re.sub(" [0-9]", "", nfn[-1].replace(NIBA_ID[1:], DIC_ID[1:]))
            corresponding_dic = "_".join(nfn) 
            print "Corresponding_dic:", corresponding_dic
            niba2dic[i + CELLID_FP_TOKEN] = corresponding_dic
            dic2niba[corresponding_dic] = [i + CELLID_FP_TOKEN]
            # we have met this DIC first time so we need to add it to the maps
            bff = "BF_" + POSI_TOKEN + str(pos) + "_" + TIME_TOKEN + time + ".tif"
            o2n[corresponding_dic] = bff
            pos += 1
            
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
        symlink(join(sourcepath, old), join(targetpath, old2new[old]))
        print "Linking", old, "to", old2new[old]
    print "Finished creating symlinks."


def prepare_b_and_f_single_files(niba2dic, dic2niba, o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Writing BF and F single files..."
    for i in niba2dic.keys():
        bf = open(join(path, o2n[niba2dic[i]][:-3] + "path"), "w") # we cut out last 3 chars from the file name and replace them by 'path'
        ff = open(join(path, o2n[i][:-3] + "path"), "w")
        #ff.write(path + o2n[i][0] + '\n') #old, buggy! also, pre changing o2n
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
    for i in sorted(l):
        if i.startswith("GFP") and i.endswith(".path"):
            print "Considering file:", i
            bf = join(path, i.replace("GFP", "BF"))
            ff = join(path, i)
            out = join(output_prefix, i[:-5])
            #mkdir(out)
            s = "%s -b %s -f %s -p %s -o %s" % (cellid, bf, ff, options_fn, out) #put_prefix)
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
            # TODO:? (an error suddenly appeared one day caused by this point, presumably triggered by a FIJI update?)
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
        cellid_results_path=join(SIC_ROOT, SIC_LINKS),
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
        outfile.write("\t".join(["FileID", "CellID", "x", "y", "pixels", "f.tot", "f.sig", "f.median", "f.mad", "time", "FileID_old"]))
        outfile.write("\n")
    
        l = listdir(path)
        spots = []
        for filename in l:
            if filename.find("SPOTS") != -1:
                print "Spotty file found:", filename
                f = open(join(path, filename), 'r')
                ls = f.readlines()
                for line in ls[1:]: # we start at 1 because we do not need another header
                    splitline = line.split(" ")
                    splitline.insert(0, splitline[-1].strip()) # fetches last item (here: file ID) and prepends
                    splitline.pop()
                    # for the matrix, strings are converted into ints and floats
                    time = re.search("[0-9]+", splitline[0].split("_")[-1]).group(0) # this is the time in minutes 
                    splitline.append(time)
                    splitline.append(n2o[splitline[0]+".tif"])
                    #print splitline
                    spot = [splitline[0], splitline[1], float(splitline[2]), float(splitline[3]), float(splitline[4]), float(splitline[5]), float(splitline[6]), float(splitline[7]), float(splitline[8]), float(time), n2o[splitline[0]+".tif"]]
                    # this is: spot = [FileID, CellID, x, y, pixels, f.tot, f.sig, f.median, f.mad, time, FileID_old]
                    spots.append(spot)
                    outfile.write("\t".join(splitline[:]))
                    outfile.write("\n")
    outfile.close()
    print "Finished aggregating spots."
    return spots


def make_plots(spots, d):
    pf.histogram_intensities(spots)
    pf.scatterplot_intensities(spots)
    pf.plot_time2ratio_between_one_dot_number_and_cell_number(d)
    pl.show()
    

def run_setup():
    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    prepare_structure()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    copy_NIBA_files_to_processed()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    link_DIC_files_to_processed()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    run_fiji_standard_mode()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"
    #color_processed_NIBA_files()
    

def run_analysis():
    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    niba2dic, dic2niba, o2n = create_map_image_data()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    create_symlinks(o2n)

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    prepare_b_and_f_single_files(niba2dic, dic2niba, o2n)

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    run_cellid()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    headers, data = load_fiji_results_and_create_mappings()

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    filename2pixel_list = create_mappings_filename2pixel_list((headers, data))

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    filename2cells, filename2hist, filename2cell_number = load_cellid_files_and_create_mappings_from_bounds(filename2pixel_list, o2n)

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

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

    toc = time.time()
    print "Time since program started:", toc - tic, "s"

    make_plots(spots, d) # TODO: das geht auch ohne spots, denn d['spots'] == spots

    toc = time.time()
    print "Time since program started:", toc - tic, "s"
    
    # returns results as a dict, in case they are needed somewhere
    return d


def run_all_steps_standard_mode():
    run_setup()
    d = run_analysis()

    
def load_and_plot():
    d = pickle.load(file(join(SIC_ROOT, SIC_RESULTS, SIC_DATA_PICKLE)))
    make_plots(d['spots'], d)  # TODO: das geht auch ohne spots denn d['spots'] == spots
    

def run_stack_cell_tracker():
    prepare_structure()
    copy_NIBA_files_to_processed()
    link_DIC_files_to_processed()
    run_fiji_track_spot_mode()
    

if __name__ == '__main__':
    #load_and_plot()
    #run_all_steps_standard_mode()
    run_stack_cell_tracker()
