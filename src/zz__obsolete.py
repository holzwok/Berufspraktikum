#-------------------------------------------------------
#OLD or OBSOLETE STUFF:
#-------------------------------------------------------

def execute_rename( filename ):
    f = open( filename, 'r')
    for line in f:
        m = re.findall("'.*?'", line)
        print m[0], "->", m[1]
        #rename(n1, n2)
    f.close()

def write_dic_file(filename, dic2niba):
    f = open(filename, "w")
    for i in dic2niba.keys():
        f.write(i + '\n')
        #f.write('"'+i+'"\n')
    f.close()

def write_niba_file(filename, niba2dic):
    f = open(filename, "w")
    for i in niba2dic.keys():
        f.write(i + '\n')
        #f.write('"' + i + '"\n')
    f.close()

def color_processed_NIBA_files(path = join(SIC_ROOT, SIC_PROCESSED)):
    '''Color processed NIBA files'''
    print "Coloring processed NIBA files..."
    l = listdir(path)
    for fn in sorted(l):
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF-mask.tif
        if fn.find(NIBA_ID+".TIF-mask.tif") != -1: # only for files whose name contains NIBA_ID+".TIF-mask.tif"
            # TODO: check that convert by ImageMagick runs under Windows
            #s = "convert %s -negate -channel G -evaluate multiply 0. -channel B -evaluate multiply 0. %s" % (join(path,fn), join(path,fn[:-4]+"-colored"+".tif"))
            s = "convert %s -negate -depth 16 -type Grayscale -evaluate multiply 0.5 -fill white -draw point_200,200 %s" % (join(path, fn), join(path, fn[:-4] + "-colored" + ".tif"))
            ss = s.split()
            for j in range(len(ss)):
                if ss[j] == "point_200,200":
                    ss[j] = 'point 200,200'
            print "External call:", " ".join(ss)
            call(ss)
            #s = "convert %s -depth 16 -type TrueColor -draw \"point 0,0\"  %s" % (join(path,fn[:-4]+"-colored-wp"+".tif"), join(path,fn[:-4]+"-colored"+".tif"))
            #print "External call:", s
            #call(s.split())
    print "Finished coloring processed NIBA files."

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

def load_cellid_files_and_create_mappings(
        filename2pixellist,
        original_name2cellid_name,
        path = join(SIC_ROOT, SIC_PROCESSED),
        cellid_results_path=join(SIC_ROOT, SIC_LINKS),
    ):
    '''Load cellid files and create mappings'''
    print "Loading cellid files and create mappings..."
    l = listdir(path)
    filename2cells = {} # filename to cell_id of pixels containing a dot
    cellid_name2original_name = dict((v[0],k) for k, v in original_name2cellid_name.iteritems())
    for i in sorted(l):
        # file name containing cell BOUNDs
        if i.find("BOUND") != -1:
            d = {}
            f = file(join(path, i), "r")
            # now we find pixels interesting for our file
            cellid_fn = "GFP_" + i[3:-10]
            orig_fn = cellid_name2original_name[cellid_fn].replace("NIBA.TIF-mask-colored.tif", "NIBA.TIF-max.tif",)
            filename2cells[orig_fn] = []
            search_px = filename2pixellist[orig_fn]
            for line in f.readlines():
                ls = line.split()
                if len(ls) == 3:
                    x, y, cellid = ls
                    if (int(x), int(y)) in search_px:
                        filename2cells[orig_fn].append(cellid)
            # we fill the list with -1 for every pixel which was not found in the cell
            #filename2cells[ orig_fn] = filename2cells[ orig_fn]+[-1]*(len(search_px)-len(filename2cells[ orig_fn]))
            f.close()
    print "Finished loading cellid files and creating mappings."
    return filename2cells
