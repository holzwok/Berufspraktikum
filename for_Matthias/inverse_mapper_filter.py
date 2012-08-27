'''
Created on 14.08.2012

@author: mschade
'''
#----------------------------------
#LIBRARIES
#----------------------------------
import time
import Tkinter
import tkFileDialog
import os
from os.path import join
import csv
import operator
from math import ceil #import math
from matplotlib import pyplot as plt
import datetime

#----------------------------------
#PARAMETERS
#----------------------------------
#minimum INT of mismatches in inner middle of virus-target sequence allowed to still be considered appropriate (everything lower will be filtered into the negative List)
#set negative to deactivate this filter: example: xcMin=-1
iXCMin = 1   #INT

#Apply XD-Tag as criterium for filtering sequences
#    if FALSE: the XD-status is ignored
#    if TRUE: a XD-status=1 automatically puts sequence on negative list for unsuitable virus-sequences.
#    normal: bXDFilter = FALSE
bXDFilter = False

#Create Subplots: if true, subplots are created for every file processed
bSubPlots = True
#Create plots: if true, full page plots are created for every gene per file processed
bPlots = True

#input_folder = r"E:\Daten\MatthiasSchade\workspace\imap"
input_folder = r"D:\32bit"
#input_folder = r"\\Ts412-molbp\shared\Matthias Schade\VirusProbeDesign\Output - inverse_mapper\default border_frac"

#inverse_mapper options
#this script call decifer the calling string used to call inverse_mapper
#attention: only supports the short versions "-h" instead of "--help"
invMapOptDic = {"-h": -1, "--version": -1, "-q": -1, "-v": -1, "-vv": -1, "-H":-1, "-t": -1, "-o": -1, "-w": -1, "-d":-1, "-f": -1, "-m": -1, "--border-frac": -1}

#NOT REQUIRED
SeqDict = {"huhu_15_22":[13,[2,5,6,7,8,9],"asdfasdf"],"huhu_17_29":[26,[2,5,6,7,8,9],"asdfasdf"],"harhar_2_9":[2,[2,5,6,7,8,9],"asdfasdf"],"huhu_15_22":[13,[2,5,6,7,8,9],"asdfasdf"]}

#----------------------------------
#FUNCTIONS
#----------------------------------
def getUserFile(str_iniDir, strDialog):
    #requests use to specifiy files for processing
    #INPUT: str_iniDir, STR, initial path to be offered to user
    #        strDialog, STR, headline-title of dialog for user 
    #OUTPUT: a list of filenames+path
    if not str_iniDir:
        str_iniDir = os.getcwd()
    master = Tkinter.Tk()
    master.withdraw() #hiding tkinter window
    file_path = tkFileDialog.askopenfilename(initialdir=str_iniDir, title=strDialog, multiple=True)
    master.quit()
    myPaths = file_path.split(" ") #TODO: convert this output into prober LIST such that even blanks can be used in the input file!!!
    #print myPaths
    return myPaths #str_Return

def readSAM(fnSAM):
#reads in the SAM file and returns the content split in two part: a header and a body

    print "\treadSAM: starting" 
    mySAMobj = open(fnSAM,"r")
    csv_read = csv.reader(mySAMobj,dialect=csv.excel_tab) #delimiter='\t'
    
    #TODO: an dieser Stelle sollte alphanumerisch nach der ersten Spalte sortiert werden
    
    csvBody=[]
    csvHeader=[]
    for row in csv_read:
        if row[0][0]!="@":
            csvBody.append(row)
            #print row
        else:
            csvHeader.append(row)
    #print "\t\t ... finished"
    return csvBody, csvHeader

