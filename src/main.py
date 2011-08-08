#!/usr/bin/env python
"""Processing of SIC data.

DATA DESCRIPTION:
I assume that the original files are named in such a way:
Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w[1DIC|2NIBA].TIF

* Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w1DIC.TIF
contain the information from brightfield. These are stacks. 

* Sic1_GFP3_[0-9]+min[a-Z]*_[0-9]*_w2NIBA.TIF
contain the information from fp channel. These are stacks. In the images clusters of fp could be observed and we assume that they correspond to a single particles A.

* [0-9]+min[a-Z]* describes the time of the experiment

AUTOMATIC RUN:
* run_all_steps

GOALS
The goal is to process the data to obtain the following information:
1. Ratio of single particles A to cell numbers in time.


DATA SETUP
1. Sorting files and preparing of symlinks. The purpose of this is to have both DIC and NIBA files in the $SIC_ROOT/$SIC_PROCESSED directory.
a/ orig files are placed in $SIC_ROOT/orig
* initial setup
b/ NIBA files are copied to $SIC_ROOT/processed
* copy_NIBA_files_to_processed
c/ DIC files are linked to $SIC_ROOT/$SIC_PROCESSED
* link_DIC_files_to_processed


2. Editing NIBA files.
The purpose of this operation is to convert NIBA stacks to 2D binary mask images and to create the tab-delimited file (Result.xsl) containing the positions of centers of dots. These operations are performed with FIJI batch processing script:
* $SIC_ROOT/$SIC_SCRIPTS/create_count_particles_from_stack.ijm  
run it on a folder:
$SIC_ROOT/$SIC_PROCESSED (contains NIBA files)
The resulting file needs to be saved as:
$SIC_ROOT/$SIC_RESULTS/$SIC_DOTS_COORDS

3. Coloring the processed NIBA files
Only mask colors are colored. The image is processed in such a way that the dots are marked red on black background.
* color_processed_NIBA_files

4. Symlinks cont.

5. Finding cells in images.
The purpose of this operation is to create lists of pixels building up each cell in each DIC image. Additionally, to ease the inspection of results the images where each cell is bounded with white circle are generated. To perform this task, cell-id was used, however the source code required editing to access and write the lists into files. Unfotunately to use the cell-id special file name convetion has to be used. Therefore:
a/ symlinks are created in $SIC_ROOT/links
* create_symlinks
b/ cell-id config files with correct name correspondance is created
* prepare_b_and_f_files
c/ cell-id is run and creates files
* script: run_analysis # TODO call the script from python
4. Gathering and processing the data from FIJI and cell-id processing

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA
"""


# Module documentation variables:
__authors__="""Szymon Stoma, Martin Seeger"""
__contact__=""
__license__="Cecill-C"
__date__="2011"
__version__="0.1"
__docformat__= "restructuredtext en"


import re
import os
from os import listdir, rename, path, mkdir, access, name, R_OK, F_OK
from shutil import copyfile, rmtree
from os.path import join, split
from subprocess import call
import matplotlib as pl # TODO: this used to be pylab
import pickle
from scipy import interpolate
import numpy as np
if os.name != 'nt':
    from os import symlink #@UnresolvedImport # TODO: must find symlink replacement for windows
else:
    import pywintypes #@UnresolvedImport @UnusedImport
    from win32com.client import Dispatch


#MACHINE = "sstoma-pokrzywa"
#MACHINE = "sstoma-smeik"
MACHINE = "martin-uschan"
#MACHINE = "MJS Windows"
if MACHINE == "sstoma-smeik":
    SIC_CELLID = "/home/sstoma/svn/sstoma/src/11_01_25_cellId/cell"
    SIC_ROOT = '/local/home/sstoma/images/11-06-18-sic,matthias'
    SIC_FIJI = '/home/sstoma/bin/Fiji.app/fiji-linux64'
elif MACHINE == "sstoma-pokrzywa":
    SIC_CELLID = "/Users/stymek/src/cell_id-1.4.3-HACK/cell"
    SIC_ROOT = '/Volumes/image-data/images/11-01-10-mateo,aouefa,dataanalysis-test'
    SIC_FIJI = 'fiji-macosx'
