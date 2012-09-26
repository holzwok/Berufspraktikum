# This script assumes that CellProfiler has been used to create masks
# For this purpose, load the pipeline 'cell_recognition_with_mask.cp'

# please do not delete the following (use comment # to disable)
#mskpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#locpath = r"X:/FISH/Images/20120608_Whi5pGFP_FISH_Osmostress/Osmoanalysis_Locfiles"
#outpath =
mskpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\mask" # must not equal locpath!
outpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\out"
locpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger"

maskfilename_token = "_mask_cells"
locfilename_token = ".loc"
token_1 = "Qusar"
token_2 = "NG"
tokens = [token_1, token_2]
mRNAfrequenciesfile = "mRNA_frequencies.txt" # is also created in loc folder

from dircache import listdir
from os.path import join, exists
from PIL import Image, ImageDraw, ImageChops #@UnresolvedImport
import os
import sqlite3
import cPickle
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

def extract_mode(name):
    for token in tokens: # error-prone if NG is in the filename somewhere else
        if token in extract_tail(name, take_from_end=1, separator="_"):
            return token
    else:
        return ""

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
    print "setting up database...",
    filepath = join(path, dbname)
    con = sqlite3.connect(filepath)
    print "done."
    print "---------------------------------------------------------------"
    return con

def create_tables(con):
    print "creating tables...",
    con.execute('''DROP TABLE IF EXISTS locfiles''')
    con.execute("CREATE TABLE locfiles(locfile VARCHAR(50), commonfileID VARCHAR(50), mode VARCHAR(50), PRIMARY KEY (locfile))")
    
    con.execute('''DROP TABLE IF EXISTS cells''')
    con.execute("CREATE TABLE cells(cellID INT, maskfilename VARCHAR(50), commonfileID VARCHAR(50), PRIMARY KEY (cellID, commonfileID))")
    
    con.execute('''DROP TABLE IF EXISTS spots''')
    con.execute("CREATE TABLE spots(spotID INTEGER PRIMARY KEY AUTOINCREMENT, x FLOAT, y FLOAT, intensity FLOAT, mRNA INT, frame INT, cellID INT, locfile VARCHAR(50), \
        FOREIGN KEY (cellID) REFERENCES cells(cellID), FOREIGN KEY (locfile) REFERENCES locfiles(locfile))")

    con.execute('''DROP TABLE IF EXISTS summary''')
    con.execute("CREATE TABLE summary(sum_intensity FLOAT, count_mRNA INT, count_cellIDs INT, count_locfiles VARCHAR(50))")

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
                querystring = "INSERT INTO cells VALUES('%s', '%s', '%s')" % (commonfileID+"_"+str(cellID), maskfile, commonfileID)
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
            if token_1 in locfile:
                mode = token_1
            else:
                mode = token_2
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
        return RNA

def enhance_spots():
    print "calculating mRNAs..."
    c = con.cursor()
    c.execute('select intensity from spots')
    intensities = [intensity[0] for intensity in c.fetchall()]
    #print intensities
    RNA_list = calculate_RNA(intensities)
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
    modes = [(extract_mode(locfile[0]), i+1) for i, locfile in enumerate(c.fetchall())]
    #print modes
    c.executemany("UPDATE spots SET mode=? WHERE spotID=?", modes)
    con.commit()

    print "done."
    print "---------------------------------------------------------------"
    
def enhance_cells():
    print "aggregating spot values to cell level...",
    c = con.cursor()
    querystring = "ALTER TABLE cells ADD total_intensity_NG FLOAT" # adding 2 columns at once did not work...
    c.execute(querystring)
    
    querystring = "ALTER TABLE cells ADD total_intensity_Qusar FLOAT"
    c.execute(querystring)
    
    querystring = "ALTER TABLE cells ADD number_of_spots_NG INT"
    c.execute(querystring)
    
    querystring = "ALTER TABLE cells ADD number_of_spots_Qusar INT"
    c.execute(querystring)
    
    querystring = "ALTER TABLE cells ADD total_mRNA_NG INT"
    c.execute(querystring)
    
    querystring = "ALTER TABLE cells ADD total_mRNA_Qusar INT"
    c.execute(querystring)

    # the following could all be written into a for loop over tokens # TODO
    querystring = "UPDATE cells SET total_intensity_NG = \
        (SELECT SUM(intensity) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_1
    c.execute(querystring)

    querystring = "UPDATE cells SET total_intensity_Qusar = \
        (SELECT SUM(intensity) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_2
    c.execute(querystring)

    querystring = "UPDATE cells SET number_of_spots_NG = \
        (SELECT COUNT(intensity) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_1
    c.execute(querystring)

    querystring = "UPDATE cells SET number_of_spots_Qusar = \
        (SELECT COUNT(intensity) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_2
    c.execute(querystring)

    querystring = "UPDATE cells SET total_mRNA_NG = \
        (SELECT SUM(mRNA) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_1
    c.execute(querystring)

    querystring = "UPDATE cells SET total_mRNA_Qusar = \
        (SELECT SUM(mRNA) FROM spots JOIN locfiles ON locfiles.locfile=spots.locfile WHERE cells.cellID=spots.cellID AND locfiles.mode='%s')" % token_2
    c.execute(querystring)

    con.commit()
    print "done."
    print "---------------------------------------------------------------"
    
