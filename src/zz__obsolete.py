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

def color_processed_NIBA_files(outpath = join(SIC_ROOT, SIC_PROCESSED)):
    '''Color processed NIBA files'''
    print "Coloring processed NIBA files..."
    lout = listdir(outpath)
    for fn in sorted(lout):
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF-mask.tif
        if fn.find(NIBA_ID+".TIF-mask.tif") != -1: # only for files whose name contains NIBA_ID+".TIF-mask.tif"
            # TODO: check that convert by ImageMagick runs under Windows
            #s = "convert %s -negate -channel G -evaluate multiply 0. -channel B -evaluate multiply 0. %s" % (join(outpath,fn), join(outpath,fn[:-4]+"-colored"+".tif"))
            s = "convert %s -negate -depth 16 -type Grayscale -evaluate multiply 0.5 -fill white -draw point_200,200 %s" % (join(outpath, fn), join(outpath, fn[:-4] + "-colored" + ".tif"))
            ss = s.split()
            for j in range(len(ss)):
                if ss[j] == "point_200,200":
                    ss[j] = 'point 200,200'
            print "External call:", " ".join(ss)
            call(ss)
            #s = "convert %s -depth 16 -type TrueColor -draw \"point 0,0\"  %s" % (join(outpath,fn[:-4]+"-colored-wp"+".tif"), join(outpath,fn[:-4]+"-colored"+".tif"))
            #print "External call:", s
            #call(s.split())
    print "Finished coloring processed NIBA files."

def prepare_b_and_f_files(niba2dic, dic2niba, o2n, outpath=join(SIC_ROOT, SIC_PROCESSED), bf_filename=join(SIC_ROOT, SIC_PROCESSED, SIC_BF_LISTFILE), f_filename=join(SIC_ROOT, SIC_PROCESSED, SIC_F_LISTFILE)):
    print "Writing BF and F files..."
    bf = file(bf_filename, "w")
    ff = file(f_filename, "w")
    for i in niba2dic.keys():
        ff.write(outpath + o2n[i][0] + '\n')
        #TODO the same DIC file is used for all NIBA
        bf.write(outpath + o2n[niba2dic[i]][0] + '\n')
    ff.close()
    bf.close()
    print "BF and F files written."

def load_cellid_files_and_create_mappings(
        filename2pixellist,
        original_name2cellid_name,
        outpath = join(SIC_ROOT, SIC_PROCESSED),
        cellid_results_path=join(SIC_ROOT, SIC_LINKS),
    ):
    '''Load cellid files and create mappings'''
    print "Loading cellid files and create mappings..."
    lout = listdir(outpath)
    filename2cells = {} # filename to cell_id of pixels containing a dot
    cellid_name2original_name = dict((v[0],k) for k, v in original_name2cellid_name.iteritems())
    for i in sorted(lout):
        # file name containing cell BOUNDs
        if i.find("BOUND") != -1:
            d = {}
            f = file(join(outpath, i), "r")
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

def aggregate_and_track_spots(spots, niba2dic):
    '''
    Aggregate spots and group them together if they might be the same. 
    Criteria for spot identification:
    1. Spots must be in the same cell (have the same CellID)
    2. Between adjacent slices, spots must not move more than moved = sqrt(CRIT_DIST2_FROM_PREV)
       The point with minimum moved (if below threshold) is identified with the predecessor
    3. One of the identified spots must lie with sqrt(CRIT_DIST2_FROM_MAX) of a spot in the max projection
    '''
    print "--------------------------------------------------------"
    print "Aggregating and tracking spots..."
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
            trajectory_matrix = [['M' for k in range(num_spots)] for lout in range(num_spots)]
            
            for k in range(num_spots):
                print trajectory_matrix[k]
            print "---------------------------------------------"
            
            for k, spotk in enumerate(local_spots):
                for lout, spotl in enumerate(local_spots):
                    trajectory_matrix[k][lout] = onTrajectory(spotk, spotl, local_spots)
                    trajectory_matrix[lout][k] = trajectory_matrix[k][lout]

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

def run_fiji_track_spot_mode(outpath=join(SIC_ROOT, SIC_PROCESSED), script_filename=join(SIC_ROOT, SIC_SCRIPTS, FIJI_TRACK_SCRIPT), niba=NIBA_ID, fiji=SIC_FIJI):
    '''Run FIJI for tracking spots'''
    print "----------------------------------------------------"
    print "Running FIJI..."
    lout = listdir(outpath)
    for fn in sorted(lout):
        print "Looking in:", fn
        # file name containing NIBA
        # Sic1_GFP3_[time]min_[index]_w[1|2][DIC|NIBA].TIF-mask.tif
        if fn.find(niba+".TIF") != -1: # run fiji only for files whose name contains NIBA_ID+".TIF"
            s = "%s %s -macro %s -batch" % (fiji, join(outpath, fn), script_filename)
            print "External call:", s
            #sucht unter Windows nur in SIC_FIJI/macros/
            call([fiji, join(outpath, fn), "-macro", script_filename, "-batch"])
    print "Finished running FIJI."