elif MACHINE == "MJS Windows":
    SIC_CELLID = 'C:\\Program Files (x86)\\VCell-ID\bin\\vcellid.exe' #TODO: working? or Progra~2 hack?
    SIC_ROOT = 'C:\\Users\\MJS\\My Dropbox\\Studium\\Berufspraktikum\\working_directory'
    SIC_FIJI = 'fiji-macosx' #TODO:
elif MACHINE == "martin-uschan":
    SIC_CELLID = 'C:\\Program Files (x86)\\VCell-ID\bin\\vcellid.exe' #TODO: 
    SIC_ROOT = '/home/martin/working_directory' 
    SIC_FIJI = '/home/martin/Fiji.app/fiji-linux'


SIC_ORIG = "orig" # folder with original images, they are not edited
SIC_PROCESSED = "processed" # folder with processed images, images may be changed, symlinks are used to go down with the size 
SIC_RESULTS = "results"
SIC_SCRIPTS = "scripts"
SIC_LINKS = "processed"
SIC_FIND_DOTS_SCRIPT = "find_dots.ijm" # fiji script for finding dots
SIC_CELLID_PARAMS = "parameters.txt" # parameters_vcellid_out.txt
SIC_BF_LISTFILE = "bf_list.txt"
SIC_F_LISTFILE = "f_list.txt"
SIC_FILE_CORRESPONDANCE= "map.txt" # file containing the links with old names and names for cell-id 
SIC_DOTS_COORDS = "dots.txt" # CSV file containing the links with old names and dot coordinates
FIJI_HEADERS = ("I", "Label", "Area", "XM", "YM", "Slice")
RAD2 = 15*15 # av. squared yeast cell radius
SIC_MAX_DOTS_PER_IMAGE  = 40 # the images containing more then this will be discarded - it is suspicious
SIC_DATA_PICKLE = "data.pickle"
SIC_ALLOWED_INSIDE_OUTSIDE_RATIO = .1
SIC_MAX_MISSED_CELL_PER_IMAGE = 20
SIC_MAX_CELLS_PER_IMAGE = 300
BF_REJECT_POS = [20,21,22,23,122, 145, 147, 148, 152, 192, 224, 226, 287, 288, 289, 290, 291, 292, 294,295,296,297,298,230, 354,355, 357, 358, 373,377, 378,467]
GFP_REJECT_POS = [25, 35, 38, 122, 133, 179, 287, 288, 292,298,299,333,354,432,434,435,466]+[182,183,184,185,186]


def prepare_structure(path=SIC_ROOT,
                      skip=[SIC_ORIG, SIC_SCRIPTS],
                      create_dirs=[SIC_PROCESSED, SIC_RESULTS, SIC_LINKS],
                      check_for=[join(SIC_ROOT, SIC_SCRIPTS, SIC_FIND_DOTS_SCRIPT),
                        join(SIC_ROOT, SIC_ORIG),
                        join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)]
                      ):
    '''Remove obsolete directories, create required directories and check requirements'''
    print "Preparing structure..."
    def remove_old_dirs(path, skip):
        print "Working in path:", path
        l = listdir(path)
        for i in l:
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
        print "Finished checking requirements."

    remove_old_dirs(path, skip) # TODO: careful, this will delete files!
    create_required_dirs(path, create_dirs)
    check_reqs(check_for)
    print "Finished preparing structure."
    

def copy_NIBA_files_to_processed(path=join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED)):
    '''Copy NIBA files to processed'''
    print "Copying NIBA files to processed..."
    l = listdir(path)
    for i in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC[ index3].TIF # TODO: strictly, this does not seem to match any of the sample files?
        if i.find("w1NIBA") != -1: # copy only files whose name contains the substring
            print "Copying", join(path,i), "to", join(dest,i)
            copyfile(join(path,i), join(dest,i))
    print "Finished copying NIBA files to processed."


def link_DIC_files_to_processed(path = join(SIC_ROOT, SIC_ORIG), dest=join(SIC_ROOT, SIC_PROCESSED)):
    '''Link DIC files to processed'''
    print "Linking DIC files to processed..."
    l = listdir(path)
    for i in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC[ index3].TIF
        if i.find("w2DIC") != -1: # link only files whose name contains the substring
            if os.name != 'nt': # TODO: this should explicitely refer to 'Linux'
                print "Linking", join(path, i), "to", join(dest, i)
                symlink(join(path, i), join(dest, i))
            else:
                # TODO: for Windows, create shortcuts instead of symlinks
                print "Operating system is Windows, calls to symlink will not work."
    print "Finished linking DIC files to processed."
        

