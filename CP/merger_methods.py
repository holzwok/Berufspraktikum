
# by Martin Seeger
# changes by Dominique Sydow
# further changes by Konstantin Holzhausen

# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

'''
CAUTION!

script does not work with 16 bit images!

file names!
- choose a description for experiment and channel mode and name your files as follows:
  mask-file  <experiment>_<channel mode>.tif
  loc-file   <experiment>_<channel mode>.loc
  image-file <experiment>_<channel mode>_mask_cells.tif
- e.g. experiment is MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1 and channel mode is w3CY5:
  mask-file  MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5_mask_cells.tif
  loc-file   MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.loc
  image-file MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.tif
- you can use one mask for several channel modes: 
  mode of mask-file name can differ from mode of loc-file and image-file name 
- you will have to give your channel as input - 
  that name has to correspond (at least) partly to the name choosen in your file naming (e.g. CY5 for w3CY5)

directory structure!
- path to mask-files must not equal path to loc-files 
- recommended structure: make 3 directories called 
  mask (containing mask-files), output (containing all output) and loc (containing loc-files and image-files)
'''

#create variables and initialising
mskpath = 'mask'
outpath = 'out'
locpath = 'loc'

# please do not delete the following (use comment # to disable)
#mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\mask" # must not equal locpath!
#outpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\out"
#locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger"
#mskpath = r"/home/martin/imaging/msk/" # must not equal locpath!
#outpath = r"/home/martin/imaging/out/"
#locpath = r"/home/martin/imaging/loc/"
# mskpath = r"C:\Users\MJS\git\Berufspraktikum\CP\mask" # must not equal locpath!
# outpath = r"C:\Users\MJS\git\Berufspraktikum\CP\loc"
# locpath = r"C:\Users\MJS\git\Berufspraktikum\CP\loc"
# mskpath = r"/home/dominique/TBP/Test_Data_ximagexchannel/mask"
# outpath = r"/home/dominique/TBP/Test_Data_ximagexchannel/output"
# locpath = r"/home/dominique/TBP/Test_Data_ximagexchannel/loc"


#tokens = ["NG", "CY5", "Qusar", "CFP", "C002", "C003"] #C002 und C003 for Matthias
#group_by_cell = True # without GUI: decide here whether to normalise per cell (group_by_cell=True) or image (group_by_cell=False)


maskfilename_token = "_mask_cells"
dtr_token = "_mask_daughters"

locfilename_token = ".loc"
threshold = 3 # minimum number of RNAs for a transcription site


from dircache import listdir # python standard library
from os.path import join, exists # python standard library
from PIL import Image, ImageDraw, ImageFont #@UnresolvedImport
from collections import Counter # python standard library
import os # python standard library
import sqlite3 # python standard library
import matplotlib.pyplot as plt
import pandas
import numpy as np
import pickle # python standard library

if mskpath==locpath:
    print "please change maskpath (must not equal locpath), aborting."
    import sys
    sys.exit()
            
###################################################################################
# auxiliary functions

# examples for me :-)
# maskfile   MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5_mask_cells.tif
# locfile    MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.loc
# imagefile  MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.tif

def extract_ID(separated_string, skip_at_end=1, separator="_"):
    '''returns strings stripped off the last skip_at_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[:-skip_at_end])
# 1. input is str (filename)
# 2. split string into list of strings by separator "_" (components of filename in a list), leaving out last component
# 3. join again, output is str from input without last component in filename
# example for me :-) ... MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1

def extract_tail(separated_string, take_from_end=1, separator="_"):
    '''returns the last take_from_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[-take_from_end:])

# mode is NG or CY5 or ... (mode of microscopy)
def extract_mode(name, tokens):
    for token in tokens: # error-prone if NG is in the filename somewhere else
        if token in extract_tail(name, take_from_end=1, separator="_"):

            return token
    else:
        print "mode not detectable:", token
        return ""

def get_maskfilename(locfile, mskpath):
    '''
    Given a locfile name, constructs the corresponding maskfile name
    '''
    #print "locfile =", locfile
    ID = extract_ID(locfile, 1)
    masks = listdir(mskpath)
    for mask in masks:
        if ID in mask:
            tail_of_maskfile = extract_tail(mask, 3) # changed from 2 (mode is contained in maskfilename, imaging: 1 probe measured with 2 channels, result: 1 mask for 2 tokens)
            maskfile = ID + "_" + tail_of_maskfile
            print "mask file:", maskfile
            return maskfile
    print "unable to get mask filename for", locfile
    return ""

def median(numericValues):
    theValues = sorted(numericValues)
    if len(theValues)%2==1:
        return theValues[(len(theValues) + 1) / 2 - 1]
    else:
        lower = theValues[len(theValues) / 2 - 1]
        upper = theValues[len(theValues) / 2]
    return (float(lower + upper)) / 2  

def tiffile(locfile):
    '''
    For given locfile returns tiffile name
    '''
    return locfile[:-3] + "tif"

