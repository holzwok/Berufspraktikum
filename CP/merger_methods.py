# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

# Script does not work with 16 Bit images

# please do not delete the following (use comment # to disable)
#mskpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#locpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#outpath =
mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\mask" # must not equal locpath!
outpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\out"
locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger"
#mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Test\mask_bf" # must not equal locpath!
#outpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Test\out"
#locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Test\Loc"

# naming rules as follows
# begining of names of loc, maskcell have to be the same
# Examples :
#MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min_1_w2NG.loc
#MAX_SIC1_stQ570_Clb5del_20120217_100pc_NG1000ms_0min_1_w2NG_maskcells.tif

maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
token_1 = "Qusar"
token_2 = "NG"
tokens = [token_1, token_2]
mRNAfrequenciesfile = "mRNA_frequencies.txt" # is also created in loc folder

from dircache import listdir
from os.path import join, exists
from PIL import Image, ImageDraw, ImageFont #@UnresolvedImport
from collections import Counter
#from time import sleep
import os
import sqlite3
import matplotlib.pyplot as plt


if mskpath==locpath:
    print "please change maskpath, aborting."
    import sys
    sys.exit()
            
###################################################################################
# auxiliary functions

def extract_ID(separated_string, skip_at_end=1, separator="_"):
    '''returns strings stripped off the last skip_at_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[:-skip_at_end])

def extract_tail(separated_string, take_from_end=1, separator="_"):
    '''returns the last take_from_end substrings separated by separator'''
    return separator.join(separated_string.split(separator)[-take_from_end:])

def extract_mode(name, tokens):
    for token in tokens: # error-prone if NG is in the filename somewhere else
        if token in extract_tail(name, take_from_end=1, separator="_"):
            return token
    else:
        print "mode not detectable:", token
        return ""

def get_maskfilename(locfile, mskpath):
    #print "locfile =", locfile
    ID = extract_ID(locfile, 1)
    masks = listdir(mskpath)
    for mask in masks:
        if ID in mask:
            tail_of_maskfile = extract_tail(mask, 3) # changed from 2
            maskfile = ID+"_"+tail_of_maskfile
            print "maskfile =", maskfile
            return maskfile
    print "unable to get mask filename for", locfile
    return ""

def median(numericValues):
    theValues = sorted(numericValues)
    if len(theValues)%2 == 1:
        return theValues[(len(theValues)+1)/2-1]
    else:
        lower = theValues[len(theValues)/2-1]
        upper = theValues[len(theValues)/2]
    return (float(lower + upper))/2  

def tiffile(locfile):
    return locfile[:-3]+"tif"

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
        
def backup_db(path=locpath, dbname='myspots.db'):
    print "backing up database...",
    filepath = join(path, dbname)
    if exists(filepath+"~"): os.remove(filepath+"~")
    if exists(filepath): os.rename(filepath, filepath+"~")
    print "done."
    print "---------------------------------------------------------------"

    
###################################################################################
# functions for main program

def setup_db(path=locpath, dbname='myspots.db'):
    filepath = join(path, dbname)
    print "setting up database at", filepath, "...",
    con = sqlite3.connect(filepath)
    print "done."
    print "---------------------------------------------------------------"
    return con

def create_tables(con):
    print "creating tables...",
    con.execute('''DROP TABLE IF EXISTS locfiles''')
    con.execute("CREATE TABLE locfiles(locfile VARCHAR(50), commonfileID VARCHAR(50), mode VARCHAR(50), PRIMARY KEY (locfile))")
    
    con.execute('''DROP TABLE IF EXISTS cells''')
    con.execute("CREATE TABLE cells(cellID INT, maskfilename VARCHAR(50), commonfileID VARCHAR(50), x_COG FLOAT, y_COG FLOAT, PRIMARY KEY (cellID, commonfileID))")
    
    con.execute('''DROP TABLE IF EXISTS spots''')
    con.execute("CREATE TABLE spots(spotID INTEGER PRIMARY KEY AUTOINCREMENT, x FLOAT, y FLOAT, intensity FLOAT, mRNA INT, frame INT, cellID INT, locfile VARCHAR(50), \
        FOREIGN KEY (cellID) REFERENCES cells(cellID), FOREIGN KEY (locfile) REFERENCES locfiles(locfile))")

    con.execute('''DROP TABLE IF EXISTS summary''')
    #con.execute("CREATE TABLE summary(sum_intensity FLOAT, count_mRNA INT, count_cellIDs INT, count_locfiles VARCHAR(50))")
    con.execute("CREATE TABLE summary(median_intensity FLOAT)")

    con.commit()
    print "done."
    print "---------------------------------------------------------------"

def get_COG(color, mask):
    '''returns the center of the ellipse in mask that has the given color'''
    width, height = mask.size
    #print width, height
    pix = mask.load()
    left = min([i for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # left boundary of ellipse
    upper = min([j for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # upper boundary of ellipse
    right = max([i for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # right boundary of ellipse
    lower = max([j for i in xrange(width) for j in xrange(height) if pix[i, j]==color]) # lower boundary of ellipse
    return (left+right)/2.0, (upper+lower)/2.0

def insert_cells(con, mskpath):
    print "inserting cells into database..."
    lout = listdir(mskpath)
    for maskfile in lout:
        if maskfilename_token in maskfile:
            print "considering mask file", maskfile, "..."
            commonfileID = extract_ID(maskfile, skip_at_end=3)
            mask = Image.open(join(mskpath, maskfile)).convert("RGB")
            #mask.show()
            colors = mask.getcolors()
            #print colors
            for cellID, color in enumerate(sorted([color[1] for color in colors])): 
                if color!=(0, 0, 0): # to exclude the background color
                    #print cellID, color
                    x, y = get_COG(color, mask)
                    querystring = "INSERT INTO cells VALUES('%s', '%s', '%s', '%s', '%s')" % (commonfileID+"_"+str(cellID), maskfile, commonfileID, x, y)
                    #print querystring
                    con.execute(querystring)
    con.commit()
    print "done."
    print "---------------------------------------------------------------"
    
def insert_locs(con, locpath, tokens):
    print "inserting locs into database...",
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            commonfileID = extract_ID(locfile, skip_at_end=1)
            # only the first occuring token is considered (i.e. the order matters)
            for token in tokens:
                print token
                print locfile
                if token in locfile:
                    mode = token
                    break
            querystring = "INSERT INTO locfiles VALUES('%s', '%s', '%s')" % (locfile, commonfileID, mode)
            #print querystring
            con.execute(querystring)
    con.commit()
    print "done."
    print "---------------------------------------------------------------"

def insert_spots(con, locpath, mskpath):
    print "inserting spots into database..."
    lin = listdir(locpath)
    for locfile in lin:
        if locfilename_token in locfile:
            try:
                mask = Image.open(join(mskpath, get_maskfilename(locfile, mskpath))).convert("RGB")
            except:
                print "image could not be opened, continuing."
                continue
            maskpixels = mask.load()
            colorlist = sorted([color[1] for color in mask.getcolors()]) # sorted from dark to bright
            colordict = dict(enumerate(colorlist))    
            inverse_colordict = dict((v,k) for k, v in colordict.items())

            print "considering loc file:", locfile
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
                        querystring = "INSERT INTO spots (x, y, intensity, frame, cellID, locfile) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (x, y, intensity, frame, cellID, locfile)
                        #print querystring
                        con.execute(querystring)
                        con.commit()
                    except:
                        print "warning, unable to insert record:", line
    print "done."
    print "---------------------------------------------------------------"

def calculate_RNA(intensities):
    ''' returns RNA as list using Aouefa's method '''
    if intensities==[]:
        return []
    else:
        med = median(intensities)
        print "median intensity of", len(intensities), "detected spots is", med, "."
        RNA = [int(0.5+intensity/med) for intensity in intensities]
        return RNA, med