def filterXDXC(csvBody, iXCMin, bXDFilter):
#filters TAG XD and XC (XD: read enabled'0' or not'1'; XC: # of errors in the two center quaters of a read)
#TODO: necessary???? and extends the [0-14]-fields of csvBody by two more empty fields for later usage
#    xcMin: INT, value for # of errors in middle section which is still considered appropriate (everthing below ends up in the negList)
#    bXD: boolean, if TRUE only XD==0 passes onto posList; if FALSE this tag is ignored
#    NOTE: assumes an alphanumerically sorted first column!!!
#OUTPUT: posList: same as csvBody or the SAM-File
#        negSeq: a simple column-set containing only the first and unique(!) column of the SAM-File: "CY045771_posStart_posENd" (NOTE: half open connotation) of virus-sequences not suitable
#        allSeq: a simple column-set containing only the first and unique(!) column of the SAM-File: "CY045771_posStart_posENd" (NOTE: half open connotation) of all virus sequences

    allSeq=[]
    tmpPosList=[] #temporary white list: to include appropriate virus-sequences not/hardly on host
    negSeq=[] #final black list: to include non-appropriate virus-sequences found en masse on host
    
    print "\tFilterXDXC: starting with # of entries in input file:", len(csvBody), "(100%)"

    
    for row in csvBody:        
        #Append to the all-sequence list anyway
        allSeq.append(row[0]) #will contain "CY045771_posStart_posENd"
        
        if len(row)<14:    #only a sequence not found on host-genome lacks the TAGs (entries 11,12,13,14)
            #TODO: extend this [0-10]-element row by six more but empty entries, such that adressing row[16] thereafter would not return an error
            tmpPosList.append(row) #add
        else:
            #consider XD-TAG or not
            if bXDFilter:
                bXDstatus = getTagVal(row[14], ":")==0
            else:
                bXDstatus = True
            #get status of XC-TAG (=#errors in two center quatiles):
            bXCstatus = getTagVal(row[13], ":")>=iXCMin
            #Take action
            if bXDstatus and bXCstatus: #if getTagVal(row[14], ":")==0 and getTagVal(row[13], ":")>=iXCMin:
                tmpPosList.append(row) #add
            else:
                negSeq.append(row[0])
        
    #clean down to unique entries:
    if allSeq:
        allSeq = set(allSeq)
    if negSeq:
        negSeq = set(negSeq)
    
    
    #purge tmpPosList by sequences which had at least one member considered unsuitable
    #TODO: make for-loop pythonian
    posList=[]
    for me in tmpPosList:
        if not me[0] in negSeq:
            posList.append(me)
    
    #TODO: high priority: sort posList by sequence (which is the first column)    
    #something like: posList = sorted(posList, key=itemgetter(0), reverse=False)
    
    #TODO: get max length of virus/target genome
    #Background: row[0] contains structures as "CY045771_10_30" with the number in between '_' representing the sequence starting position 
    maxNTLen=2500
    
    #User-Feedback
    print "\tFilterXDXC: finishing with # of valid entries under the filter applied:", len(posList), " (", 100*len(posList)/len(csvBody),"%)"
    
    return posList, negSeq, allSeq, maxNTLen

def getTagVal(myStr, searchChar):
    #returns a number as int from the last occurrence of 'searchChar' onwards
    #example: getTagVal(NM:i:1, ":") returns 1 as integer
    # if no occurrence is found, a 0 is returned
    
    i=myStr.rindex(searchChar)
    if i<len(myStr):
        iOut = int(myStr[i+1:])
    else:
        iOut=0
    return iOut

def getUniqueSequences(csvBody): #DEPRICATED!!!!!!!!!!!!!!!!!!!1
#DEPRICATED!!!!!!!!!!!!!!!!!!!1
# extracts the virus-sequence names and returns unique entries only
# example: CY045767_848_868 // name_startPos_endPos
    r=[]
    #TODO: write the for-loop pythonian-like
    for row in csvBody:
        print row[0]
        r.append[row[0]]
    s = list(set(r))
    return s

def getQFactor(i):
    #weighting the edit distance
    #TODO: make nicer and weight by predictions of hybridizations by NUPACK
    return 10**(-i) #temporary solution only

