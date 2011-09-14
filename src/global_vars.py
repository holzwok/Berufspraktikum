#!/usr/bin/env python
'''
All global variable, machine and session settings are contained in this file (or are set by the GUI).
If running from command line (not from GUI), pls adjust MACHINE according to your machine below.
If running from command line (not from GUI), pls select desired session in SESSION below.
'''

# this block was commented out in order to run the GUI
#MACHINE = "sstoma-pokrzywa"
#MACHINE = "sstoma-smeik"
MACHINE = "martin-uschan"
#MACHINE = "aouefa-linux"
#MACHINE = "MJS Windows"
#MACHINE = "MJS Linux"

if MACHINE == "sstoma-smeik":
    SIC_CELLID = "/home/sstoma/svn/sstoma/src/11_01_25_cellId/cell"
    SIC_ROOT = '/local/home/sstoma/images/11-06-18-sic,matthias'
    SIC_FIJI = '/home/sstoma/bin/Fiji.app/fiji-linux64'
    SIC_SPOTTY = ''
    SIC_MEDIAN = ''
elif MACHINE == "sstoma-pokrzywa":
    SIC_CELLID = "/Users/stymek/src/cell_id-1.4.3-HACK/cell"
    SIC_ROOT = '/Volumes/image-data/images/11-01-10-mateo,aouefa,dataanalysis-test'
    SIC_FIJI = 'fiji-macosx'
    SIC_SPOTTY = ''
    SIC_MEDIAN = ''
elif MACHINE == "martin-uschan":
    SIC_CELLID = "/home/basar/Personal/Martin_Seeger/imaging/cell_id-143_hack/cell"
    SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
    SIC_FIJI = '/home/basar/Personal/Martin_Seeger/imaging/Fiji.app/fiji-linux64'
    SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/src/spottyG.R'
    SIC_MEDIAN = '/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/src/median_clustering.R'
elif MACHINE == "aouefa-linux":
    SIC_CELLID = "/home/aouefa/cell_id-143_hack/cell"
    SIC_ROOT = '/home/aouefa/working_directory' 
    SIC_FIJI = '/home/aouefa/Fiji.app/fiji-linux'
    SIC_SPOTTY = '/home/aouefa/git/Berufspraktikum/src/spottyG.R'
    SIC_MEDIAN = ''
elif MACHINE == "MJS Windows":
    SIC_CELLID = r'C:/Program Files (x86)/VCell-ID/bin/vcellid.exe' #TODO: working? or Progra~2 hack?
    SIC_ROOT = r'C:/Users/MJS/My Dropbox/Studium/Berufspraktikum/working_directory'
    SIC_FIJI = r'C:/Program Files/Fiji.app/fiji-win64.exe'
    SIC_SPOTTY = ''
    SIC_MEDIAN = ''
elif MACHINE == "MJS Linux":
    SIC_CELLID = "/home/mjs/Berufspraktikum/imaging/cell_id-1.4.3_hack/cell"
    SIC_ROOT = '/home/mjs/Berufspraktikum/working_directory' 
    SIC_FIJI = '/usr/bin/fiji' #'/home/mjs/Berufspraktikum/Fiji.app/fiji-linux64' # <- this one does not work
    SIC_SPOTTY = ''
    SIC_MEDIAN = ''


#SESSION = "17_nice_pictures_linux"
#SESSION = "53_selected"
#SESSION = "20110609_sic1_gfp3x-dapi_fixed_mounted_CLEAN"
#SESSION = "20110609_sic1_gfp3x-dapi_fixed_mounted_2_CLEAN"
SESSION = "test_session_martin_linux"
#SESSION = "test_session_aouefa_linux"
#SESSION = "170_files_synchronised_aouefa_linux"
#SESSION = "20110819_FISH_Aouefa"
#SESSION = "20110831_Sic1MS2_150xObj"

if SESSION == "17_nice_pictures_linux":
    SIC_ORIG = "orig" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1DIC"
elif SESSION == "53_selected":
    SIC_ORIG = "orig2" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1DIC"
elif SESSION == "20110609_sic1_gfp3x-dapi_fixed_mounted_CLEAN":
    SIC_ORIG = "orig1" # folder with original images, they are not edited
    NIBA_ID = "w1NIBA"
    DIC_ID = "w3DIC"