def enhance_spots(con, tokens):
    print "calculating mRNAs..."
    c = con.cursor()
    c.execute('select intensity from spots')
    intensities = [intensity[0] for intensity in c.fetchall()]
    #print intensities
    RNA_list, med = calculate_RNA(intensities)
    print "found", sum(RNA_list), "mRNAs."
    RNAs = [(RNA, i+1) for i, RNA in enumerate(RNA_list)]
    #print RNAs
    c.executemany("UPDATE spots SET mRNA=? WHERE spotID=?", RNAs)
    con.commit()
    
    querystring = "ALTER TABLE spots ADD commonfileID VARCHAR(50)"
    c.execute(querystring)
    con.commit()
    
    querystring = "ALTER TABLE spots ADD mode VARCHAR(50)"
    c.execute(querystring)
    con.commit()
    
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
    
    # TODO:
    querystring = "INSERT INTO summary VALUES('%s')" % str(med)
    #print querystring
    c.execute(querystring)

    con.commit()

    print "done."
    print "---------------------------------------------------------------"
    
def enhance_cells(con, tokens):
    print "aggregating spot values to cell level..."
    c = con.cursor()

    for token in tokens:
        print "considering token:", token

        # write total intensity for token
        querystring = "ALTER TABLE cells ADD total_intensity_"+token+" FLOAT" # adding 2 columns at once did not work...
        c.execute(querystring)
        # write total number of spots for token
        querystring = "ALTER TABLE cells ADD number_of_spots_"+token+" INT"
        c.execute(querystring)
        # write total mRNA for token
        querystring = "ALTER TABLE cells ADD total_mRNA_"+token+" INT"  
        c.execute(querystring)
        con.commit()

    for token in tokens:
        # get all cells and the aggregated data from the spots table
        querystring = "SELECT cellID, SUM(intensity) AS total_intensity_"+token+", COUNT(spotID) AS number_of_spots_"+token+", \
            SUM(mRNA) AS total_mRNA_"+token+" FROM spots WHERE mode='"+token+"' GROUP BY cellID"
        c.execute(querystring)
        groupeddata = c.fetchall()
        # write the aggregated data to the cells table
        for item in groupeddata:
            #print item
            querystring = "UPDATE cells SET total_intensity_"+token+" = '"+str(item[1])+"', number_of_spots_"+token+" = '"+str(item[2])+"', total_mRNA_"+token+" = '"+str(item[3])+"' WHERE cellID = '"+str(item[0])+"'"
            #print querystring
            c.execute(querystring)
        con.commit()
    
    print "done."
    print "---------------------------------------------------------------"
    