def fiji_run_dot_finding(path=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, SIC_FIND_DOTS_SCRIPT)):
    '''Run FIJI to find dots'''
    print "Running FIJI to find dots..."
    l = listdir(path)
    for fn in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC.TIF-mask.tif
        if fn.find("w1NIBA.TIF") != -1: # run fiji only for files whose name contains the substring
            s = "%s %s -macro %s -batch" % (SIC_FIJI, join(path, fn), script_filename)
            print "# ext. call:", s
            call(s.split())
    print "Finished running FIJI to find dots"


def color_processed_NIBA_files(path = join(SIC_ROOT, SIC_PROCESSED)):
    '''Color processed NIBA files'''
    print "Coloring processed NIBA files..."
    l = listdir(path)
    for fn in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC.TIF-mask.tif
        if fn.find("w1NIBA.TIF-mask.tif") != -1: # only for files whose name contains the substring
            # TODO: check that convert by ImageMagick runs under Windows
            #s = "convert %s -negate -channel G -evaluate multiply 0. -channel B -evaluate multiply 0. %s" % (join(path,fn), join(path,fn[:-4]+"-colored"+".tif"))
            s = "convert %s -negate -depth 16 -type Grayscale -evaluate multiply 0.5 -fill white -draw point_200,200 %s" % (join(path, fn), join(path, fn[:-4] + "-colored" + ".tif"))
            ss = s.split()
            for j in range(len(ss)):
                if ss[j] == "point_200,200":
                    ss[j] = 'point 200,200'
            print "# ext. call:", ss
            call(ss)
            #s = "convert %s -depth 16 -type TrueColor -draw \"point 0,0\"  %s" % (join(path,fn[:-4]+"-colored-wp"+".tif"), join(path,fn[:-4]+"-colored"+".tif"))
            #print "# ext. call:", s
            #call(s.split())
    print "Finished coloring processed NIBA files"


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
    for i in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC.TIF
        if i.endswith("w1NIBA.TIF"):
            nfn = i.split("_")
            time = re.search("[0-9]+", nfn[2]).group(0)
            nn = "GFP_Position" + str(pos) + "_time" + time + ".tif"
            o2n[i + "-mask-colored.tif"] = [nn]
            print "nfn =", nfn
            corresponding_dic = nfn[0] + "_" + nfn[1] + "_" + nfn[2] + "_" + nfn[3] + "_" + re.sub(" [0-9]", "", nfn[4].replace("1NIBA","2DIC")) 
            niba2dic[i + "-mask-colored.tif"] = corresponding_dic
            dic2niba[corresponding_dic] = [i + "-mask-colored.tif"]
            # we have met this DIC first time so we need to add it to the maps
            bff = "BF_Position" + str(pos) + "_time" + time + ".tif"
            o2n[corresponding_dic] = [bff]
            pos += 1
            
    # checking if all required DIC files are present
    for i in dic2niba:
        if i not in l:
            print " !: required DIC file not found:", i
            #return -1
    # generating rename file
    for i in o2n.keys():
        #f.write("'"+i+"'")
        f.write(i + " ")
        for j in o2n[i]:
            #f.write(" '"+j+"'")
            f.write(j)
        f.write("\n")
    f.close()
    print "Finished creating map image data"
    return niba2dic, dic2niba, o2n


def write_dic_file(filename, dic2niba):
    f = open(filename, "w")
    for i in dic2niba.keys():
        f.write(i+'\n')
        #f.write('"'+i+'"\n')
    f.close()


def write_niba_file(filename, niba2dic):
    f = open(filename, "w")
    for i in niba2dic.keys():
        f.write(i + '\n')
        #f.write('"' + i + '"\n')
    f.close()

    
