#---------------------------------------------------------------------------------------------#
# Purpose:
#    to generate two lists:
#        (i) a list n-grams of a pattern file of type ".fa" (seqmentation into possible probes to be matched against a target genome)
#        (ii)a list of matches between the pattern and a genome file (verification for hits)
#
#Authors: Martin Seeger, Matthias Schade
#---------------------------------------------------------------------------------------------#

#Import Classes
import subprocess
from dircache import listdir
from os.path import join
import os
import datetime
import shelve #dumping variables
#from non_match_finder import create_qgramIndex_list,purgeByGenome
from non_match_finder import purgeByGenome
#import sys
#import glob
import operator
import time

#Version Number of this script
v=0.82

#range of length of probe to be tested for design
#q_min = 20 #minimum length to be tested
#q_max = 20 #maximum length to be tested
#minimum number of mismatches (between pattern (=virus) and host genome) required 
#in order to reach at a probe which is sufficiently unlikely to interact with host genome
#  note: mm has too be higher than 0, otherwise this entire program makes no sense 
#  example: if mm=3: then all alignments (between pattern and host) which only have 2, 1 or even 0 
#          mismatches will be rejected
#mm=3

#grouped together in tuples: pairs of probe length and mm to be tested:
# [length of probe to be tested for design, highest number of mismatches with genome to be excluded]
# example: myParam = [[20,3],[20,4]] # this results in two runs: one with length 20 and mm=3; and the other with length 20nt and mm=4  
#myParam = [[20,3],[20,4],[21,3]]
#myParam = [[20,3],[20,4],[20,5], [21,3], [21,4],[21,5], [22,5],[22,6],[23,4],[23,5],[23,6], [24,4],[24,5],[24,6], [25,6],[25,7], [27,7],[27,8],[27,9], [30,8],[30,9],[30,10], [32,9],[32,10],[32,11], [34,11],[34,12],[34,13], [42,14],[42,15],[42,16], [50,17],[50,18],[50,19], [26,6],[26,7],[26,8], [28,7],[28,8],[28,9], [29,8],[29,9],[29,10]]
myParam = [[24,4],[24,5],[24,6], [25,6],[25,7], [27,7],[27,8],[27,9], [30,8],[30,9],[30,10], [32,9],[32,10],[32,11], [34,11],[34,12],[34,13], [42,14],[42,15],[42,16], [50,17],[50,18],[50,19], [26,6],[26,7],[26,8], [28,7],[28,8],[28,9], [29,8],[29,9],[29,10]]


#recognition rate of matches in percent (100 = 100%)
rr=100 #keep at 100!!!

#position of starting nucleotide included into query
# note: negative values mean: "option disregarded = all positions evaluated"
start = -1 #230

#position of last nucleotide included into query
# note: negative values mean: "option disregarded = all positions evaluated"
end = -1 #260

#recognition rate for razerS in the target genome
rr = 100

# Consider insertions, deletions and mismatches as errors. If FALSE, only mismatches are recognized.
bInDelAsError = True

#Produce an error distribution file containing the relative frequencies of
#  mismatches for each read position. If the "--indels" option is given, the
#  relative frequencies of insertions and deletions are also recorded.
# if strErrFile is empty, no such error distribution file is created
#strErrFile ="errDistrbFile.txt"
strErrFile =""

#Input folders:
#    -from the pattern (e.g. virus) a list of n-grams is created to be matched against the genome (e.g. host)
#    -the genome is used for targeting each of the n-grams against
# attention: switch "\" by "/" due to OS
folder_pattern = "D:/Data/Matthias Schade/workspace/MyTestProject/mynewPythonPackage/pattern" #own pc
folder_genome = "D:/Data/Matthias Schade/workspace/MyTestProject/mynewPythonPackage/genome" #own pc
#folder_pattern = "D:/Data/Matthias Schade/workspace/VirusProbeDesign/pattern" #pc at micro
#folder_genome = "D:/Data/Matthias Schade/workspace/VirusProbeDesign/genome" #pc at micro
#folder_pattern = "E:/Daten/MatthiasSchade/workspace/VirusProbeDesign/pattern" #pc40
#folder_genome = "E:/Daten/MatthiasSchade/workspace/VirusProbeDesign/genome" #pc40