def calcQualityAndHist(posList,maxEDistSearchedFor):
#TODO: low priority: as posList can get big, it would be great if we could work with posList as a pointer
#calculates a quality factor for each sequence as well as a mismatch-histogram
#INPUT: posList; 14-item list of values as returned from inverse_mapper output, alphanumerically sorted by first column (=virus-sequence name)
#    maxEDistSearchedFor, INT, value for option "filtration-distance" for inverse_mapper as extracted from the header in SAM-File
#OUTPUT: extended list by 2 items: quality and a n-values long "histogram"
#        qLim, LIST, containing the CUMMULATIVely seen best-q-value (=smallest), and the worst-q-value (=largest)

    print "\tcalcQualityAndHist: starting"
    allSeqDict = dict()
    allSeqKeys = set([pos[0] for pos in posList])
    qLim = [9999,-9999] #[best, worst]; instantiate with terrible values for best-quality factor and worst qualitiy factor
    
    #what does this do?
    for key in allSeqKeys:
        
        allSeqDict[key] = [0,[0],"a"] #TODO: inititiate second value and third value correctly
    
    #assign a q-factor to each key-word
    for pos in posList:
        if len(pos)>11: #len(pos)>11 means this sequence has been found by inverse_mapper
            allSeqDict[pos[0]][0] += getQFactor(int(getTagVal(pos[11], ":")))
        else: #len(pos)<=11 means this sequence has not been found by inverse_mapper thus the q-factor is assumed to be one step worse than the "filtration-distance" (equals the maximum edit distance looked for)
            allSeqDict[pos[0]][0] += getQFactor(int(maxEDistSearchedFor+1)) #NOTE: as allSeqDict should be initiated with '0', this should set the mini
        #Tracking the worst = highest Q-value for later usage
        if allSeqDict[pos[0]][0]>qLim[1]:
            qLim[1] = allSeqDict[pos[0]][0] #update worstQ
        if allSeqDict[pos[0]][0]<qLim[0]:
            qLim[0] = allSeqDict[pos[0]][0] #update worstQ
    
        #TODO: here expand CIGAR-Notation, calculate HISTOGRAM Value and add to allSeqDict value[1]
            #allSeqDict[pos[0]][1] += myCIGARConverter(row[5])
            
        #TODO: here, add sequence length to allSeqDICT if its not already there
            #if not allSeqDict[pos[0]][2]: 
            #    allSeqDict[pos[0]][1] = pos[9] #(=sequence)
            
    #TODO: normalize histograms
    
    return allSeqDict, qLim


def myCIGARConverter(myC, M):
#converts a CIGAR-notation in a weighted histogram
    
    #idxList = [search via regex for "=", "I", "D","X" and pass back index positions of those]
    #splitList = split myC at the idxList-positions such that a list of entries like this is obtained: [["13="], ["4I"], [1D], ...]
    
    #i=0 #position-counter
    #for x in splitList:
    #    new = lookupCigarM(x(1))
    #    hist(i,i+x(0))=hist(i,i+x(0))+ new # NOTE: simple vector addition; NOT: extension
    #    i=i+len(new)
    
    
    return []
    
def lookupCigarM(strIn):
#TODO: make nicer, fill with Gewichtung
#returns a line-vector of i elements all of out-value
#INPUT: strIN: STR consisting of type '#Char' with "#" of indefinite length but of type INT
#OUTPUT: vector
    
    #i, myChar = splitInValueAndSingleChar(strIn)
    #if myChar=="=": #match
    #    out=0
    #if myChar=="D": #deletion
    #    out=1 #temp
    #if myChar=="I": #insert
    #    out=1 #temp
    #if myChar=="D": #mismatch
    #    out=1 #temp
    
    #return [out]*i
    return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def myStripLPlus(string, char,strOption):
    #returns left side of a string up to the first occurence of 'char'
    #INPUT: string, STR, to be searched for existance of 'char'
    #        char, STR
    #        strOption, STR, specifies what to do if 'char' is not found in 'string'
    #                Note: if strOption=="all": returns entire string if 'char' is not found
    #                      if strOption<>"all": returns "" if 'char' is not found
    
    i = string.find(char)
    #print "\t\t laueft: ...."
    if i>0:
        #print "\t\t\t erster"
        return string[0:i]
    #now what happens if 'char' was not found
    elif (i<=0 and strOption!="all"):
        #print "\t\t\t zweiter"
        return ""
    elif (i<=0 and strOption=="all"):
        #print "\t\t\t dritter"
        return string
    