def get_COG(color, mask):
    '''returns the center of the ellipse in mask that has the given color'''
    width, height = mask.size
    #print width, height
    pix = mask.load()
    left = min([i for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # left boundary of ellipse
    upper = min([j for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # upper boundary of ellipse
    right = max([i for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # right boundary of ellipse
    lower = max([j for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # lower boundary of ellipse
    return (left + right) / 2.0, (upper + lower) / 2.0

def draw_cross(x, y, draw):
    x = int(x + 0.5)
    y = int(y + 0.5)
    draw.line([(x-4, y), (x+4,y)], fill="red")
    draw.line([(x, y-4), (x,y+4)], fill="red")

def write_into(filename, text, x, y):
    # this construction was necessary because often files had not been closed yet by the previous call
    # it is equivalent to "try until it works"
    while True:
        try:
            im = Image.open(filename)
            draw = ImageDraw.Draw(im)
            draw.text((x, y), text, fill="#ff0000") #, font=font)
            del draw 
            im.save(filename)
            break
        except:
            pass
        
def get_intensities(con, token):
    c = con.cursor()
    c.execute("select intensity, cellID from spots WHERE mode = '" + token + "'")
    data = c.fetchall()
    intensities = [(intensity[0], intensity[1]) for intensity in data] # list of tuples (intensity, cellID)
    return intensities

#Konstantin's code
def eval_dtr(con):
	c = con.cursor()
	#enquire if table "dtrs" exists
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dtrs';")
	retval = (c.fetchall() != [])
	return retval

def get_dtrs_intens(con, token):
	c = con.cursor()
	c.execute("SELECT spots.intensity,  dtr_spots.dtrID \
				FROM spots INNER JOIN dtr_spots ON dtr_spots.spotID = spots.spotID \
				WHERE mode='"+token+"';")
	data = c.fetchall()
	intensities = [(cell[0], cell[1]) for cell in data]
	return intensities
 
###################################################################################
# database functions

def backup_db(path=locpath, dbname='myspots.db'):
    print "backing up database...",
    filepath = join(path, dbname)
    if exists(filepath + "~"): 
        os.remove(filepath + "~")
    if exists(filepath): 
        os.rename(filepath, filepath + "~")
    print "done."
    print "-------------------------------------------------------"

def add_db_column(con, table, column, type):
    c = con.cursor()
    try:
        querystring = "ALTER TABLE " + table + " ADD " + column + " " + type
        c.execute(querystring)
        con.commit()
    except:
        print "unable to add column " + column + "to table " + table

def insert_one_row(con, table, valuetuple):
    insertstring = ", ".join(["'"+str(value)+"'" for value in valuetuple])
    #print insertstring
    querystring = "INSERT INTO " + table + " VALUES(%s)" % insertstring
    #print querystring
    con.execute(querystring)
    con.commit()
    
    
###################################################################################
# functions for main program

def setup_db(path=outpath, dbname='myspots.db'):
    filepath = join(path, dbname)
    print "setting up database at", filepath, "..."
    con = sqlite3.connect(filepath)
    print "done."
    print "-------------------------------------------------------\n"
    return con

def create_tables(con, op_mode):
	print "creating tables..."
	con.execute('''DROP TABLE IF EXISTS locfiles''')
	con.execute("CREATE TABLE locfiles(locfile VARCHAR(50), commonfileID VARCHAR(50), mode VARCHAR(50), PRIMARY KEY (locfile))")
	
	con.execute('''DROP TABLE IF EXISTS cells''')
	con.execute("CREATE TABLE cells(cellID INT, maskfilename VARCHAR(50), commonfileID VARCHAR(50), x_COG FLOAT, y_COG FLOAT, PRIMARY KEY (cellID, commonfileID))")
	
	"""Konstantin begin"""

	#clean off mother-daughter workspace
	con.execute('''DROP TABLE IF EXISTS cell_dtr_corr''')
	
	con.execute('''DROP TABLE IF EXISTS dtrs''') #daughter' s table
	con.execute('''DROP TABLE IF EXISTS dtr_spots''') #daughter-spot' s table
	if op_mode == "MD":
		con.execute("CREATE TABLE dtrs(dtrID INT PRIMARY KEY, cellID INT, x_COG FLOAT, y_COG FLOAT, FOREIGN KEY (cellID) REFERENCES cells(cellID))")
		con.execute("CREATE TABLE dtr_spots(row INTEGER PRIMARY KEY AUTOINCREMENT, spotID INT, dtrID INT, FOREIGN KEY (spotID) REFERENCES spots(spotID), FOREIGN KEY (dtrID) REFERENCES dtrs(dtrID))")
	
	"""Konstantin end"""
	
	con.execute('''DROP TABLE IF EXISTS spots''')
	con.execute("CREATE TABLE spots(spotID INTEGER PRIMARY KEY AUTOINCREMENT, x FLOAT, y FLOAT, intensity FLOAT, mRNA INT, transcription_site INT, mRNA_without_transcription_site INT, frame INT, \
		cellID INT, locfile VARCHAR(50), mode VARCHAR(50), \
		FOREIGN KEY (cellID) REFERENCES cells(cellID), FOREIGN KEY (locfile) REFERENCES locfiles(locfile))")
	
	con.execute('''DROP TABLE IF EXISTS summary''')
	#con.execute("CREATE TABLE summary(sum_intensity FLOAT, count_mRNA INT, count_cellIDs INT, count_locfiles VARCHAR(50))")
	#Konstantin's code
	if eval_dtr(con):
		con.execute("CREATE TABLE summary(token VARCHAR(50), median_intensity_for_all_cells FLOAT, median_intensity_for_all_dtrs FLOAT)")
	else:
		con.execute("CREATE TABLE summary(token VARCHAR(50), median_intensity_for_all_cells FLOAT)")
	
	con.commit()
	print "done."
	print "-------------------------------------------------------"

'''Konstantin begin'''
def insert_cells(con, mskpath, op_mode):
	"""
	take all masks, look for cells in them and write the cells into database
	"""
	print "inserting cells into database..."
	lout = listdir(mskpath)
	celldict = {}
	for maskfile in lout:
		if maskfilename_token in maskfile: #only those files that actually are masks
			print "considering mask file:", maskfile, "..."
			commonfileID = extract_ID(maskfile, skip_at_end=3) #example: input MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min_1_w2NG_mask_cells.tif, output MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min
			mask = Image.open(join(mskpath, maskfile))
			if not mask.mode=="RGB":
				mask = mask.convert("RGB")
			#mask.show()
			mask_d = "" #assign default value

			if op_mode == "MD":
				for mfile in lout:
					if (dtr_token in mfile) and (commonfileID in mfile):
						mask_d = Image.open(join(mskpath, mfile))
				
						if mask_d == "":
							print "no daughter's files found, continue ignoring"
						else:
							if not mask_d.mode=="RGB":
								mask_d = mask_d.convert("RGB")
							colors_dtr = mask_d.getcolors()
				
			colors = mask.getcolors()

			#for mask analysis, handle images as numpy arrays for performance reasons
			cells = np.array(mask)
			if mask_d != "":
				dtrs = np.array(mask_d)
		
			#print colors
			#example: [(5223, (17, 17, 17)), (3208, (13, 13, 13)), (3625, (11, 11, 11)), (3430, (7, 7, 7)), (4612, (5, 5, 5)), (4155, (3, 3, 3)), (235401, (1, 1, 1)), (2490, (2, 2, 2))]
			for cellID, color in enumerate(sorted([color[1] for color in colors])): 
				#[color[1] for color in colors] returns list with all color tuple
				#sorted(...) sorts color tuples
				#enumerate(...) returns to each color tuple a cellID starting from 0 where 0 is (1,1,1)
				if color!=(0, 0, 0) and color!=(1, 1, 1): # to exclude the background color
				#print cellID, color
					x, y = get_COG(color, mask)
					insert_one_row(con, "cells", (commonfileID+"_"+str(cellID), maskfile, commonfileID, x, y))
					celldict[commonfileID+"_"+str(cellID)] = [maskfile, commonfileID, x, y]
					cell_i = (cells == color) #generate binary images for further operations
					
					if mask_d != "": #evaluate daughters if wished
						for dtrID, color_d in enumerate(sorted(color[1] for color in colors_dtr)):
							
							if color_d!=(0, 0, 0) and color!=(1, 1, 1): #to exclude the background color
								dtrs_j = (dtrs == color_d)
								
								if cell_i.any() and dtrs_j.any(): #check for empty sets
									merge = cell_i | dtrs_j #actual binary merge
									#check if merge is subset of selected cell-region => daughter of cell_k cause
									#                                                    daughters are always part of their
									#                                                    mothers
									if np.equal(merge, cell_i).all():
										dtr_mask = Image.fromarray(dtrs_j, 'RGB')
										x, y = get_COG((1,1,1), dtr_mask) #binary
										insert_one_row(con, "dtrs", (commonfileID+"_daughter_"+str(dtrID),\
											commonfileID+"_"+str(cellID), x, y))
									
	pickle.dump(celldict, open("./cells.pkl", "wb"))
	print "done."
	print "-------------------------------------------------------"
'''Konstantin end'''

"""
def insert_cells(con, mskpath):
    
    take all masks, look for cells in them and write the cells into database
    maks
    print "inserting cells into database..."
    lout = listdir(mskpath)
    celldict = {}
    for maskfile in lout:
        if maskfilename_token in maskfile: #only those files that actually are masks
            print "considering mask file:", maskfile, "..."
            commonfileID = extract_ID(maskfile, skip_at_end=3) #example: input MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min_1_w2NG_mask_cells.tif, output MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min
            mask = Image.open(join(mskpath, maskfile))
            if not mask.mode=="RGB":
                mask = mask.convert("RGB")
            #mask.show()
            colors = mask.getcolors()
            #print colors
            #example: [(5223, (17, 17, 17)), (3208, (13, 13, 13)), (3625, (11, 11, 11)), (3430, (7, 7, 7)), (4612, (5, 5, 5)), (4155, (3, 3, 3)), (235401, (1, 1, 1)), (2490, (2, 2, 2))]
            for cellID, color in enumerate(sorted([color[1] for color in colors])): 
                #[color[1] for color in colors] returns list with all color tuple
                #sorted(...) sorts color tuples
                #enumerate(...) returns to each color tuple a cellID starting from 0 where 0 is (1,1,1)
                if color!=(0, 0, 0) and color!=(1,1,1): # to exclude the background color
                    #print cellID, color
                    x, y = get_COG(color, mask)
                    insert_one_row(con, "cells", (commonfileID+"_"+str(cellID), maskfile, commonfileID, x, y))
                    celldict[commonfileID+"_"+str(cellID)] = [maskfile, commonfileID, x, y]
    pickle.dump(celldict, open("./cells.pkl", "wb"))
    print "done."
    print "-------------------------------------------------------"
"""


def insert_cells_from_dict(con, mskpath):
    print "inserting cells from dict..."
    celldict = pickle.load(open("./cells.pkl", "r"))
    for cell in celldict:
        insert_one_row(con, "cells", [cell] + celldict[cell])
    con.commit()
    print "done."
    print "-------------------------------------------------------"

def insert_locs(con, locpath, tokens):
    """
    take all locfiles, look for tokens in them and write the filenames into database
    """
    print "inserting locs into database..."
    print 'tokens:', tokens
    #print 'channeltokens:', channeltokens
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            print "considering loc file:", locfile
            commonfileID = extract_ID(locfile, skip_at_end=1)
            # only the first occuring token is considered (i.e. the order matters if more than one token occurs)
            foundmode = False
            #print "considering token:", tokens
            print 'tokens:', tokens
            for token in tokens:   
                if token in locfile:
                    mode = token
                    foundmode = True
                    break
            if foundmode:
                print "found mode:", mode
            else:
                print "warning: locfile ", locfile, " does not contain acceptable mode!" 
            insert_one_row(con, "locfiles", (locfile, commonfileID, mode))
    print "done."
    print "-------------------------------------------------------"

"""Konstantin begin"""
def insert_spots(con, locpath, mskpath, tokens, op_mode):
	'''
	'''
	print "inserting spots into database..."
	lin = listdir(locpath)
	for locfile in lin:
		if locfilename_token in locfile:
			maskfilename = join(mskpath, get_maskfilename(locfile, mskpath))
			try:
				mask_cell = Image.open(maskfilename).convert("RGB")
			except:
				print "image could not be opened, continuing."
				continue
			
			if op_mode == "MD":
				try:
					print "associated daughters mask: ", extract_ID(maskfilename, skip_at_end=1)+"_daughters.tif"
					mask_dtr = Image.open(extract_ID(maskfilename, skip_at_end=1)+"_daughters.tif")
				except:
					print "daughters image could not be opened, continuing"
					continue

			maskpixels = mask_cell.load()
			colorlist = sorted([color[1] for color in mask_cell.getcolors()]) # sorted from dark to bright
			colordict = dict(enumerate(colorlist))    
			inverse_colordict = dict((v,k) for k, v in colordict.items())

			if op_mode == "MD":
				maskpixels_d = mask_dtr.load()
				colorlist_d = sorted([color[1] for color in mask_dtr.getcolors()]) #sorted from dark to bright
				colordict_d = dict(enumerate(colorlist_d))
				inverse_colordict_d = dict((v,k) for k, v in colordict_d.items())

			print "loc file: ", locfile
			commonfileID = extract_ID(locfile, skip_at_end=1)

			with open(join(locpath, locfile), 'r') as f:
				for line in f:
					data = line.split()
					try:
						x = data[0]
						y = data[1]
						intensity = data[2]
						frame = data[3]
						cellID = commonfileID+"_"+str(inverse_colordict[maskpixels[round(float(x)), round(float(y))]]) 
						# cell_ID but also color
						
						mode = extract_mode(join(locpath, locfile), tokens)
						querystring = "INSERT INTO spots (x, y, intensity, frame, cellID, locfile, mode) \
							VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (x, y, intensity, frame, cellID, locfile, mode)
						#print querystring
						con.execute(querystring)
						con.commit()
						
						if op_mode == "MD":
							con.text_factory = str
							c = con.cursor()
										
							for i in c.execute("SELECT dtrID FROM dtrs ORDER BY dtrID"): 
								
								index = inverse_colordict_d[maskpixels_d[round(float(x)), round(float(y))]]
								
								if int(extract_tail(i[0], take_from_end=1)) == index:
									dtrID = commonfileID+"_daughter_"+str(index)
									con.text_factory = unicode
									c.execute("SELECT max(spotID) FROM spots")
									spotID = c.fetchone()[0]
									c.execute("INSERT INTO dtr_spots (spotID, dtrID) VALUES('%s', '%s')" % (spotID, dtrID))
									con.commit()
									
					except:
						print "warning, unable to insert record:", line
	print "done."
	print "-------------------------------------------------------"

"""Konstantin end"""
"""def insert_spots(con, locpath, mskpath, tokens):


    print "inserting spots into database..."
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            try:
                mask_cell = Image.open(join(mskpath, get_maskfilename(locfile, mskpath))).convert("RGB")
            except:
                print "image could not be opened, continuing."
                continue

            maskpixels = mask_cell.load()
            colorlist = sorted([color[1] for color in mask_cell.getcolors()]) # sorted from dark to bright
            colordict = dict(enumerate(colorlist))    
            inverse_colordict = dict((v,k) for k, v in colordict.items())

            print "loc file: ", locfile
            commonfileID = extract_ID(locfile, skip_at_end=1)
            
            with open(join(locpath, locfile), 'r') as f:
                for line in f:
                    data = line.split()
                    try:
                        x = data[0]
                        y = data[1]
                        intensity = data[2]
                        frame = data[3]
                        cellID = commonfileID+"_"+str(inverse_colordict[maskpixels[round(float(x)), round(float(y))]]) # cell_ID but also color_ID
                        mode = extract_mode(join(locpath, locfile), tokens)
                        querystring = "INSERT INTO spots (x, y, intensity, frame, cellID, locfile, mode) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (x, y, intensity, frame, cellID, locfile, mode)
                        #print querystring
                        con.execute(querystring)
                        con.commit()
                    except:
                        print "warning, unable to insert record:", line
    print "done."
    print "-------------------------------------------------------"
"""

def calculate_RNA(intensities, group_by_cell=False):
    ''' 
    returns RNA as list using Aouefa's method
    If group_by_cell==True then RNAs are normalized per cell, else by image
    '''
    # intensities from def get_intensities (# list of tuples (intensity, cellID)) and def enhance_spots
    if intensities==[]:
        return []
    elif group_by_cell: # group_by_cell==True
        intensityvalues = [intensity[0] for intensity in intensities] # intensities list of tuples (intensity, cellID)
        cellIDs = [intensity[1] for intensity in intensities]
        data_frame = pandas.DataFrame({'intensity': intensityvalues, 'cellID': cellIDs})
        float_RNAs = data_frame['intensity'] / data_frame.groupby('cellID')['intensity'].transform(np.median)
        data_frame['RNA'] = [int(0.5 + float_RNA) for float_RNA in float_RNAs]
        #print data_frame
        RNA = data_frame['RNA'] 
        print "median intensity of", len(intensities), "detected spots is", median(intensityvalues), "."
        med = list(data_frame.groupby('cellID')['intensity'].transform(np.median))
        return RNA, med # RNA is pandas.DataFrame, med is list of floats
    else: # group_by_cell==False
        # changed by Dominique 
        # intensities is in this merger_methods-version - in contrast to the last one without median per cell- a list of tuples
        # for Aouefa's method we need to extract the intensities as a list called intensityvalues
        intensityvalues = [intensity[0] for intensity in intensities] # intensities list of tuples (intensity, cellID)
        #med = median(intensities)[0] from Aouefa's method
        med = median(intensityvalues)
        print "median intensity of", len(intensities), "detected spots is", med, "."
        RNA = [int(0.5 + intensity[0] / med) for intensity in intensities]
        return RNA, med # RNA is list of int, med is float

def enhance_spots(con, tokens, group_by_cell):
    '''
    enter mRNA into spots table
    '''
    print "aggregating spot values to spots level..." # by Dominique
    
    c = con.cursor()

    # for each token calculate and insert into spots table for each spot: 
        # number of mRNAs 
        # number of transcription sites 
        # number of mRNAs per spot without mRNAs at transcription site (named functional_mRNA)
    
    # important! creat variable blub that enhancing spotID, otherwise the following for loop will always overwrite columns starting each time at spotID 1
    blub = 0
    for token in tokens:
        print
        # number of mRNAS
        print "calculating number of mRNAs for token " + token + "..."
        intensities = get_intensities(con, token) # list of tuples (intensity, cellID) 
        RNA_list, med = calculate_RNA(intensities, group_by_cell)
        print "found", sum(RNA_list), "mRNAs for token " + token + "."
        RNAs = [(int(RNA), int(i+1)) for i, RNA in enumerate(RNA_list)] # list of tuples, int(RNA): integer for RNA because number of RNA is needed, int(i+1): enumerate generates values from 0, for spotID we need values from 1
        # important to convert tuple values to int, otherwise in some cases (e.g. value being numpy value for group_by_cell True) problems with writing values to table
        RNAs = [(i, j+blub) for i, j in RNAs] # by Dominique
        c.executemany("UPDATE spots SET mRNA=? WHERE spotID=?", RNAs)
        con.commit()

        # number of transcriptions sites
        print "calculating number of transcription sites for token " + token + "..."
        transcription_sites = [(int((RNA>=threshold)*1.0), int(i+1)) for i, RNA in enumerate(RNA_list)] # False*1==0, True*1==1
        # important to convert tuple values to int, otherwise in some cases (e.g. value being numpy value for group_by_cell True) problems with writing values to table
        print "found", int(sum([i for i,j in transcription_sites])), "transcription site(s) for token " + token + "."
        transcription_sites = [(i, j+blub) for i, j in transcription_sites] # by Dominique
        c.executemany("UPDATE spots SET transcription_site=? WHERE spotID=?", transcription_sites)
        con.commit()

        # number of mRNAs per spot without mRNAs at transcription site (named functional_mRNA)
        # by Dominique
        print "calculating number of functional/cytoplasmic mRNAs (without mRNAs at transcription sites) for token " + token + "..."
        functional_mRNA = [(int((RNA<threshold)*int(RNAs[i][0])), int(i+1)) for i, RNA in enumerate(RNA_list)]
        # important to convert tuple values to int, otherwise in some cases (e.g. value being numpy value for group_by_cell True) problems with writing values to table
        print "found", sum(RNA_list)-int(sum([i for i,j in transcription_sites])), "functional mRNAs for token " + token + "."
        functional_mRNA = [(i, j+blub) for i, j in functional_mRNA] # by Dominique
        c.executemany("UPDATE spots SET mRNA_without_transcription_site=? WHERE spotID=?", functional_mRNA)
        con.commit()
        
        # important! enhancing spotID, otherwise for loop will always overwrite columns starting each time at spotID 1
        blub = blub + len(RNAs)
        
    # insert into spots table: commonfileID
    add_db_column(con, "spots", "commonfileID", "VARCHAR(50)")
    c.execute('select locfile from spots')
    commonfileIDs = [(extract_ID(locfile[0], skip_at_end=1), i+1) for i, locfile in enumerate(c.fetchall())]
    #print commonfileIDs
    c.executemany("UPDATE spots SET commonfileID=? WHERE spotID=?", commonfileIDs)
    con.commit()


    c.execute('select locfile from spots')
    modes = [(extract_mode(locfile[0], tokens), i+1) for i, locfile in enumerate(c.fetchall())]
    #print modes
    c.executemany("UPDATE spots SET mode=? WHERE spotID=?", modes)
    con.commit()

    print "done."
    print "-------------------------------------------------------"


def enhance_cells(con, tokens):
	'''
	takes all spot level values and aggregates them to cell level
	'''
	print "aggregating spot values to cell level..."
	c = con.cursor()

	# for each token, add intensity, number of spots and transcription sites as empty columns to cells table
	for token in tokens:
		print "considering token:", token
		
		add_db_column(con, "cells", "total_intensity_"+token, "FLOAT")
		add_db_column(con, "cells", "number_of_spots_"+token, "INT")
		add_db_column(con, "cells", "total_mRNA_"+token, "INT")
		add_db_column(con, "cells", "total_transcription_sites_"+token, "INT")
		add_db_column(con, "cells", "total_mRNA_without_transcription_sites_"+token, "INT") # new by Dominique
		add_db_column(con, "cells", "median_intensity_"+token, "INT")
		
		#Konstantin's code
		#check if table dtrs exists => evaluate daughters seperately
		if eval_dtr(con):
			add_db_column(con, "dtrs", "dtr_total_intensity_"+token, "FLOAT")
			add_db_column(con, "dtrs", "dtr_number_of_spots_"+token, "INT")
			add_db_column(con, "dtrs", "dtr_total_mRNA_"+token, "INT")
			add_db_column(con, "dtrs", "dtr_total_transcription_sites_"+token, "INT")
			add_db_column(con, "dtrs", "dtr_total_mRNA_without_transcription_sites_"+token, "INT")
			add_db_column(con, "dtrs", "dtr_median_intensity_"+token, "INT")
			
	'''
	# Martin's code!!!
	for token in tokens:
        # get all cells and the aggregated data from the spots table
        querystring = "SELECT cellID, SUM(intensity) AS total_intensity_"+token+", COUNT(spotID) AS number_of_spots_"+token+", \
            SUM(mRNA) AS total_mRNA_"+token+", \
            SUM(transcription_site) AS total_transcription_sites_"+token+" FROM spots WHERE mode='"+token+"' GROUP BY cellID"
        c.execute(querystring)
        groupeddata = c.fetchall()

        # write the aggregated data to the cells table
        for item in groupeddata:
            #print "item =", item
            querystring = "UPDATE cells SET total_intensity_"+token+" = '"+str(item[1])+"', \
            number_of_spots_"+token+" = '"+str(item[2])+"', \
            total_mRNA_"+token+" = '"+str(item[3])+"', \
            total_transcription_sites_"+token+" = '"+str(item[4])+"' \
            WHERE cellID = '"+str(item[0])+"'"
            #print querystring
            c.execute(querystring)
        con.commit()
	'''
	
	for token in tokens:
		# get all cells and the aggregated data from the spots table
		querystring = "SELECT cellID, \
			SUM(intensity) AS total_intensity_"+token+", \
			COUNT(spotID) AS number_of_spots_"+token+", \
			SUM(mRNA) AS total_mRNA_"+token+", \
			SUM(transcription_site) AS total_transcription_sites_"+token+", \
			SUM(mRNA_without_transcription_site) AS total_mRNA_without_transcription_sites_"+token+" \
			FROM spots \
			WHERE mode='"+token+"' \
			GROUP BY cellID"
		c.execute(querystring)
		groupeddata = c.fetchall()
		
		# write the aggregated data to the cells table
		for item in groupeddata:
			#print "item =", item
			querystring = "UPDATE cells \
				SET total_intensity_"+token+" = '"  +str(item[1])+  "', \
				number_of_spots_"+token+" = '"+str(item[2])+"', \
				total_mRNA_"+token+" = '"+str(item[3])+"', \
				total_transcription_sites_"+token+" = '"+str(item[4])+"', \
				total_mRNA_without_transcription_sites_"+token+" = '"+str(item[5])+"'\
				WHERE cellID = '"+str(item[0])+"'"
			#print querystring
			c.execute(querystring)
		
		#Konstantin's code
		#basically just do it again
		if eval_dtr(con):
			c.execute("SELECT dtr_spots.dtrID, \
					SUM(intensity) AS dtr_total_intensity_"+token+", \
					COUNT(dtr_spots.spotID) AS dtr_number_of_spots_"+token+", \
					SUM(mRNA) AS dtr_total_mRNA_"+token+", \
					SUM(transcription_site) AS dtr_total_transcription_sites_"+token+", \
					SUM(mRNA_without_transcription_site) AS dtr_mRNA_without_transcription_sites_"+token+" \
				FROM dtr_spots INNER JOIN spots \
					ON dtr_spots.spotID = spots.spotID \
				WHERE mode='"+token+"'\
				GROUP BY dtr_spots.dtrID;")
			
			for item in c.fetchall():
				c.execute("UPDATE dtrs \
					SET dtr_total_intensity_"+token+" = '"  +str(item[1])+  "', \
						dtr_number_of_spots_"+token+" = '"+str(item[2])+"', \
						dtr_total_mRNA_"+token+" = '"+str(item[3])+"', \
						dtr_total_transcription_sites_"+token+" = '"+str(item[4])+"', \
						dtr_total_mRNA_without_transcription_sites_"+token+" = '"+str(item[5])+"'\
					WHERE dtrID = '"+str(item[0])+"'")
						
						
		# write to all fields that were left empty 0
		# condition: where total_intensity is NULL/empty (when total_intensity of a cell is 0 all to that cell related fields must be 0 also)
		querystring = "UPDATE cells \
			SET total_intensity_"+token+" = '0', \
				number_of_spots_"+token+" = '0', \
				total_mRNA_"+token+" = '0', \
				total_transcription_sites_"+token+" = '0', \
				total_mRNA_without_transcription_sites_"+token+" = '0'\
			WHERE total_intensity_"+token+" IS NULL"
		c.execute(querystring)
	
		if eval_dtr(con):
			querystring = "UPDATE dtrs \
				SET dtr_total_intensity_"+token+" = '0', \
					dtr_number_of_spots_"+token+" = '0', \
					dtr_total_mRNA_"+token+" = '0', \
					dtr_total_transcription_sites_"+token+" = '0', \
					dtr_total_mRNA_without_transcription_sites_"+token+" = '0'\
				WHERE dtr_total_intensity_"+token+" IS NULL"
			c.execute(querystring)

		con.commit()
		
	print "done."
	print "-------------------------------------------------------"
    
def enhance_locs(con):
    print "aggregating spot values to locfile level..."
    c = con.cursor()

    add_db_column(con, "locfiles", "number_of_spots", "INT")
    add_db_column(con, "locfiles", "total_mRNA", "INT")
    
    c.execute('SELECT mode, commonfileID, sum(mRNA), count(spotID) FROM spots GROUP BY mode, commonfileID')
    groupeddata = c.fetchall()
    #print groupeddata
    for item in groupeddata:
        querystring = "UPDATE locfiles SET number_of_spots = '%s' WHERE mode='%s' AND commonfileID = '%s'" % (str(item[3]), str(item[0]), str(item[1]))
        #print querystring
        c.execute(querystring)
        querystring = "UPDATE locfiles SET total_mRNA = '%s' WHERE mode='%s' AND commonfileID = '%s'" % (str(item[2]), str(item[0]), str(item[1]))
        #print querystring
        c.execute(querystring)

    con.commit()
    print "done."
    print "-------------------------------------------------------"

"""
# by Dominique: I don't see why it is necessary to have 2 methods for that, why not merging them to one? 
# I don't know why but the method add_median_to_cells_token does not take intensities from add_median_to_cells

def add_median_to_cells_token(con, intensities, token):
    print "group_by_cell = ", group_by_cell
    print "warning: the GUI checkbox is not working"

    if not group_by_cell:
        print "group_by_cell is False, so not adding median to cell"

    else:
        df = pandas.DataFrame(intensities)
        df.columns = ["intensity", "cellID"]
        #print df.groupby("cellID").median()
        cellmediansdf = df.groupby("cellID").median()
        cellIDs = [str(cell) for cell in cellmediansdf.index.values]
        medints = cellmediansdf["intensity"].values
        cellmedians = zip(medints, cellIDs)

        c = con.cursor()
        c.executemany("UPDATE cells SET median_intensity_"+token+"=? WHERE cellID=?", cellmedians)
        con.commit()

def add_median_to_cells(con):
    for token in tokens:
        intensities = get_intensities(con, token)
        add_median_to_cells_token(con, intensities, token)
    print "done."
    print "-------------------------------------------------------"
"""

def add_median_to_cells(con, tokens, group_by_cell):
	print "group_by_cell = ", group_by_cell
	# print "warning: the GUI checkbox is not working" # it is working now ... :-)
	for token in tokens:
		if not group_by_cell:
			print "group_by_cell is False, so not adding median to cell" # group_by_cell==False means normalisation per image folder
		else:
			intensities = get_intensities(con, token)  # intensities list of tuples (intensity, cellID)
			#print intensities
			df = pandas.DataFrame(intensities)
			#print df    
			df.columns = ["intensity", "cellID"]
			#print df
			#print df.groupby("cellID").median()
			cellmediansdf = df.groupby("cellID").median()
			cellIDs = [str(cell) for cell in cellmediansdf.index.values]
			medints = cellmediansdf["intensity"].values
			cellmedians = zip(medints, cellIDs)
				
			#Konstantin's code
			if eval_dtr(con):
				intensities = get_dtrs_intens(con, token)
				df = pandas.DataFrame(intensities)
				df.columns = ["intensity", "dtrID"]
				#actually calculating median
				dtrmediansdf = df.groupby("dtrID").median()
				dtrIDs = [str(dtr) for dtr in dtrmediansdf.index.values]
				dtr_medints = dtrmediansdf["intensity"].values
				dtrmedians = zip(dtr_medints, dtrIDs)
				c = con.cursor()
				c.executemany("UPDATE dtrs SET dtr_median_intensity_"+token+"=? WHERE dtrID =?", dtrmedians)
				con.commit()
        		
			c = con.cursor()
			c.executemany("UPDATE cells SET median_intensity_"+token+"=? WHERE cellID=?", cellmedians)
			con.commit()
	print "done."
	print "-------------------------------------------------------"

def insert_summary(con, tokens):    
	# summary contains so far only one value: median intensity for all cells (in image folder/per experiment)
	# this value is also printed out in the shell
	
	print "creating summary table that contains median intensity for all cells..."
	
	# Martin's version
	# con.execute('''DROP TABLE IF EXISTS summary''') # already in create_tables
	# # insertstring contains colums for summary table:
	# insertstring = ""
	# for token in tokens
	#     insertstring += "median_intensity_for_all_cells_" + token + " FLOAT,"
	# insertstring = insertstring[:-1] # remove last comma
	# con.execute("CREATE TABLE summary(" + insertstring + ")") #here Aouefa's ERROR: summary table already exists
	# con.commit()
	# for token in tokens:
	#     intensities = get_intensities(con, token)
	#     intensityvalues = [intensity[0] for intensity in intensities]
	#     '''
	#     # following code is wrong, intensities have to be transformed into intensityvalues in both cases
	#     if not group_by_cell:
	#         # if group_by_cell=False meaning normalisation per image
	#         intensityvalues = intensities  
	#     else:
	#         intensityvalues = [intensity[0] for intensity in intensities]
	#     '''
	#     querystring = "INSERT INTO summary (median_intensity_for_all_cells_" + token + ") VALUES('%s')" % (median(intensityvalues))
	#     #print querystring
	#     con.execute(querystring)
	#     con.commit()
	# Dominique's version - rearranging table structure...
	for token in tokens:
		intensities = get_intensities(con, token)
		intensityvalues = [intensity[0] for intensity in intensities]
		
		querystring = "INSERT INTO summary (token,median_intensity_for_all_cells) VALUES('%s', '%s')" % (token, median(intensityvalues))
		#print querystring
			
		#Konstantin's Code:
		if eval_dtr(con):
			dtr_intensities = get_dtrs_intens(con, token)
			dtr_int_vals = [intensity[0] for intensity in intensities]
			querystring = "INSERT INTO summary (token,median_intensity_for_all_cells, median_intensity_for_all_dtrs) \
				 VALUES('%s', '%s', '%s')" % (token, median(intensityvalues), median(dtr_int_vals))
				
		con.execute(querystring)
		con.commit()
	
	print "done."
	print "-------------------------------------------------------"

"""Konstantin begin"""

def merge_tables(con):
	#merging dtrs table into results table
	c = con.cursor()
	c.execute("DROP TABLE IF EXISTS cell_dtr_corr;") 
	c.execute("CREATE TABLE cell_dtr_corr AS SELECT * FROM cells LEFT JOIN dtrs USING(cellID);")
	con.commit()

"""Konstantin end"""

def scatter_plot_two_modes(con, outpath, token_1, token_2):
    # plotting mRNA amount in two modes for each cell against each other
    # each data point represents two types of mRNA (referring to the two modes) in the same cell 
    print "creating scatter plot..."
    c = con.cursor()
    c.execute('select total_mRNA_without_transcription_sites_'+token_1+', total_mRNA_without_transcription_sites_'+token_2+' from cells') # changed total_mRNA_%s to total_mRNA_without_transcription_sites_%s
    fetch = c.fetchall()
    #print "c.fetchall() =", fetch
    x = [x[0] if x[0] else 0 for x in fetch]
    #c.execute('select total_mRNA_Qusar from cells')
    y = [y[1] if y[1] else 0 for y in fetch]
    plt.figure()

    # scatterplot code starts here
    plt.scatter(x, y, color='tomato')
    plt.axis([-0.1, max(max(x), max(y))+0.1, -0.1, max(max(x), max(y))+0.1]) # x- and y-axis equal
    # scatterplot code ends here
    plt.title('functional mRNA frequencies per cell')
    plt.xlabel(token_1)
    plt.ylabel(token_2)
    figurepath = join(outpath, "figure2_"+token_1+"_"+token_2+".png")
    plt.savefig(figurepath)
    #plt.show()
    print "saving figure to", figurepath, "... done."
    print "-------------------------------------------------------"

def plot_and_store_mRNA_frequency(con, token, outpath):
    print "creating mRNA histogram..."

    c = con.cursor()
    querystring = 'select total_mRNA_without_transcription_sites_%s from cells' % token # changed total_mRNA_%s to total_mRNA_without_transcription_sites_%s
    print querystring
    c.execute(querystring)
    x = [x[0] if x[0] else 0 for x in c.fetchall()] # list of int containing total functional mRNA for each cell
    y = Counter(x) # collections.Counter type: like dict - VALUE containing frequency of cells containing a specific amount of mRNA (stored as KEY)
    # y.values() is list of values grouped by descending order
    # y.keys() is the corresponding list of keys
    # sum(y.values()) is total amount of cells
    print sum(y.values())
    relative_y = [float(i)/float(sum(y.values()))for i in y.values()]

    plt.figure()

    '''
    # for absolute y axis (absolute number of cells)
    plt.bar(y.keys(), y.values(), width=0.8, color='b', align="center")
    plt.ylabel('Frequencies')
    plt.title('Frequency of mRNAs per cell ('+token+')')
    #plt.xticks(range(bins+1))
    plt.yticks(range(max(y.values())+2))
    plt.draw()
    '''

    # for relative y axis (relative number of cells)
    plt.bar(y.keys(), relative_y, width=0.8, color='b', align="center")
    plt.ylabel('Relative frequencies')
    plt.xlabel('Number of mRNAs per cell')
    plt.title('Distribution of mRNAs per cell ('+token+')')
    plt.xticks(range(0, max(x)+1))
    plt.yticks(np.arange(0.0, 1.1, 0.1))
    # write some infos into the figure:
    ## total number of cells
    info_text = "total number of cells: " + str(len(x))
    plt.figtext(0.4, 0.85, info_text)
    ## median intensity for all cells
    c.execute("SELECT median_intensity_for_all_cells FROM summary WHERE token = '" + token + "'")
    info = c.fetchall() # info is list containing one tuple containing one value, calling that value via info[0][0]
    print info[0][0]
    info_text = "median intensity for all cells: " + str(info[0][0])
    plt.figtext(0.4, 0.8, info_text)
    plt.draw()
    figurepath = join(outpath, "figure1_" + token + ".png")
    plt.savefig(figurepath)
    #plt.show()
    print "saving figure to", figurepath, "... done."
    print "-------------------------------------------------------"

def draw_crosses(con, locpath, outpath):
    print "drawing crosses over found spots..."
    c = con.cursor()
    c.execute('SELECT x, y, locfile FROM spots')
    cross_data = [(x, y, tiffile(locfile)) for (x, y, locfile) in c.fetchall()]
    #for point in cross_data:
    #    print point

    c.execute('SELECT locfile FROM spots GROUP BY locfile')
    tiffiles = [tiffile(locfile[0]) for locfile in c.fetchall()]
    #print tiffiles
    for tif in tiffiles:
        outtif = "out."+tif
        print "drawing into file", outtif
        orig = Image.open(join(locpath, tif)).copy().convert("RGB")
        points = [(x, y) for (x, y, filename) in cross_data if filename==tif]
        #print points
        for x, y in points:
            #print "found spot at", x, y
            draw = ImageDraw.Draw(orig)
            draw_cross(x, y, draw)
        #orig = Image.blend(orig, Image.open(join(locpath, tif)), 0.5)
        orig.save(join(outpath, outtif))

    print "done."
    print "-------------------------------------------------------"
    
def annotate_cells(con, locpath, outpath):
    print "annotating cells..."
    c = con.cursor()
    c.execute('SELECT locfile FROM spots GROUP BY locfile')
    tiffiles = [tiffile(locfile[0]) for locfile in c.fetchall()]
    for tif in tiffiles:
        tifcommonfile = extract_ID(tif, skip_at_end=1, separator="_")
        outtif = "out."+tif
        print "writing annotations into file", outtif
        outfilepath = join(outpath, outtif)
        # create outfile if it does not exist
        if not os.path.isfile(join(outpath, outtif)):
            orig = Image.open(join(locpath, tif)).copy().convert("RGB")
            orig.save(outfilepath)            
            
        c.execute('SELECT cellID, x_COG, y_COG FROM cells')
        celllist = c.fetchall()
        #print "celllist =", celllist
        for cell, x, y in celllist:
            cellname = extract_tail(str(cell), take_from_end=2, separator="_")
            cellcommonfile = extract_ID(cell, skip_at_end=1, separator="_")
            #print cellcommonfile
            #print cellname, x, y
            cellnumber = extract_tail(cellname, take_from_end=1, separator="_")
            if cellcommonfile==tifcommonfile:
                if cellnumber != '0': # 0 is the background
                    write_into(outfilepath, cellname, x, y)
                    #orig.save(outfilepath)

    print "done."
    print "-------------------------------------------------------"

    
###################################################################################
# main program

if __name__ == '__main__':
    con = setup_db()
    create_tables(con)
    insert_cells(con, mskpath)
    insert_locs(con, locpath, tokens)
    insert_spots(con, locpath, mskpath, tokens)
    # enhance_spots(con, tokens, group_by_cell)
    # enhance_cells(con, tokens)
    # enhance_locs(con)
    # insert_summary(con, tokens)

    # add_median_to_cells(con, tokens, group_by_cell)

    # if len(channeltokens)>=2:
    #     print "creating scatter plot for", channeltokens[0], channeltokens[1]
    #     scatter_plot_two_modes(con, outpath, channeltokens[0], channeltokens[1])

    # for token in tokens:
    #     print "creating frequency plot for", token
    #     plot_and_store_mRNA_frequency(con, token, outpath)

    # draw_crosses(con, locpath, outpath)
    # annotate_cells(con, locpath, outpath)