#Name of file into which all n-grams are written (Attention: can possibly be overwritten!!!)
qgramfile = "qgrams.fa" #TODO: generate one qgramfile per pattern generically/automatically without overwriting

#Fasta-name of n-gram-sequences in 'qgramfile' (e.g.: "read")
#qgram_entryname = "read_"

#Shelve file name for saving all variables in output-folder
shlv_name = "shelved.out" #taken from: http://stackoverflow.com/questions/2960864/how-can-i-save-all-the-variables-in-the-current-python-session
strReadMe = "ReadMe_ParametersUsed.txt"

#user-feedback by razerS:
# modes: no screen-feedback: razerSVerboseMode = ""
# modes: some screen-feedback: razerSVerboseMode = "-v"
# modes: very talkative: razerSVerboseMode = "-vv"
razerSVerboseMode = ""

#output-format of razerS
#    "of0": usual default value for razerS
#    "of1": enhanced FASTA output-format for razerS; example line: ">57918952,57918932[id=seg8(00016:00036)_0,fragId=16,contigId=Un,errors=3,percId=85,ambiguity=2]"
razerSOutputFormat ="of1"

#Modus: What sequences are to be returned?
# - if you -letztendlich- need those pattern sequences which were NOT found in the genome, chose: TRUE
# - if you -letztendlich- need those pattern sequences which were found in the genome, chose: FALSE (not tested)
# ATTENTION: this has direct results on 'non_match_finder' 
bNonMatchFinder=True

#Code-Execution Speed:
# pattern sequences to be compared against the target genome can be reduced after each razerS-call, such that
# only those pattern-sequences remain for the next run, which have not yet been found to exist in the target-genome
# this reduces unnecessary scanning
# ATTENTION: if this mode is activated, resulting "*.fa.result"-files will not contain all pattern-sequences found
#    for this genome any longer (thus being incomplete). This information is relevant only if you plan on working
#    with "*.fa.result"-files other than using 'non-match-finder'
bReduceSeqAtRuntime = False

#-----------------------------------------#
#-----------END OF PARAMETERS-------------#
#-----------------------------------------#


def ensure_dir(f):
    #if directory does not yet exists, it is created
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    return d

# function to create n-grams from the patternfile of length q starting at position 'start' until reaching 'end-q+1'
def create_qgram_list(q, start, end, folder_pattern,fName):
    fStr = fName[:-3] #filename
    patternfile = join(folder_pattern, fName)
    
    #print "asdf: ", fStr
    
    pattern = ""
    #read in the patternfile
    with open(patternfile, 'r') as f:
        for line in f:
            if not line.startswith(">"):
                pattern += line.strip()
    
    if (start>-1 & end>-1):
        #split the pattern into n-grams beginning from starting position
        qgramlist = [pattern[i:i + q] for i in range(start, end - q + 1)]
        #create a position list for each qgramlist: 'starting pos: ending pos' in sense as given in patternfile
        #posStrList = [str("%05d" %j)+":"+str("%05d" %(j+q)) for j in range(start, end - q + 1)] #formated output. E.g.: seg(00001:00013)
        posStrList = [str(fStr)+"("+str("%05d" %j)+":"+str("%05d" %(j+q))+")" for j in range(start, end - q + 1)] #formated output. E.g.: seg(00001:00013)
        #patternfile[:-3]   
    else:
        #split the pattern into n-grams disregarding positions
        qgramlist = [pattern[i:i + q] for i in range(0, len(pattern)-q+1)]
        #create a position list for each qgramlist: 'starting pos: ending pos' in sense as given in patternfile
        #posStrList = [str("%05d" %j)+":"+str("%05d" %(j+q)) for j in range(0, len(pattern)-q+1)] #formated output. E.g.: seg(00001:00013)
        posStrList = [str(fStr)+"("+str("%05d" %j)+":"+str("%05d" %(j+q))+")" for j in range(0, len(pattern)-q+1)] #formated output. E.g.: seg(00001:00013)

    return [qgramlist ,posStrList]