def myStripL(string, char):
    #returns left side of a string up to the first occurence of 'char'
    i = string.find(char)
    if i>0:
        return string[0:i]
    else:
        return ""

def getMiddle(string, char):
    #returns middle part of string between the leftmost and the rightmost occurence of 'char'
    l = string.find(char)
    r = string.rfind(char)
    if (l<>r and r>0 and l>0):
        return string[l+1:r]
    else:
        return ""

def convertPairsToFullList(vals ,iGeneLen, worstQValue):
    #expands a list of x/y-points "[[4,2], [6,8], ...]" into to lists: x=[1,2,3,4...] and y=[worstQValue, worstQValue, 234, 233, ...]
    
    #if iGeneLen is negative or not specified, the maxiumum nucleotide strand length needs to be determined
    if iGeneLen<1:
        for (i, j) in vals:
            if i>iGeneLen:
                iGeneLen=i+1
                
    x = range(1,iGeneLen+2)        
    y=[worstQValue for i in x]
    
    for (i, j) in vals:
        #print "iGeneLen, len(x), len(y): ", iGeneLen, len(x), len(y)
        #print "i, j, y", i, j #, y
        y[i]=j
    #color-Value
    iClr = [(1-(i*10)) for i in y]
    return x,y, iClr


def myQSubPlot(oriArgsIn, iGeneLen, qLim, xLim, yLim, geneDict, plot_cols, plot_rows, myPath):
    #creates an subplot-overview of of nucleotide-sequence-starting position vs q-factor in form of a subplot
    #INPUT:
    #    oriArgsIn: STR
    #    iGeneLen: INT, defines how much of the strand is shown; when negative value is specified an automatic value is determined

    #Create Canvas
    fig = plt.figure(figsize=(14, 14)) #creates a new canvas with width, height in inches
    str_title = "Quality factor for call: ", oriArgsIn
    fig.suptitle(str_title)
    ax = []
    c = 0
    for g in geneDict: #format of geneDict: [[startingPos, q-Factor], [startingPos, q-Factor], ...]
        c = c + 1
        x=[] #empty
        y=[] #empty
        #get xy-points from dict
        vals = geneDict[g]
        #expand xy-points into two arrays
        x, y, iClr = convertPairsToFullList(vals, iGeneLen, qLim[1])
        #create/choose subplot:
        #print "plot_cols, plot_rows, c: ", plot_cols, plot_rows, c
        ax.append(fig.add_subplot(plot_cols, plot_rows, c)) #TODO: c=lookUp index position of g in sorted.geneDict.keys()
        #plot data
        #ax[len(ax) - 1].scatter(x, y, marker='+') #edgecolors='none', alpha=0.2)
        ax[len(ax) - 1].scatter(x, y, s=3, facecolor='0.5', lw=0) #This sets the markersize to 1 (s=1), the facecolor to gray (facecolor='0.5'), and the linewidth to 0 (lw=0)
        #ax[len(ax)-1].plot( x, y, ':gs', alpha=0.2)
        #set x,y limits and subtitles
        ax[len(ax) - 1].set_title(g)
        ax[len(ax) - 1].set_yscale('log')
        ax[len(ax) - 1].set_xlim(xLim)
        #ax[len(ax) - 1].set_ylim(yLim)
        
        
        
    #plt.show()
    #save plot in input_folder #fnSAM
    strSaveFig = join(myPath, 'subPlot_img.png')
    print "\t\t saving subplot in ", strSaveFig
    plt.savefig(strSaveFig)
    

