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
from matplotlib import pyplot as PLT

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

input_folder = "D:/Data/Matthias Schade/workspace/inverse_mapper_related/"
#----------------------------------
#FUNCTIONS
#----------------------------------
def getUserFile(str_iniDir, strDialog):
    if not str_iniDir:
        str_iniDir = os.getcwd()
    master = Tkinter.Tk()
    master.withdraw() #hiding tkinter window
    file_path = tkFileDialog.askopenfilename(initialdir=str_iniDir, title=strDialog)
    master.quit()
    return file_path #str_Return

def readSAM(fnSAM):
#reads in the SAM file and returns the content split in two part: a header and a body 
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
    
    for row in csvBody:        
        #Append to the all-sequence list anyway
        allSeq.append(row[0]) #will contain "CY045771_posStart_posENd"
        
        if len(row)==10:    #only a sequence not found on host-genome lacks the TAGs (entries 11,12,13,14)
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

    return posList, negSeq, allSeq, maxNTLen

def getTagVal(myStr, searchChar):
    #returns a number as int from the last occurrence of 'searchChar' on
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
    return 10**i #temporary solution only

def calcQualityAndHist(posList, allSeq):
#TODO: low priority: as posList can get big, it would be great if we could work with posList as a pointer
#calculates a quality factor for each sequence as well as a mismatch-histogram
#INPUT: posList; 14-item list of values as returned from inverse_mapper output, alphanumerically sorted by first column (=virus-sequence name)
#OUTPUT: extended list by 2 items: quality and a n-values long "histogram"

    worstQ = 0
    qGramLen = len(posList[0][9]) #get length of sequence 
    
    #TODO: convert allSeq in a dictionary called 'allSeqDict' here or in the next lines
    #    'allSeqDict' shall have for entries: as 'name' the item from 'allSeq' and as val a tuple containing (quality, n-tuple-histogram, sequence)
    allSeqDict = dict(allSeq) #ERROR
    
    #asuming: posList is alphanumerically sorted by first column (=virus-sequence name)
    for row in posList:
        hist=[0]*qGramLen
        
        #Calculate Sequence Quality and CIGAR-dependent histogram
        if row[2]=="*": #means virus-sequence had not been found on host-genome
            #TODO: high priority make sure that every posList-entry has 17-fields [0-16] by now (as some come with only 10, most with 14/15)
            #posList[15]=0 # best quality for a sequence non-existant on host-genome
            deltaQ = 0
            deltaHist = [0]*qGramLen #TODO: soll ein Vektor der Länge qGramLen darstellen, gefüllt mit Werten 0
        else:
            deltaQ = getQFactor(row[11])
            deltaHist = myCIGARConverter(row[5])
        
        #TODO: low priorit: update posList with q-value, such that each entry has its own q-value
        #posList(row[0])[15]=q #ERROR: so nicht lauffähig
        
        #update and summarize r
        allSeqDict(row[0])[0]=allSeqDict(row[0])[0]+deltaQ
        allSeqDict(row[0])[1]=allSeqDict(row[0])[1]+deltaHist #TODO: high priority: einfache Vektoraddition?????  [1,2,3]+[0,0,4]=[1,2,7]
        if not allSeqDict(row[0])[2]: #if there is not yet a sequence at [2], then write it now
            allSeqDict(row[0])[2]=row[9]
            
        #TODO: get worst(=highest) qualtiy-factor in the list (for later visualization)
        if worstQ<allSeqDict(row[0])[0]:
            worstQ=allSeqDict(row[0])[0]    
        #TODO: normalize the tuple in r[1] by the
        
            
        
    return allSeqDict, posList, worstQ #TODO: once 'posList' is a pointer, it has not to be passed back



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

def visualizeQ(allSeqDict,maxNTLen):
#For each unique
    #error check
    if not type(allSeqDict) is dict:
        print " visualizeQ: Input not of type dict"
        return
    
    #TODO: from the name list of allSeqDict get all unique keys
    #TODO: from s get all chars left of the first occurence of "_" (Background: s="CY045771_10_30" with 'CY045771' representing the gen of origin) 
    uInGen = set([s for s in allSeqDict.keys()]) #probably causes an error at this stage
    
    
    #User-feedback
    print "\nSTARTING: visualization"
    
    #get screen width and height
    root = Tkinter.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    #for subplots: calculate number of required rows
    plot_cols = 2
    l = len(uInGen)
    plot_rows = int(ceil(l/plot_cols)) #int(math.ceil(l/plot_cols))
    
    #organize data into subsets and get (x/y)
    #mySubsets=[] #lTODO: let mySubsets be a dictionary with keys from uInGen and values x/y (as to be calculated here)
    #for u in uInGen:
        #TODO: this: x= [convert int value in between "_" of allSeqDict.keys() with allSeqDict.keys()==u]
        #TODO: this: y=[get correspondent q value for each x] #background: allSeqDict.values() contains a three-tuple (q, n-tuple histogram, sequence)
        #TODO: mySubsets[u].values=[x,y] #fill [x,y] into the dict under the corresponding key
    
    #Create Canvas
    fig = PLT.figure(figsize=(14, 14)) #creates a new canvas with width, height in inches
    str_title = "bla, bla, bla"
    fig.suptitle(str_title)
    
    #Plot data in Subplots in canvas 'fig'
    #for m in mySubsets:
        #TODO: Plot
        #xLim=[0,maxNTLen]
    
    #save plot in input_folder
    #TODO: low priority
    #strSaveFig = join(input_folder, 'seq_q_img.png')
    #PLT.savefig(strSaveFig)
    #print " saving plot in ", strSaveFig
    
    #User Feedback
    print " DONE: visualization\n"
    
    
    return mySubsets

#-----------------------------------
# MAIN-BODY of CODE
#-----------------------------------
if __name__=='__main__':
    
    #startTime = time.clock()
    
    #fnSAM="D:/Data/Matthias Schade/workspace/inverse_mapper_related/allAPR8_Canis_53top_w16d2f5__001_mini.sam" 
    fnSAM="D:/Data/Matthias Schade/workspace/inverse_mapper_related/allAPR8_Canis_53top_w16d2f5__001_nano.sam"
    fnSAM = getUserFile(input_folder, "Select SAM file from inverse_mapper")
    
    #read in SAM-File
    csvBody, csvHeader = readSAM(fnSAM)
    
    #Filter and Split Sequences
    posList, negSeq, allSeq,maxNTLen = filterXDXC(csvBody, iXCMin,bXDFilter) ########allSeq = getUniqueSequences(csvBody)
    
    #Calculate sequence quality and mismatch histogram for each sequence
    #allSeqDict, posList,worstQ = calcQualityAndHist(posList, M)

    #TODO: low priority: #extracting paramerters used to call inverse_mapper (background: this is nice to have in the title when plotting the data
    #[strHost, strVir, w, d, f, ... options] = extractCallParameters(csvHeader) 
    
    #visualize sequence quality
    #TODO: low priority
    #mySubsets = visualizeQ(allSeqDict,maxNTLen)
    
    #TODO: save Data probably both in human readable form and as a pickle
    #posList
    #allSeqDict
    #mySubsets
    
    
    

    