elif SESSION == "20110609_sic1_gfp3x-dapi_fixed_mounted_2_CLEAN":
    SIC_ORIG = "orig4" # folder with original images, they are not edited
    NIBA_ID = "w1NIBA"
    DIC_ID = "w3DIC"
elif SESSION == "test_session_martin_linux":
    SIC_ORIG = "orig3" # folder with original images, they are not edited
    NIBA_ID = "w1NIBA"
    DIC_ID = "w3DIC"
elif SESSION == "test_session_aouefa_linux":
    SIC_ORIG = "orig" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1DIC"
elif SESSION == "170_files_synchronised_aouefa_linux":
    SIC_ORIG = "orig1" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1DIC"
# FISH session
# TODO: PARAM_DICT
elif SESSION == "20110819_FISH_Aouefa":
    SIC_ORIG = "orig6" # folder with original images, they are not edited
    NIBA_ID = "w2NG"
    DIC_ID = "w1BF"
# spot tracker session
elif SESSION == "20110831_Sic1MS2_150xObj":
    SIC_ORIG = "orig5" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1BF"
    PARAM_DICT = {"max_dist_over_waist":10.0,
                  "max_split_over_minor_axis":1.0,
                  "min_pixels_per_cell":505,
                  "max_pixels_per_cell":9999,
                  "background_reject_factor":0.5,
                  "tracking_comparison":0.2}
else: # default
    SIC_ORIG = "orig" # folder with original images, they are not edited
    NIBA_ID = "w2NIBA"
    DIC_ID = "w1DIC"


SIC_PROCESSED = "processed" # folder with processed images, images may be changed, symlinks are used to go down with the size 
SIC_RESULTS = "results"
SIC_SCRIPTS = "scripts"
SIC_LINKS = "processed"
FIJI_STANDARD_SCRIPT = "find_dots.ijm" # fiji script for standard mode
FIJI_TRACK_SCRIPT = "stack2image.ijm" # fiji script for track spot mode
SIC_CELLID_PARAMS = "parameters.txt"

# The following are a set of heuristically useful cell-ID parameters.
# They can be explicitely overwritten in a session below.
PARAM_DICT = {"max_dist_over_waist":100.0,
              "max_split_over_minor_axis":1.0,
              "min_pixels_per_cell":235,
              "max_pixels_per_cell":1500,
              "background_reject_factor":1.0,
              "tracking_comparison":0.2}

BF_REJECT_POS = []
GFP_REJECT_POS = []
SIC_MAX_DOTS_PER_IMAGE  = 40 # Images containing more than this will be discarded
SIC_MAX_MISSED_CELL_PER_IMAGE = 20
SIC_MAX_CELLS_PER_IMAGE = 300
SIC_ALLOWED_INSIDE_OUTSIDE_RATIO = .1

SIC_BF_LISTFILE = "bf_list.txt" # TODO: not yet used
SIC_F_LISTFILE = "f_list.txt"   # TODO: not yet used
SIC_FILE_CORRESPONDANCE = "map.txt" # file containing the links with old names and names for cell-id 
FIJI_HEADERS = ("Key", "Label", "Area", "XM", "YM", "Slice")
RAD2 = 15*15 # avg. squared yeast cell radius
SIC_DATA_PICKLE = "data.pickle"

POSI_TOKEN = "P" # This will be built into the Cell ID filenames
TIME_TOKEN = "T" # This will be built into the Cell ID filenames
CELLID_FP_TOKEN = "-max.tif" # This determines which fluorophore file cell-ID is applied to: 
                                # e.g. "-mask-colored.tif": to masked files (flat background and intensity)
                                # e.g. "-max.tif": to max projection files (flat background, modulated intensity)
GMAX = 3 # maximum number of clusters per cell for clustering algorithm


def n_RNA(intensity):
    slope = 15.268      # delta intensity per extra GFP molecule
    saturation = 0.7    # percentage of occupied GFP binding sites
    n_GFP_max = 72      # maximum number of GFPs that can bind to one mRNA
    n = intensity/slope/saturation/n_GFP_max
    return n