def enhance_locs():
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
        print querystring
        c.execute(querystring)
        querystring = "UPDATE locfiles SET total_mRNA = '%s' WHERE mode='%s' AND commonfileID = '%s'" % (str(item[2]), str(item[0]), str(item[1]))
        print querystring
        c.execute(querystring)

    con.commit()
    print "done."
    print "---------------------------------------------------------------"
    
def scatter_plot_two_modes():
    print "creating scatter plot..."
    c = con.cursor()
    c.execute('select total_mRNA_NG from cells')
    x = [x[0] if x[0] else 0 for x in c.fetchall()]
    #print x
    c.execute('select total_mRNA_Qusar from cells')
    y = [y[0] if y[0] else 0 for y in c.fetchall()]
    #print y
    plt.figure()

    # scatterplot code starts here
    plt.scatter(x, y, color='tomato')    
    # scatterplot code ends here
    plt.title('mRNA frequencies per cell: comparison')
    plt.xlabel(token_1)
    plt.ylabel(token_2)
    plt.savefig(join(locpath, "figure2.png"))
    plt.draw()
    print "done."
    print "---------------------------------------------------------------"

def plot_and_store_mRNA_frequency(token):
    print "creating mRNA histogram..."
    # FIXME: move to database mode
    mRNAfrequencies = cPickle.load(file("mRNAfrequencies.pkl"))
    print mRNAfrequencies

    c = con.cursor()
    querystring = 'select total_mRNA_%s from cells' % token
    c.execute(querystring)
    x = [x[0] if x[0] else 0 for x in c.fetchall()]
    
    
    #for tk in tokens:
    #    print tk, mRNAfrequencies[tk]
    bins = mRNAfrequencies[token].keys()
    if not bins:
        bins = [0]
    print "bins =", bins
    plotvals = mRNAfrequencies[token].values()
    if not plotvals:
        plotvals = [1]
    print "plotvals =", plotvals
    #old: plotvals = [elem[0] for elem in mRNAfrequencies[token].values()]
    totalmRNAs = sum(plotvals)
    with open(join(locpath, mRNAfrequenciesfile), 'w') as f:
        print "writing to", join(locpath, mRNAfrequenciesfile+token+".txt")
        f.write("\t".join(["number_of_mRNAs", "absolute_frequency", "relative_frequency_(percent)"]))
        f.write("\n")
        for i, val in enumerate(plotvals):
            f.write("\t".join([str(i), str(val), str(100.0*val/totalmRNAs)]))
            f.write("\n")

    width = 0.75           # width of the bars
    plt.figure()
    p1 = plt.bar(bins, plotvals, width, color='b', align="center")
    #p1 = plt.hist(plotvals, normed=False, cumulative=False, histtype='bar', align='mid',
    #   orientation='vertical', rwidth=None, log=False, color='b')
    #p1 = plt.plot(bins, plotvals)

    plt.ylabel('Frequencies')
    plt.title('Frequency of mRNAs per cell ('+token+')')
    plt.xticks(range(max(bins)+2))
    plt.yticks(range(max(plotvals)+2))
    print "done."
    plt.draw()
    plt.savefig(join(locpath, "figure1"+token+".png"))
    #plt.show()

def draw_crosses():
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
        print "drawing into file", tif
        outtif = "out."+tif
        orig = Image.open(join(locpath, tif)) #.convert("RGB")
        points = [(x, y) for (x, y, filename) in cross_data if filename==tif]
        #print points
        for x, y in points:
            print "found spot at", x, y
            draw = ImageDraw.Draw(orig)
            draw_cross(x, y, draw)
        orig.save(join(outpath, outtif))

    print "done."
    print "---------------------------------------------------------------"
    
    
###################################################################################
# main program

if __name__ == '__main__':
    con = setup_db()
    create_tables(con)
    insert_cells()
    insert_locs()
    insert_spots()
    enhance_spots()
    enhance_cells()
    enhance_locs()
    #scatter_plot_two_modes()
    #plot_and_store_mRNA_frequency(token_1)
    #plot_and_store_mRNA_frequency(token_2)
    draw_crosses()
    #plt.show()