def myQPlot(oriArgsIn, iGeneLen, qLim, xLim, yLim, geneDict, plot_cols, plot_rows,myPath):
    #creates a one page graph of nucleotide-sequence-starting position vs q-factor (the smaller q, the better)
    #INPUT:
    #    oriArgsIn: STR
    #    iGeneLen: INT, defines how much of the strand is shown; when negative value is specified an automatic value is determined
    #    qLim: LST [best (=lowest), worst(=highest) cummulative q value for a sequenc
    
    #Create Canvas
    #fig = plt.figure(figsize=(14, 14)) #creates a new canvas with width, height in inches
    #str_title = "Quality factor for call: ", oriArgsIn
    #fig.suptitle(str_title)
    #ax = []
    c = 0
    for g in geneDict: #format of geneDict: [[startingPos, q-Factor], [startingPos, q-Factor], ...]
        c = c + 1
        x=[] #empty
        y=[] #empty
        #get xy-points from dict
        vals = geneDict[g] #val contains
        #expand xy-points into two arrays
        x, y, iClr = convertPairsToFullList(vals, iGeneLen, qLim[1])
        #print "len(x), len(y): ", len(x), len(y)
        
        #plot data
        plt.figure()
        ax = plt.subplot(1,1,1)
        #ax.scatter(x, y, marker='+') #edgecolors='none', alpha=0.2)
        #ax.scatter(x, y, c=y) #, s=3, vmin=0, vmax=0.1) #edgecolors='none', alpha=0.2)
        
        #ax.scatter(x, y, c=iClr)
        ax.scatter(x, y, c=y, vmin=0.0, vmax=0.1) #, s=5)
        #plt.colorbar(sc)

        #sc = plt.scatter(xy, xy, c=z, vmin=0, vmax=20, s=35, cmap=cm)
        #plt.colorbar(sc)


        #ax.scatter(x, y, s=3, facecolor='0.5', lw=0) #This sets the markersize to 1 (s=1), the facecolor to gray (facecolor='0.5'), and the linewidth to 0 (lw=0)
        #ax.colorbar()
        #set x,y limits and subtitles
        ax.set_title(g)
        ax.set_xlabel('Nucleotide Position')
        ax.set_ylabel('Q-Factor (the smaller the better)')
        ax.set_yscale('log')
        ax.set_xlim([0, len(x)+1])
        #ax.set_ylim(yLim)
        

        #plt.show()
        #save plot in input_folder #fnSAM
        strSaveFig = join(myPath, str(g)+str('.png'))
        plt.savefig(strSaveFig)
        print "\t\t saving single plot in ", strSaveFig
        plt.clf()

    