def create_symlinks(s2t, sourcepath=join(SIC_ROOT, SIC_PROCESSED), targetpath=join(SIC_ROOT, SIC_LINKS)):
    for i in s2t.keys():
        for j in s2t[i]:
            symlink(join(sourcepath, i), join(targetpath, j))
            print " #: Linking", join(sourcepath, i), join(targetpath, j)


def prepare_b_and_f_files(niba2dic, dic2niba, o2n, path=join(SIC_ROOT, SIC_PROCESSED), bf_filename=join(SIC_ROOT, SIC_PROCESSED, SIC_BF_LISTFILE), f_filename=join(SIC_ROOT, SIC_PROCESSED, SIC_F_LISTFILE)):
    print "Writing BF and F files..."
    bf = file(bf_filename, "w")
    ff = file(f_filename, "w")
    for i in niba2dic.keys():
        ff.write(path + o2n[i][0] + '\n')
        #TODO the same DIC file is used for all NIBA
        bf.write(path + o2n[niba2dic[i]][0] + '\n')
    ff.close()
    bf.close()
    print "BF and F files written."


def prepare_b_and_f_single_files(niba2dic, dic2niba, o2n, path=join(SIC_ROOT, SIC_PROCESSED)):
    print "Writing BF and F single files..."
    for i in niba2dic.keys():
        bf = file(path + o2n[niba2dic[i]][0][:-3] + "path", "w") # we cut out last 3 chars from the file name and we put 'path'
        ff = file(path + o2n[i][0][:-3] + "path", "w")
        ff.write(path + o2n[i][0] + '\n')
        #TODO the same DIC file is used for all NIBA
        bf.write(path + o2n[niba2dic[i]][0] + '\n')
        ff.close()
        bf.close()
    print "BF and F single files written."


def run_cellid(path = join(SIC_ROOT, SIC_PROCESSED),
               cellid=SIC_CELLID,
               bf_fn=join(SIC_ROOT, SIC_PROCESSED, SIC_BF_LISTFILE),
               f_fn=join(SIC_ROOT, SIC_PROCESSED, SIC_F_LISTFILE),
               options_fn=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS),
               output_prefix=join(SIC_ROOT, SIC_PROCESSED)
               ):
    #s = "convert %s -negate -channel G -evaluate multiply 0. -channel B -evaluate multiply 0. %s" % (join(path,fn), join(path,fn[:-4]+"-colored"+".tif"))
    ## TODO: change this to run it file after file - change also the output_prefix so it should give the _all file...
    l = listdir(path)
    for i in l:
        if i.startswith("GFP") and i.endswith(".path"):
            bf = join(path, i.replace("GFP", "BF"))
            ff = join(path, i)
            out = join(path, i[:-5])
            #mkdir(out)
            s = "%s -b %s -f %s -p %s -o %s" % (cellid, bf, ff, options_fn, out)
            print "# ext. call:", s
            call(s.split())
        
        
def load_fiji_results_and_create_mappings(path=join(SIC_ROOT, SIC_PROCESSED), headers=FIJI_HEADERS):
    l = listdir(path)
    s = set() 
    for i in l:
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w2NIBA/w1DIC.TIF
        if not i.find(".xls") == -1:
            f = open(join(path,i), 'r')
            ls = f.readlines()
            
            for i in ls:
                s.add(tuple(i.split()))
                # A problem is a space in the label
                #  	Label	XM	YM
                #1	Sic1_GFP3_142min_1_w2NIBA2.TIF-avg.tif	327.264706	13.500000
    # headers are set manually here
    #headers = tuple(ls[0].split())
    return (headers, s)


def find_index(ind_desc='', headers=()):
    for i in range(len(headers)):
        if not headers[i].find(ind_desc) == -1:
            return i
    raise Exception(" !: Index description not found in headers!")

    
def create_mappings_filename2pixel_list( ds ):
    headers, data = ds
    res = {}    
    for l in data:
        label = l[find_index("Label", headers)]
        x = int(float(l[find_index("XM",headers)]))
        y = int(float(l[find_index("YM",headers)]))
        #label = label[:-8]
        if res.has_key(label):
            tl = res[label]
            tl.append((x, y))
            res[label] = tl
        else:
            res[label] = [(x, y)]
    return res


