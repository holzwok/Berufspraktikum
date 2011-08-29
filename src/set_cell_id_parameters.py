import os
from os import rename
from os.path import join, exists

#MACHINE = "sstoma-pokrzywa"
#MACHINE = "sstoma-smeik"
MACHINE = "martin-uschan"
#MACHINE = "MJS Windows"
#MACHINE = "MJS Linux"

if MACHINE == "sstoma-smeik":
    SIC_CELLID = "/home/sstoma/svn/sstoma/src/11_01_25_cellId/cell"
    SIC_ROOT = '/local/home/sstoma/images/11-06-18-sic,matthias'
    SIC_FIJI = '/home/sstoma/bin/Fiji.app/fiji-linux64'
    SIC_SPOTTY = ''
elif MACHINE == "sstoma-pokrzywa":
    SIC_CELLID = "/Users/stymek/src/cell_id-1.4.3-HACK/cell"
    SIC_ROOT = '/Volumes/image-data/images/11-01-10-mateo,aouefa,dataanalysis-test'
    SIC_FIJI = 'fiji-macosx'
    SIC_SPOTTY = ''
elif MACHINE == "martin-uschan":
    SIC_CELLID = "/home/basar/Personal/Martin_Seeger/imaging/cell_id-143_hack/cell"
    SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
    SIC_FIJI = '/home/basar/Personal/Martin_Seeger/imaging/Fiji.app/fiji-linux64'
    SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/workspace/Berufspraktikum/src/spottyG.R'
elif MACHINE == "MJS Windows":
    SIC_CELLID = r'C:/Program Files (x86)/VCell-ID/bin/vcellid.exe' #TODO: working? or Progra~2 hack?
    SIC_ROOT = r'C:/Users/MJS/My Dropbox/Studium/Berufspraktikum/working_directory'
    SIC_FIJI = r'C:/Program Files/Fiji.app/fiji-win64.exe'
    SIC_SPOTTY = ''
elif MACHINE == "MJS Linux":
    SIC_CELLID = "/home/mjs/Berufspraktikum/imaging/cell_id-1.4.3_hack/cell"
    SIC_ROOT = '/home/mjs/Berufspraktikum/working_directory' 
    SIC_FIJI = '/usr/bin/fiji' #'/home/mjs/Berufspraktikum/Fiji.app/fiji-linux64' # <- this one does not work
    SIC_SPOTTY = ''


SIC_SCRIPTS = "scripts"
SIC_CELLID_PARAMS = "parameters.txt"

# The following are the default parameters as set in Cell ID:
PARAM_DICT_DEFAULT = {"max_dist_over_waist":8.0,
                      "max_split_over_minor_axis":0.5,
                      "min_pixels_per_cell":75,
                      "max_pixels_per_cell":1500,
                      "background_reject_factor":1.0,
                      "tracking_comparison":0.2}


def set_parameters(param_dict=PARAM_DICT_DEFAULT,
                   param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)):

    if exists(param_file+"~"): os.remove(param_file+"~")
    rename(param_file, param_file+"~")
    
    with open(param_file, "w") as outfile:
        for k, v in param_dict.items():
            outfile.write(" "+k+" "+str(v)+"\n")
        # I am not letting these be modified at present, so they are always appended:
        outfile.write(" image_type brightfield\n")
        outfile.write(" bf_fl_mapping list\n")
        outfile.write(" align_individual_cells\n")
        

if __name__ == '__main__':
    # The following are some heuristically reasonable parameters:
    param_dict_current = {"max_dist_over_waist":100.0,
                          "max_split_over_minor_axis":10.0,
                          "min_pixels_per_cell":235,
                          "max_pixels_per_cell":1500,
                          "background_reject_factor":1.0,
                          "tracking_comparison":0.2}
    set_parameters(param_dict_current)
