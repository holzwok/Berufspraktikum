import os
from os import rename
from os.path import join, exists


from global_vars import *


# The following are the default parameters as set in Cell ID:
PARAM_DICT_DEFAULT = {"max_dist_over_waist":8.0,
                      "max_split_over_minor_axis":0.5,
                      "min_pixels_per_cell":75,
                      "max_pixels_per_cell":1500,
                      "background_reject_factor":1.0,
                      "tracking_comparison":0.2}


def set_parameters(param_dict=PARAM_DICT_DEFAULT,
                   param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)):

    print "Setting cell-ID parameters..."
    if exists(param_file+"~"): os.remove(param_file+"~")
    if exists(param_file): rename(param_file, param_file+"~")
    
    with open(param_file, "w") as outfile:
        for k, v in param_dict.items():
            outfile.write(" "+k+" "+str(v)+"\n")
        # I am not letting these be modified at present, so they are always appended:
        outfile.write(" image_type brightfield\n")
        outfile.write(" bf_fl_mapping list\n")
        outfile.write(" align_individual_cells\n")
    print "Finished setting cell-ID parameters."
        

if __name__ == '__main__':
    # The following are some heuristically reasonable parameters:
    param_dict_current = {"max_dist_over_waist":100.0,
                          "max_split_over_minor_axis":10.0,
                          "min_pixels_per_cell":235,
                          "max_pixels_per_cell":1500,
                          "background_reject_factor":1.0,
                          "tracking_comparison":0.2}
    set_parameters(param_dict_current)