def load_cellid_files_and_create_mappings(
        filename2pixellist,
        original_name2cellid_name,
        path = join(SIC_ROOT, SIC_PROCESSED),
        cellid_results_path=join(SIC_ROOT, SIC_LINKS),
    ):
    l = listdir( path )
    filename2cells = {} # filename to cell_id of pixels containing a dot
    cellid_name2original_name = dict((v[0],k) for k, v in original_name2cellid_name.iteritems())
    for i in l:
        # file name containing cell BOUNDs
        if i.find("BOUND") != -1:
            d = {}
            f = file(join(path,i), "r")
            # now we find pixels interesting for our file
            cellid_fn = "GFP_" + i[3:-10]
            orig_fn = cellid_name2original_name[ cellid_fn ].replace("_w2NIBA.TIF-mask-colored.tif", "_w2NIBA.TIF-max.tif",)
            filename2cells[orig_fn] = []
            search_px = filename2pixellist[orig_fn]
            for line in f.readlines():
                ls = line.split()
                if len(ls) == 3:
                    x, y, cellid = ls
                    if (int(x), int(y)) in search_px:
                        filename2cells[orig_fn].append(cellid)
                #assert False
            # we fill the list with -1 for every pixe which was not found in the cell
            #filename2cells[ orig_fn] = filename2cells[ orig_fn]+[-1]*(len(search_px)-len(filename2cells[ orig_fn]))
            f.close()
    return filename2cells


def load_cellid_files_and_create_mappings_from_bounds(
        filename2pixellist,
        original_name2cellid_name,
        path = join(SIC_ROOT, SIC_PROCESSED),
        cellid_results_path=join(SIC_ROOT, SIC_LINKS),
    ):
    l = listdir(path)
    filename2cells = {} # filename to cell_id of pixels containing a dot
    cellid_name2original_name = dict((v[0], k) for k, v in original_name2cellid_name.iteritems())
    filename2cell_number = {} # mapping with filename and the number of discovered cells
    filename2hist = {} # mapping with filename to hist
    for i in l:
        # file name containing cell BOUNDs
        if i.find("BOUND") != -1 and i.find("GFP") != -1:
            print " # Processing ", i
            cell2center = {}
            d = {}
            f = file(join(path,i), "r")
            # now we find pixels interesting for our file
            cellid_fn = i[:-10]
            orig_fn = cellid_name2original_name[ cellid_fn ].replace("_w2NIBA.TIF-mask-colored.tif","_w2NIBA.TIF-max.tif",)
            filename2cells[ orig_fn ] = []
            cell_nb = set()
            # reading the boundary position for each cell
            for line in f.readlines():
                ls = line.split()
                if len(ls) == 3:
                    x,y,cellid = map(int, ls)
                    if cell2center.has_key(cellid):
                        (ox,oy,nb) = cell2center[cellid]
                        cell_nb.add(cellid)
                        cell2center[cellid] = (ox+x, oy+y, nb+1)
                    else:
                        cell2center[cellid] = (x, y, 1)
            f.close()
            
            # finding cell centers
            for ck,val in cell2center.iteritems():
                cell2center[ck] = (val[0]/float(val[2]), val[1]/float(val[2]), val[2])
            
            # finding to which cell belongs a point
            search_px = filename2pixellist[orig_fn]
            for px in search_px:
                hit = False
                for cc, cv in cell2center.iteritems():
                    if pow((px[0] - cv[0]), 2) + pow((px[1] - cv[1]), 2) < RAD2: 
                        filename2cells[orig_fn].append(cc)
                        hit = True
                        break
                if not hit:
                    filename2cells[orig_fn].append(-1)
                #assert False
            # we fill the list with -1 for every pixe which was not found in the cell
            filename2cells[orig_fn] = filename2cells[orig_fn] # + [-1] * missed #(len(search_px) - len(filename2cells[orig_fn]))
            #print filename2cells[orig_fn]
            
            # agregate the cells hist
            for i, j in filename2cells.iteritems():
                b = {}
                for item in j:
                    b[item] = b.get(item, 0) + 1
                filename2cells[i] = b
            #print filename2cells[orig_fn]
            #assert False
            
            # make hist
            
            d = filename2cells[orig_fn]
            td = dict()
            if d.has_key(-1):
                not_found = d.pop(-1)
            else:
                not_found = 0
            for i, j in d.iteritems():
                td[j] = td.get(j, 0) + 1
            filename2hist[orig_fn] = (td, not_found)
            #print filename2hist
            #assert False
            
            # cell number
            filename2cell_number[orig_fn] = len(cell_nb)
    return filename2cells, filename2hist, filename2cell_number    