def enhance_locs(con):
    print "aggregating spot values to locfile level..."
    c = con.cursor()

    querystring = "ALTER TABLE locfiles ADD number_of_spots INT"
    #print querystring
    c.execute(querystring)
    
    querystring = "ALTER TABLE locfiles ADD total_mRNA INT"
    #print querystring
    c.execute(querystring)
    
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
    print "---------------------------------------------------------------"
    
def scatter_plot_two_modes(con, outpath, token_1, token_2):
    print "creating scatter plot..."
    c = con.cursor()
    c.execute('select total_mRNA_'+token_1+', total_mRNA_'+token_2+' from cells')
    fetch = c.fetchall()
    #print "c.fetchall() =", fetch
    x = [x[0] if x[0] else 0 for x in fetch]
    #c.execute('select total_mRNA_Qusar from cells')
    y = [y[1] if y[1] else 0 for y in fetch]
    plt.figure()

    # scatterplot code starts here
    plt.scatter(x, y, color='tomato')    
    # scatterplot code ends here
    plt.title('mRNA frequencies per cell: comparison')
    plt.xlabel(token_1)
    plt.ylabel(token_2)
    figurepath = join(outpath, "figure2.png")
    plt.savefig(figurepath)
    #plt.show()
    print "saving figure to", figurepath, "... done."
    print "---------------------------------------------------------------"

def write_histogram_to_db(con, token, y):
    print "writing histogram to database..."
    tablename = "histogram_"+token
    print "updating table..."
    con.execute('''DROP TABLE IF EXISTS '''+tablename)
    con.execute('''CREATE TABLE '''+tablename+'''(bin INTEGER PRIMARY KEY, count INTEGER)''')
    
    for key in y:
        #print key, y[key]
        # now write to db
        querystring = "INSERT INTO "+tablename+" VALUES('%s', '%s')" % (str(key), str(y[key]))
        #print querystring
        con.execute(querystring)

    con.commit()

def plot_and_store_mRNA_frequency(con, token, outpath):
    print "creating mRNA histogram..."

    c = con.cursor()
    querystring = 'select total_mRNA_%s from cells' % token
    print querystring
    c.execute(querystring)
    x = [x[0] if x[0] else 0 for x in c.fetchall()]
    print x
    y = Counter(x)
    #print y
    #print y.keys()
    #print y.values()
    write_histogram_to_db(con, token, y)
    plt.figure()
    plt.bar(y.keys(), y.values(), width=0.8, color='b', align="center")
    plt.ylabel('Frequencies')
    plt.title('Frequency of mRNAs per cell ('+token+')')
    #plt.xticks(range(bins+1))
    plt.yticks(range(max(y.values())+2))
    plt.draw()
    figurepath = join(outpath, "figure1_" + token + ".png")
    plt.savefig(figurepath)
    #plt.show()
    print "saving figure to", figurepath, "... done."
    print "---------------------------------------------------------------"

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
    print "---------------------------------------------------------------"
    
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
    print "---------------------------------------------------------------"

    
###################################################################################
# main program

if __name__ == '__main__':
    con = setup_db()
    create_tables(con)
    insert_cells(con, mskpath)
    insert_locs(con, locpath, tokens)
    insert_spots(con, locpath, mskpath)
    enhance_spots(con, tokens)
    enhance_cells(con, tokens)
    enhance_locs(con)
    #scatter_plot_two_modes(con, outpath, token_1, token_2)
    plot_and_store_mRNA_frequency(con, token_1, outpath)
    plot_and_store_mRNA_frequency(con, token_2, outpath)
    #draw_crosses(con, locpath, outpath)
    #annotate_cells(con, locpath, outpath)
    #plt.show()