def visualizeQ(allSeqDict,posSeperator, oriArgsIn, iGeneLen, qLim, myPath, myFile, bSubPlots, bPlots):
#Visualization of quality value for all sequences.
#INPUT: allSeqDict: DICT, key=originname_start_end; value=[q-value, [mismatch-histogram], sequence]
#        posSeperator: CHAR, used to separate name from positioning in key of dict: if the key was "charles_22_30", then the separator is "_"
#        oriArgsIn: STR, contains the call used to make up data from the original target and host genomes; contains a lot of parameters
#            Note: a more comprehensive dict of information is stored in invMapDic with key=option-name; value=option-value
#        iGeneLen: maximum lenght of a gene (=max length displayed)
#        qLim: LST,  best (=smallest) and worst (=largest) qualtity-factors in the cummulated allSeqDict
#        myPath: STR, path to the subfolder (if myPath='C:\test\' then myFile is located at 'C:\myFile'
#        myFile: STR, original name of the input file
#        bSubPlots: BOOL: defines if the overview subplots are created visualizing the q-factor
#        bPlots: BOOL: defines if per gene and file a plot is created visualizing the q-factor 
#OUTPUT:
#
#seg_length={"seg1": 2300, "seg2":2300, "seg3":2193, "seg4":1723, "seg5":1501, "seg6" :1373, "seg7":986, "seg8":848 } #reference segment length
    
    print "\tvisualizeQ: starting"
    #error check
    if not type(allSeqDict) is dict:
        print " visualizeQ: Input not of type dict"
        return
    
    #TODO: from the name list of allSeqDict get all unique keys
    #TODO: from s get all chars left of the first occurence of "_" (Background: s="CY045771_10_30" with 'CY045771' representing the gen of origin) 
    #uInGen = set([s for s in allSeqDict.keys()]) #probably causes an error at this stage
    uInGen = set([myStripL(s,posSeperator) for s in allSeqDict.keys()]) #probably causes an error at this stage
    
    #Get maxima for q and histogram-length
    qmax=0
    qmin=1000
    hmax=0
    for q,h,s in allSeqDict.values():
        if q>qmax:   #actually, qLim contains already the needed information; thus, this line could be skipped
            qmax = q #actually, qLim contains already the needed information; thus, this line could be skipped
        if q<qmin:   #actually, qLim contains already the needed information; thus, this line could be skipped
            qmin = q #actually, qLim contains already the needed information; thus, this line could be skipped
        if len(h)>hmax:
            hmax=len(h)
    
    #split allSeqDict values in groups according to unique origin-gens
    geneDict = dict() # format: key = origin-genome; value = [starting Position, quality factor]
    for k in allSeqDict:
        k_set = myStripL(k,posSeperator)
        iPos = int(getMiddle(k, posSeperator))
        geneDict.setdefault(k_set, []).append([iPos,allSeqDict[k][0]])
    
    
    #get screen width and height
    #root = Tkinter.Tk()
    #screen_width = root.winfo_screenwidth()
    #screen_height = root.winfo_screenheight()
    
    #for subplots: calculate number of required rows
    plot_rows = 2
    l = len(uInGen)
    plot_cols = int(l/plot_rows)+1 #plot_rows = int(ceil(l/plot_cols)) #int(math.ceil(l/plot_cols))
    
    #set limits
    xLim = [0, iGeneLen]
    yLim = [qmin, qmax] #actually, here, yLim and qLim ar identical
    
    #create one canvas with many subplots
    if bSubPlots:
        myQSubPlot(oriArgsIn, iGeneLen, qLim, xLim, yLim, geneDict, plot_cols, plot_rows,myPath)
    #create several images with one chart each    
    if bPlots:
        myQPlot(oriArgsIn, -1, qLim, xLim, yLim, geneDict, plot_cols, plot_rows, myPath)
    
    #if iHistogram:
    #    myPlotHistogram() #TODO
    
    #histogram
    #http://matplotlib.sourceforge.net/users/pyplot_tutorial.html
    

    
    #User-feedback
    #print "\t\t ... finished"
    
    return uInGen, qmax, hmax, geneDict

def extractHeaderData(csvHeader,invMapOptDic):
    #returns the originally used calling line conatining all parameters
    #INPUT: a csvHeader
    #sample output: "inverse_mapper -H Canis_53top.fa -t allAPR8.fa -o allAPR8_Canis_53top_w16d2f5__001.sam -w 16 -d 2 -f 5"
    # returns [none] if no suitable header is found
    strCall = ""
    for row in csvHeader:
        for el in row:
            if el.startswith("CL:"):
                strCall = el[3:]
                return strCall, extractInverseMapperOptions(strCall,invMapOptDic)
            
def extractInverseMapperOptions(strCall,invMapOptDic):
    #breaks down input string and returns options used for calling inverse_mapper
    #INPUT: strCall, STR, example: CL:"inverse_mapper -H Canis_53top.fa -t allAPR8.fa -o allAPR8_Canis_53top_w16d2f4__001.sam -w 16 -d 2 -f 4"
    #OUTPUT: invMapOptDict, DICT, key=option ("H" or "f", etc); value = value of option
    
    for o in invMapOptDic:
        #print "invMapOptDic[o] :", invMapOptDic[o]
        i = strCall.find(str(o))
        #print "i found: ", i
        if i>0:
            i=i+len(o)+1 #note: this consideres the existance of a blank after an option ("-H ") before the corresponding value
            #print "vorher: ", invMapOptDic[o], "bei Extaktion von ", strCall[i:]
            invMapOptDic[o]=myStripLPlus(strCall[i:], " ","all") #Note: option "all" allows for full string returned if " " is not found (usefull for end of line!!!)
            #print "\tnachher: ", invMapOptDic[o]
    return invMapOptDic