# function to create a fasta-file containing qgrams
#    -file to be created/overwritten: 'qgramfile'
#    -contend to be filled into file: 'qgramlist'
def create_qgram_file(qgramfile, qgramlist, posStrList,pattern_source):
    readcount = 0
    #open/create file as writable
    with open(qgramfile, 'w') as f:
    #with open(join(fileprefix,"_",qgramfile), 'w') as f:
        #str("_%03d_nt" %q)
        #create one fasta-entry by n-gram-entry
        for gram in qgramlist:
            #f.write(">" + pattern_source+"("+posStrList[readcount]+")") #old: only when posStrList = "0000:0020"
            f.write(">" +posStrList[readcount]) #new: only when posStrList = "seg2(0000:0020)"
            f.write("\n")
            f.write(gram)
            f.write("\n")
            readcount=readcount+1
            
def getDirFilesEndsWith(input_folder, strFix):
    #function returns a list of files from a folder
    # contains only files which end on suffix 'strFix'
    # list is sorted by file size
    filtered=[]
    filteredAndSorted = []
    
    #Check if path exists
    if os.path.exists(input_folder): 
        names = listdir(input_folder) #get all entries in a directory
        #apply suffix-filtering
        for x in names:
            if x.endswith(strFix):
                filtered.append(x)
        #return filtered
        
        #sort by file-size
        flist= filtered
        for i in range(len(flist)):
            #statinfo = os.stat(flist[i])
            statinfo = os.stat(join(input_folder,flist[i]))
            flist[i] = flist[i],statinfo.st_size,statinfo.st_ctime
        
        #sort by file size;
        flist.sort(key=operator.itemgetter(1))  #for sorting by 'creation date' use: #flist.sort(key=operator.itemgetter(2))
        
        #extract only the file-names
        for j in flist:
            filteredAndSorted.append(j[0])

    return filteredAndSorted



def getDirFilesStartsWith(input_folder, strFix):

    filtered=[]
    names = listdir(input_folder) #get all entries in a directory
    for x in names:
        if x.startswith(strFix):
            filtered.append(x)
                     
    return filtered
def createOutputFolder(mm, rr, q):
    #create a new output-folder to dump all related information
    now = datetime.datetime.now()
    out_rel_f = now.strftime("%Y-%m-%d_%H-%M") + str("_%02dnt" % q) + str("_%02dmm" % mm) + str("_%03drr" % rr) #out_rel_f= now.strftime("%Y-%m-%d_%H-%M")+"_"+str(q)+"nt"+"_"+str(mm)+"mm"+"_"+str(rr)+"rr"
    out_f = join(os.getcwd(), out_rel_f, "readme.txt") #out_f= join(os.getcwd(), now.strftime("%Y-%m-%d_%H-%M"),"readme.txt")
    output_folder = ensure_dir(out_f) #if directory does not yet exists, it is created
    return output_folder