def run_all_steps():
    run_create_required_files()
    return run_analysis()

    
def run_create_required_files():
    prepare_structure()
    copy_NIBA_files_to_processed()
    link_DIC_files_to_processed()
    fiji_run_dot_finding()
    color_processed_NIBA_files()
    niba2dic, dic2niba, o2n = create_map_image_data()
    create_symlinks(o2n)
    # prepare_b_and_f_files(niba2dic, dic2niba, o2n) # next line substitutes this one
    prepare_b_and_f_single_files(niba2dic, dic2niba, o2n)
    run_cellid()
    d = run_analysis()
    return d
    #plot_time2ratio_between_one_dot_number_and_cell_number(d)
    

def run_analysis():
    niba2dic, dic2niba, o2n = create_map_image_data()
    headers, data = load_fiji_results_and_create_mappings()
    filename2pixel_list = create_mappings_filename2pixel_list((headers, data))
    filename2cells, filename2hist, filename2cell_number = load_cellid_files_and_create_mappings_from_bounds(filename2pixel_list, o2n)
    
    d = {
        "niba2dic" : niba2dic,
        "dic2niba" : dic2niba,
        "o2n" : o2n,
        "filename2pixel_list" : filename2pixel_list,
        "headers": headers,
        "data" : data,
        "filename2cells" : filename2cells,
        "filename2hist" : filename2hist,
        "filename2cell_number" : filename2cell_number,
    }
    pickle.dump(d, file(join(SIC_ROOT,SIC_RESULTS,SIC_DATA_PICKLE),"w") )
    return d
    