def createSubFolder(fnSAM):
    #creates a name and a subfolder bases on path and input name
    #INPUT: str, expected format: "D:\folderA\...\folderZ\filename.ZZZ"
    #OUTPUT: STR, "D:\folderA\...\folderZ\filename___yyyy-mm-dd\"
    #    bNew, Bool, indicates if subfolder had to be created new
    #    strFile: STR, original file name
    
    bNew = False
    #current date
    now = datetime.datetime.now() #format: '2012-08-22 17:59:29.108000'
    #split fnSAM into folder-path and file-name
    strParent = os.path.dirname(fnSAM)
    strFile = os.path.basename(fnSAM)
    #print str(now)
    #suggest new subfolder
    strSub = strFile[:-4]+"___"+str(now)[:10]
    #print strSub
    strSubFolder = strParent+"/"+strSub
    #create new subfolder
    if not os.path.isdir(strSubFolder):
        os.makedirs(strSubFolder)
        bNew=True
    
    return strSubFolder, strFile, bNew
#-----------------------------------
# MAIN-BODY of CODE
#-----------------------------------
if __name__=='__main__':
    
    print "\n--------------------------------\nWelcome to inverse_mapper_filter\n--------------------------------\n"
    print "(Currently, as for input please use a file path and name lacking any blanks.)\n"
    allSeqDict = dict()
    
    #ask user for path to process
    #fnSAM="D:/Data/Matthias Schade/workspace/inverse_mapper_related/allAPR8_Canis_53top_w16d2f5__001_mini.sam" 
    #fnSAM = r"E:\Daten\MatthiasSchade\workspace\imap\allAPR8_Canis_53top_w16d2f5__001_nano.sam"
    #fnSAM=r"D:/32bit/allAPR8_Canis_53top_w16d2f5__001_mini.sam"
    #fnSAM=r"D:/32bit/allAPR8_Canis_53top_w16d2f4__001.sam"
    #fnSAM = r"D:\32bit\allAPR8_Canis_53top_w16d2f5__001_nano.txt"
    fnSAMList = getUserFile(input_folder, "Select SAM file from inverse_mapper (files with blanks in it not supported yet)")
    
    #TODO: interrupt here if fnSAMList is empty because the user clicked on "abort" in the open-file-dialogue
    
    for fnSAM in fnSAMList:
        
        print "Processing file: ", fnSAM
        #read in SAM-File
        csvBody, csvHeader = readSAM(fnSAM)
        
        #extract data from header and update invMapOptDic
        strCall,invMapOptDic = extractHeaderData(csvHeader,invMapOptDic)
        
        #Filter and Split Sequences
        posList, negSeq, allSeq, maxNTLen = filterXDXC(csvBody, iXCMin, bXDFilter) ########allSeq = getUniqueSequences(csvBody)
        
        #if nothing made it through the filter, stop here
        if csvBody and not posList:
            print "\t WARNING: No sequences made it through the XDXC-filter"
            raise SystemExit
        #create a subdirectory:
        myPath, myFile, bFolderIsNew = createSubFolder(fnSAM)
        
    
        #Calculate sequence quality and mismatch histogram for each sequence
        allSeqDict, qLim = calcQualityAndHist(posList,int(invMapOptDic["-f"]))
            
        #visualize sequence quality
        if not allSeqDict:
            allSeqDict=SeqDict
        uInGen, qmax, hmax, geneDict = visualizeQ(allSeqDict,"_", strCall,maxNTLen, qLim, myPath, myFile, bSubPlots, bPlots)
            
        #TODO: save Data probably both in human readable form and as a pickle
        #posList
        #allSeqDict
        #mySubsets
        print "\tFile Done: "+str(datetime.datetime.now())[0:19] #format: '2012-08-22 17:59:29.108000')
    #end of for
    
    #User Feedback
    print "\nAll Jobs Finished: "+str(datetime.datetime.now())[0:19] #format: '2012-08-22 17:59:29.108000')

    