#def createInputParamFile(strFolder, strFName, outFolder, patFiles, genFiles):
def createInputParamFile(strFolder, strFName, z, v, bNonMatchFinder, bReduceSeqAtRuntime, mm, rr, q, ident, razerSOutputFormat, patternfiles, genomefiles):
    #writes a user-readable readme file to the output folder
    # z is a spacer: e.g. z="# "
    myFile = join(strFolder, strFName)
    
    now = datetime.datetime.now()
    
    #open/create file as writable
    with open(myFile, 'w') as f:
        f.write(z+"PROBE-GENERATOR: Parameters used\n")
        f.write(z+"\n")
        f.write(z+"date: "+ str(now.strftime("%Y-%m-%d_%H-%M-%S"))+"\n")
        f.write(z+"probe_generator version: "+str(v)+"\n")
        f.write(z+"output format of razerS: "+str(razerSOutputFormat)+"\n")
        f.write(z+"Considering inserts and deletions: "+str(bInDelAsError)+"\n")
        f.write(z+"Writing error distribution file to: "+str(strErrFile)+"\n")
        f.write(z+"\n")
        f.write(z+"Code running in search-modus: bNonMatchFinder = : "+str(bNonMatchFinder)+"\n")
        f.write(z+"Code running in speed-modus: bReduceSeqAtRuntime = : "+str(bReduceSeqAtRuntime)+"\n")
        f.write(z+"\n")
        f.write(z+"\n")
        f.write(z+"Probe-length (qGrams): "+str(q)+"\n")
        #f.write("\n"+z)
        f.write(z+"Mismatches (min editdistance to genome): "+str(mm)+"\n")
        f.write(z+"Identity (min identity allowed to genome): "+str(ident)+"\n")
        f.write(z+"RazerS recognition rate: "+str(rr)+"\n")
        f.write(z+"Output folder created: "+strFolder+"\n")
        f.write(z+"Input Patternfiles used: \n")
        for a in patternfiles:
            f.write("\t"+a+"\n")
        f.write(z+"Input Genomefiles used: \n")
        for b in genomefiles:
            f.write("\t"+b+"\n")
        f.write(z+"\n")
    #f.close()
    
    return myFile

def getFileSize(fName):
    #INPUT: file as string; file and path
    #Source: http://effbot.org/zone/python-fileinfo.htm
    #import os, time
    #from stat import * # ST_SIZE etc
    from stat import ST_SIZE # ST_SIZE etc
    
    fSize=0
    
    try:
        st = os.stat(fName)
    except IOError:
        print "\n\tFailed to get information about: ", file
    else:
        #print "file size:", st[ST_SIZE]
        fSize = st[ST_SIZE]
        #print "file modified:", time.asctime(time.localtime(st[ST_MTIME]))
    return fSize

def reduceQGramListAtRuntime(razerSOutputFormat, output_folder, qgramlist, posStrList, rOutFNme, razeroutputfilename):
#reduce current list of patternfiles by those which have already been found and
# thus are unsuitable anyway (makes no sense to let them be searched again against
# the genome once more
#check if razerS has successfully written an output file:
#print "getFileSize(razeroutputfilename): ", getFileSize(razeroutputfilename)
    if getFileSize(razeroutputfilename) > 0:
        #convert two lists into one dict with posStrList as Key and qgramlist as value
        # qgramDict = {'seg8(00608:00621)': 'GAGAAGCAGTAAT', 'seg8(00442:00455)': 'GGGCTTTCACCGA', ...}
        qgramDict = dict(zip(posStrList, qgramlist)) #new in v=0.7
        qgramDict = purgeByGenome(output_folder, [str(rOutFNme)], qgramDict, razerSOutputFormat, False)
        #split dict into two lists (overwriting existing lists)
        # posStrList will contain: ['seg1(00000:00020)', 'seg1(00001:00021)', 'seg1(00002:00022)', ...] #TODO: 0-20 sind 21 Elemente!!!!
        # qgramlist will contain: ['AAGTC...', 'TTCGA...',...]
        posStrList = qgramDict.keys()
        qgramlist = qgramDict.values()
        
    return [qgramlist,posStrList]

def estimateRemainingTime(startTime, nCall, nTotalCalls):
    strMsg = "\n"
    remainingTime = (((time.clock() - startTime)/nCall)*(nTotalCalls-nCall) / 3600) # in hours
    if remainingTime <1:
        strMsg =  "\tEstimated remaining execution time: %.2f min" % (remainingTime * 60) # in min
    else:
        strMsg =  "\tEstimated remaining execution time: %.2f hours" % remainingTime # in hours
    #print strMsg
    return strMsg

