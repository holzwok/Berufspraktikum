import os
from os import rename
from os.path import join, exists


from global_vars import *


def set_parameters(param_dict=PARAM_DICT,
                   param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)):
    '''Takes parameters from param_dict and writes them to param_file'''
    print "Setting cell-ID parameters..."
    if exists(param_file+"~"): os.remove(param_file+"~")
    if exists(param_file): rename(param_file, param_file+"~")
    
    with open(param_file, "w") as outfile:
        print "Writing to file:", param_file
        for k, v in param_dict.items():
            outfile.write(" "+k+" "+str(v)+"\n")
        # I am not letting these be modified at present, so they are always appended:
        outfile.write(" image_type brightfield\n")
        outfile.write(" bf_fl_mapping list\n")
        outfile.write(" align_individual_cells\n")
    print "Finished setting cell-ID parameters."

def load_parameters(param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)):
    '''Loads parameters from param_file and returns dict'''
    param_dict = dict()
    with open(param_file, "r") as infile:
        for line in infile:
            linelist = line.split()
            if len(linelist)==2:
                key = linelist[0]
                try:
                    value = float(linelist[1]) if '.' in linelist[1] else int(linelist[1])
                    param_dict[key]=value
                except:
                    pass
                    # maybe not the cleanest way to skip the image_type brightfield line
    return param_dict

if __name__ == '__main__':
    # The following are some heuristically reasonable parameters:
    param_dict_current = {"max_dist_over_waist":100.0,
                          "max_split_over_minor_axis":1.0,
                          "min_pixels_per_cell":235,
                          "max_pixels_per_cell":1500,
                          "background_reject_factor":1.0,
                          "tracking_comparison":0.2}
    set_parameters(param_dict_current)
    
    with open(join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS), 'r') as pfile:
        print pfile.read()
    
    print load_parameters(join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS))