def plot_time2ratio_between_one_dot_number_and_cell_number( data, black_list=BF_REJECT_POS+GFP_REJECT_POS ):
    time2one_dot = {}
    time2mult_dot = {}
    time2not_discovered = {}
    time2number_of_cells = {}
    time2ratioA = {}
    time2ratioB = {}
    time2ratioC = {}
    
    filename2hist = data["filename2hist"]
    filename2cells = data["filename2cells"]
    filename2cell_number = data["filename2cell_number"]
    for fn, d in filename2hist.iteritems():
            sfn = fn.split("_")
            time = float(re.search("[0-9]+", sfn[2]).group(0))
            sofn = data["o2n"][fn.replace("-max", "-mask-colored")][0].split("_")
            pos = int(re.search("[0-9]+", sofn[1]).group(0))
            ## filtering
            # now we need to decide if we filter out the image; decision is based on:
            # 1. if not "too many" dots were found (it is likely that it is a mistake)
            # * SIC_MAX_DOTS_PER_IMAGE is critical value
            # 2. if the ratio of dots in the cells to dots outside of the cells is
            # smaller then SIC_ALLOWED_INSIDE_OUTSIDE_RATIO then the image is discarded
            # 3. Number of missed cell is bigger then SIC_MAX_MISSED_CELL_PER_IMAGE
            # 4. Number of cells is smaller then SIC_MAX_MISSED_CELL_PER_IMAGE
            # 5. Filter the position from black_list
            
            tot_dots_in_cells = sum(filename2hist[fn][0].itervalues())
            tot_dots_outside_cells = filename2hist[fn][1]
            print data["o2n"][fn.replace("-max", "-mask-colored")], tot_dots_in_cells, tot_dots_outside_cells
            #1
            if  tot_dots_in_cells+tot_dots_outside_cells > SIC_MAX_DOTS_PER_IMAGE: continue
            #2
            if tot_dots_in_cells / max(1,float(tot_dots_outside_cells)) < SIC_ALLOWED_INSIDE_OUTSIDE_RATIO: continue
            #3
            if tot_dots_outside_cells > SIC_MAX_MISSED_CELL_PER_IMAGE: continue
            #4
            if filename2cell_number[fn] > SIC_MAX_MISSED_CELL_PER_IMAGE: continue
            #5
            if pos in black_list: continue
            ## end of filtering
            
            time2one_dot[time] = time2one_dot.get(time, 0)+filename2hist[fn][0].get(1, 0) # we add the one dots
            time2mult_dot[time] = time2mult_dot.get(time, 0)
            for i in range(10):
                time2mult_dot[time] += i*filename2hist[fn][0].get(i, 0)
            time2not_discovered[time] = time2not_discovered.get(time, 0)+filename2hist[fn][1] # not discovered
            time2number_of_cells[time] = time2number_of_cells.get(time, 0)+filename2cell_number[fn]
    for i in time2one_dot.keys():
        time2ratioA[i] = time2one_dot[i] / float(time2number_of_cells[i])
        time2ratioB[i] = time2not_discovered[i] / float(time2number_of_cells[i])
        time2ratioC[i] = time2mult_dot[i] / float(time2number_of_cells[i])
    
    data1 = [(k,v) for k, v in time2ratioA.items()]
    data1.sort()
    data1x, data1y = zip(*data1)
    data1x = [data1x[0]-1]+list(data1x)+[data1x[-1]+1]
    data1y = [data1y[0]]+list(data1y)+[data1y[-1]]
    data1tck = interpolate.splrep(data1x,data1y,k=2)
    data1xi = np.arange(min(data1x),max(data1x),1)
    data1yi = interpolate.splev(data1xi,data1tck,der=0)

    data2 = [(k,v) for k, v in time2ratioB.items()]
    data2.sort()
    data2x, data2y = zip(*data2)
    
    data3 = [(k,v) for k, v in time2number_of_cells.items()]
    data3.sort()
    data3x, data3y = zip(*data3)
    
    data4 = [(k,v) for k, v in time2not_discovered.items()]
    data4.sort()
    data4x, data4y = zip(*data4)
    
    data5 = [(k,v) for k, v in time2ratioC.items()]
    data5.sort()
    data5x, data5y = zip(*data5)
    data5x = [data5x[0]-1]+list(data5x)+[data5x[-1]+1]
    data5y = [data5y[0]]+list(data5y)+[data5y[-1]]
    data5tck = interpolate.splrep(data5x,data5y,k=2)
    data5xi = np.arange(min(data5x),max(data5x),1)
    data5yi = interpolate.splev(data5xi,data5tck,der=0)
    
    pl.subplot(221)
    pl.plot(data1x, data1y, 'or',)
    pl.xlabel("Time [s]")
    #pl.ylabel("1dot/#cell")

    pl.subplot(221)
    pl.plot(data5x,data5y,'og')
    pl.xlabel("Time [s]")
    #pl.ylabel("1-10dot / #cell")
    pl.plot( data1xi, data1yi, "r", data5xi, data5yi, "g")
    pl.legend(["1dot/#cell", "1-10dot/#cell"])
    
    pl.subplot(222)
    pl.plot(data2x,data2y)
    pl.xlabel("Time [s]")
    pl.ylabel("Missed/#cell")
    
    pl.subplot(223)
    pl.plot(data3x,data3y)
    pl.xlabel("Time [s]")
    pl.ylabel("#cell")
 
    pl.subplot(224)
    pl.plot(data4x,data4y)
    pl.xlabel("Time [s]")
    pl.ylabel("#missed dots")
    
    pl.show()


#niba2dic, dic2niba, o2n = create_map_image_data()
#create_symlinks(SIC_ROOT, SIC_ROOT+"symlinks/", o2n)
#prepare_b_and_f_files(niba2dic, dic2niba, o2n)
#files2points = load_fiji_results_and_create_mappings(SIC_ROOT+"Results.xls")


if __name__ == '__main__':
    #prepare_structure()
    #copy_NIBA_files_to_processed()
    #link_DIC_files_to_processed()
    #fiji_run_dot_finding()
    #color_processed_NIBA_files()
    niba2dic, dic2niba, o2n = create_map_image_data()
    #run_create_required_files()

#-------------------------------------------------------
#OLD STUFF:
#-------------------------------------------------------
#def execute_rename( filename ):
#    f = open( filename, 'r')
#    for line in f:
#        m = re.findall("'.*?'", line)
#        print m[0], "->", m[1]
#        #rename(n1, n2)
#    f.close()