def appendMsgToFile(strFile, strMsg, bTimeStamp):
# Tiny function to add msg to a file
#    strFile: full path and file name of the file to be opened ('append-modus')
#    strMsg: string to be appended
#    bTimeStamp: boolean, adds a time-stamp before the msg

    try:
        with open(strFile, 'a') as f:
            if bTimeStamp:
                strMsg= str(datetime.datetime.now()) + ": " + strMsg
            f.write("\n" + strMsg) #new: only when posStrList = "seg2(0000:0020)"
        f.close()
    except:
        print "\t\t(Not important; but failed to add above msg to info-file.)"
        
#-----------------------------------
# MAIN-BODY of CODE
#-----------------------------------
if __name__=='__main__':
    
    #USer-Feedback on starting up the program
    print "\n----STARTING UP---------"
    
    #create a range of probe-lengths to be tested
    #rng_q = range(q_min,q_max+1)
    #rng_q.reverse()
    
    #estimate remaining time
    startTime = time.clock()
    
    ##folder_pattern
    ##folder_genome
    
    #Empty handle for info-file
    fInf=[]
    
    #for q in rng_q:
    nCall=0 #counter: will count the current call of razerS 
    for tpl in myParam:
        q=tpl[0]
        mm=tpl[1]
        
        #create an output-folder
        output_folder = createOutputFolder(mm, rr, q)
        
        #User-feedback
        print "\nUsing probe length = ", str(q)," with mismatch length = ", str(mm), "\n"
        #print "out_f: ", out_f
        #print "outfold_: ", output_folder        
        
        #calculate identity for razerS:
        if mm>0:
            ident = round((1-((mm-1)/float(q)))*100,2) #razerS requires the identity to be in percent. See "razerS -h" for details
            if ident<50:
                print "\tWarning: Identity at given seq-length and required mismatches was calculated to be below 50%, thus it was set to the minimum value of 50% (as required by razerS)."
                ident=50
                
        #Read in all files in the patter directory and the genome directory
        patternfiles = getDirFilesEndsWith(folder_pattern, ".fa")
        genomefiles = getDirFilesEndsWith(folder_genome, ".fa") 
        
        #check for existance
        if not patternfiles:
            print("Either pattern-directory not correct or empty: "+str(folder_pattern))
            break
        if not genomefiles:
            print("Either genome-directory not correct or empty: "+str(folder_genome))
            break
        
        #calculate total amounts razerS is projected to be called:
        nTotalCalls = len(myParam)*len(patternfiles)*len(genomefiles)

        
        #---------------------------
        #Shelve variables
        #---------------------------
        shelve_file=join(output_folder, shlv_name)#'/tmp/shelve.out' #print "shlv_filename: ", shlv_filename
        print "\nSTARTING: dumping variables into shelve: ", shelve_file
        my_shelve = shelve.open(shelve_file,"n") # 'n' for new
        my_shelve['v'] = v #version number of this script
        #my_shelve['bNonMatchFinder'] = bNonMatchFinder #mode in which program runs
        my_shelve['bReduceSeqAtRuntime'] = bReduceSeqAtRuntime #can increase speed but be careful
        my_shelve['mm'] = mm #editdistance to genome in mismatches
        my_shelve['rr'] = rr #recognition rate with which the genome was scanned through
        my_shelve['q'] = q #
        my_shelve['ident'] = ident #
        my_shelve['razerSOutputFormat']=razerSOutputFormat #new in v=0.6
        my_shelve['bInDelAsError']=bInDelAsError #new in v=0.63
        my_shelve['strErrFile']=strErrFile #new in v=0.63
        my_shelve['patternfiles'] = patternfiles #
        my_shelve['genomefiles'] = genomefiles #
        print " DONE: dumping variables."
        
        #Dump all Parameters into a user-readable info-file
        strInfoFile = createInputParamFile(output_folder, strReadMe, "# ", v, bNonMatchFinder, bReduceSeqAtRuntime, mm, rr, q, ident, razerSOutputFormat, patternfiles, genomefiles)
        if strInfoFile:
            print "hallo"
            
        #Run through all pattern-files (e.g. all virus-segments supplied)
        for patternfile in patternfiles:
            #if not patternfile.endswith(".fa"): continue #depricated: not needed because of use of getDirFilesEndsWith
            #Run through all genome-files (e.g. all host-genome-chromosomes)
            
            #from the pattern-file create a list of n-grams of length q
            # qgramlist will contain: ['ATGGATGTCAATCCGACCTT', 'TGGATGTCAATCCGACCTTA', ...]
            # whereas posStrList will contain: ['seg1(00000:00020)', 'seg1(00001:00021)', 'seg1(00002:00022)', ...] #TODO: 0-20 sind 21 Elemente!!!!
            #[qgramlist,posStrList] = create_qgram_list(q, start, end, join(folder_pattern, patternfile))
            [qgramlist,posStrList] = create_qgram_list(q, start, end, folder_pattern, patternfile)
                              
            #create a qgramfilename unique for each pattern
            qgramfilename = '_'.join([patternfile[:-3],str(str(q)+"nt"),qgramfile])
            qgramfilename = join(output_folder,qgramfilename)
            
            #create a fasta-file with all n-grams: when speed-modus is FALSE, file is written only once per pattern
            if (bReduceSeqAtRuntime == False):
                create_qgram_file(qgramfilename, qgramlist,posStrList,patternfile[:-3])            
            
            for genomefile in genomefiles:
                #create a fasta-file with all n-grams: when speed-modus is TRUE, file is written for every genome-scanned
                # while this causes a delay due to writing, it can enhance the searching process because the total number
                # of sequences to be searched are subsequently reduced by purging the list of patterns to be searched
                
                nCall = nCall+1
                
                if bReduceSeqAtRuntime:
                    create_qgram_file(qgramfilename, qgramlist,posStrList,patternfile[:-3])
                
                #if not genomefile.endswith(".fa"): continue #depricated: not needed because of use of getDirFilesEndsWith  
    
                #create a name for razerS-Output file
                rOutFNme = str(genomefile[:-3]+patternfile+".result")
                razeroutputfilename = join(output_folder,rOutFNme)
                
                #instatiate basic razerS-arguments
                #razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-o", razeroutputfilename,"-a"]
                razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-o", razeroutputfilename]
                
                if razerSVerboseMode: #leaves razerS talkative                
                    razers_arg.append(str(razerSVerboseMode))

                #create a string containing all parameters to execute razer both verbose as well as with a specified output-file-name
                if razerSOutputFormat =="of0": #default razerS-output format
                    razers_arg.append("-a")
                    #razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-v", "-o", razeroutputfilename,"-a"]
                    #razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-o", razeroutputfilename,"-a"]
                if razerSOutputFormat =="of1": #enhanced FASTA-output of razerS; see "razerS -h" for help
                    razers_arg.append("-a") #dump the alignment for each match
                    razers_arg.append("-of") #specification of output format
                    razers_arg.append(str(1))  #specification of output format
                    #razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-o", razeroutputfilename,"-a", "-of", str(1)]

                #consider indels as mismatches as well: expand razerS-call string by argument
                if bInDelAsError:
                    razers_arg.append("-id")
                
                if strErrFile:
                    #create a name for Error (=InDelMissmatch) Distribution file
                    #    razeroutputfilename = join(output_folder,genomefile[:-3]+str(strErrFile))
                    #create an indel/mismatch error distribution file: expand razerS-call string by argument
                    razers_arg.append("-ed")
                    razers_arg.append(str(genomefile[:-3]+str(strErrFile)))
                                
                #dump razerS-Call: 
                my_shelve['razers_arg'] = razers_arg
                
                #User-Feedback
                #print "\n" + "("+str(nCall)+"/"+str(nTotalCalls)+"): " + str(datetime.datetime.now()) + ": Prepared to call razerS with arguments: \n\t", razers_arg[1:]
                strMsg1 = str("\n" + "("+str(nCall) + "/" + str(nTotalCalls) + "): " + str(datetime.datetime.now()) + ": Prepared to call razerS with arguments: \n\t")
                #print strMsg1
                strMsg1 = strMsg1+ str(razers_arg[1:])
                #strMsg1 = str("\n" + "("+str(nCall)+"/"+str(nTotalCalls)+"): " + str(datetime.datetime.now()) + ": Prepared to call razerS with arguments: \n\t", razers_arg[1:])
                print strMsg1; appendMsgToFile(strInfoFile, strMsg1, False)
                
                #check if file with qgrams is empty (abort if empty)
                #print "File-size qgramfilename: ", getFileSize(qgramfilename)
                strMsg2 = "\n"                
                if not getFileSize(qgramfilename) > 0:
                    strMsg2 = "\n\tNOT calling razerS, as "+str(qgramfilename)+" is empty"
                    print strMsg2; appendMsgToFile(strInfoFile, strMsg2, False)
                    continue
                
                #check if ident is smaller 100, such that calling razerS makes sense
                strMsg3 = "\n"
                if ident>=100:
                    strMsg3= "\tWarning: number of mismatches (between pattern and host genome) still tolerated is currently zero.\nThis makes no sense as it would allow for probes that interact with both the pattern and the genome!"
                    print strMsg3; appendMsgToFile(strInfoFile, strMsg3, False)
                    continue
                
                #prepare to call razerS                
                print "\tCalling razerS ...\n\tAs long as the red square next to the grey cross is lighted up razerS is still running ..."
                
                #Give out Estimation of Remaining Time until end of execution
                strMsg4 = "\n"
                if (nCall>len(genomefiles)):
                    strMsg4 = estimateRemainingTime(startTime, nCall, nTotalCalls)
                    print strMsg4; appendMsgToFile(strInfoFile, strMsg1, False)
                
                #Routine to call razerS
                strMsg5 = "\n"                        
                try:
                    #actually call razers
                    subprocess.call(razers_arg)
                    #reduce qugramlist by sequences already found by razerS
                    if (bNonMatchFinder&bReduceSeqAtRuntime): #TODO: and if not last file
                        [qgramlist,posStrList] = reduceQGramListAtRuntime(razerSOutputFormat, output_folder, qgramlist, posStrList, rOutFNme, razeroutputfilename)
                        
                #catch/exception
                except:
                    strMsg5 = "\tSome Error Occurred while calling razerS ... continuing nevertheless...."
                    print strMsg5; appendMsgToFile(strInfoFile, strMsg5, False)
                    pass
                    #user-output: fehler
                    #write to info-file: fehler
                
                    
    
        my_shelve.close() #close after all runs
        strMsg555 = "\n Parameter pair successfully finished.\n------------------------------\n" 
        print  strMsg555; appendMsgToFile(strInfoFile, strMsg555, True)
#        remainingTime = (((time.clock() - startTime)/nCall)*(nTotalCalls-nCall) / 3600) # in hours
#    if remainingTime <1:
#        strMsg =  "\tEstimated remaining execution time: %.2f min" % (remainingTime * 60) # in min
#    else:
#        strMsg =  "\tEstimated remaining execution time: %.2f hours" % remainingTime # in hours

    #strMsg999 = "\n" + str(datetime.datetime.now()) + ": Entire listjob finished." 
    strMsg999 = "\n ---------------------------------------------\Entire parameter-list finished successfully.\n---------------------------------------------"
    print  strMsg999; appendMsgToFile(strInfoFile, strMsg999, True)

    