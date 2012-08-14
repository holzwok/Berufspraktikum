# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

# please do not delete the following (use comment # to disable)
#mskpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#locpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\WT_SIC1_stR610_CLN2_stQ570\mask"
#locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\WT_SIC1_stR610_CLN2_stQ570"
mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\mask"
locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger"

maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
token_1 = "NG"
token_2 = "Qusar610"
tokens = [token_1, token_2]

from dircache import listdir
from os.path import join, exists
from PIL import Image #@UnresolvedImport
import os
import sqlite3

            
###################################################################################
# auxiliary functions

def extract_ID(separated_string, skip_at_end=1, separator="_"):
    '''returns strings stripped off the last skip_at_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[:-skip_at_end])

def extract_tail(separated_string, take_from_end=1, separator="_"):
    '''returns strings stripped off the last skip_at_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[-take_from_end:])

def get_maskfilename(locfile):
    #print "locfile =", locfile
    ID = extract_ID(locfile, 1)
    masks = listdir(mskpath)
    for mask in masks:
        if ID in mask:
            tail_of_maskfile = extract_tail(mask, 3)
            maskfile = ID+"_"+tail_of_maskfile
            #print "maskfile =", maskfile
            return maskfile
    print "unable to get mask filename for", locfile
    return ""


###################################################################################
# functions for main program

def setup_db(path=locpath, dbname='myspots.db'):
    print "setting up database...",
    filepath = join(path, dbname)
    if exists(filepath+"~"): os.remove(filepath+"~")
    if exists(filepath): os.rename(filepath, filepath+"~")
    con = sqlite3.connect(filepath)
    print "done."
    print "---------------------------------------------------------------"
    return con

def create_tables(con):
    print "creating tables...",
    con.execute('''DROP TABLE IF EXISTS locfiles''')
    con.execute("CREATE TABLE locfiles(locfilename VARCHAR(50), commonfileID VARCHAR(50), mode VARCHAR(50), PRIMARY KEY (locfilename))")
    
    con.execute('''DROP TABLE IF EXISTS cells''')
    con.execute("CREATE TABLE cells(cellID INT, maskfilename VARCHAR(50), commonfileID VARCHAR(50), PRIMARY KEY (cellID, commonfileID))")
    
    con.execute('''DROP TABLE IF EXISTS spots''')
    con.execute("CREATE TABLE spots(x FLOAT, y FLOAT, intensity FLOAT, frame INT, cellID INT, locfilename VARCHAR(50), PRIMARY KEY (x, y, frame), FOREIGN KEY (cellID) REFERENCES cells(cellID), FOREIGN KEY (locfilename) REFERENCES locfiles(locfilename))")

    con.commit()
    print "done."
    print "---------------------------------------------------------------"

def insert_cells():
    print "inserting masks into database...",
    lout = listdir(mskpath)
    for maskfile in lout:
        if maskfilename_token in maskfile:
            commonfileID = extract_ID(maskfile, skip_at_end=3)
            mask = Image.open(join(mskpath, maskfile)).convert("RGB")
            #mask.show()
            for cellID, color in enumerate(sorted([color[1] for color in mask.getcolors()])): 
            #for cellID, color in enumerate(sorted([color[1] for color in mask.getcolors()])[1:]): 
                # the [1:] skips the darkest color which is black and is the outside of cells
                querystring = "INSERT INTO cells VALUES('%s', '%s', '%s')" % (cellID, maskfile, commonfileID)
                #print querystring
                con.execute(querystring)
    con.commit()
    print "done."
    print "---------------------------------------------------------------"
    
def insert_locs():
    print "inserting locs into database...",
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            commonfileID = extract_ID(locfile, skip_at_end=1)
            if token_2 in locfile:
                mode = token_2
            else:
                mode = token_1
            querystring = "INSERT INTO locfiles VALUES('%s', '%s', '%s')" % (locfile, commonfileID, mode)
            #print querystring
            con.execute(querystring)
    con.commit()
    print "done."
    print "---------------------------------------------------------------"

def insert_spots():
    print "inserting spots into database..."
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            try:
                mask = Image.open(join(mskpath, get_maskfilename(locfile))).convert("RGB")
            except:
                print "image could not be opened, continuing."
                continue
            maskpixels = mask.load()
            colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
            colordict = dict(enumerate(colorlist))    
            inverse_colordict = dict((v,k) for k, v in colordict.items())

            print "considering file:", locfile
            with open(join(locpath, locfile), 'r') as f:
                for line in f:
                    data = line.split()
                    try:
                        x = data[0]
                        y = data[1]
                        intensity = data[2]
                        frame = data[3]
                        cellID = inverse_colordict[maskpixels[round(float(x)), round(float(y))]] # cell_ID but also color_ID
                        querystring = "INSERT INTO spots VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (x, y, intensity, frame, cellID, locfile)
                        #print querystring
                        con.execute(querystring)
                        con.commit()
                    except:
                        print "warning, unable to insert record:", line
                        #pass
    print "done."
    print "---------------------------------------------------------------"

def enhance_cells():
    print "calculating intensities...",
    c = con.cursor()
    querystring = "ALTER TABLE cells ADD total_intensity_NG FLOAT" # adding 2 columns at once did not work...
    c.execute(querystring)
    querystring = "ALTER TABLE cells ADD total_intensity_Qusar FLOAT"
    c.execute(querystring)

    querystring = "UPDATE cells SET total_intensity_NG = \
        (SELECT SUM(intensity) FROM spots JOIN locfiles ON locfiles.locfilename=spots.locfilename WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_1
    c.execute(querystring)

    querystring = "UPDATE cells SET total_intensity_Qusar = \
        (SELECT SUM(intensity) FROM spots JOIN locfiles ON locfiles.locfilename=spots.locfilename WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_2
    c.execute(querystring)

    con.commit()
    print "done."
    print "---------------------------------------------------------------"
    
    
def query_spots():
    c = con.cursor()
    c.execute('SELECT * FROM spots INNER JOIN cells ON cells.cellID=spots.cellID WHERE cells.cellID=1')
    #for counter in range(10):
    #    print c.fetchone()
    con.commit()
        
    
###################################################################################
# main program

if __name__ == '__main__':
    con = setup_db()
    create_tables(con)
    insert_cells()
    insert_locs()
    insert_spots()
    #query_spots()
    enhance_cells()