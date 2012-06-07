#---------------------------------------------------------------------------------------------#
# Purpose:
#    to generate two lists:
#        (i) a list n-grams of a pattern file of type ".fa" (seqmentation into possible probes to be matched against a target genome)
#        (ii)a list of matches between the pattern and a genome file (verification for hits)
#
#Authors: Martin Seeger, Matthias Schade
#---------------------------------------------------------------------------------------------#

import subprocess
from dircache import listdir
from os.path import join
import os
import datetime
import shelve #dumping variables
 
#-----------------------------------------# 
#---------------PARAMETERS----------------#
#-----------------------------------------#
#Version Number of this script
v=0.2
#range of length of probe to be tested for design
q_min = 20 #minimum length to be tested
q_max = 20 #maximum length to be tested

#minimum number of mismatches (between pattern (=virus) and host genome) required 
#in order to reach at a probe which is sufficiently unlikely to interact with host genome
#  note: mm has too be higher than 0, otherwise this entire program makes no sense 
#  example: if mm=3: then all alignments (between pattern and host) which only have 2, 1 or even 0 
#          mismatches will be rejected
mm=3
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

#Input folders:
#    -from the pattern (e.g. virus) a list of n-grams is created to be matched against the genome (e.g. host)
#    -the genome is used for targeting each of the n-grams against
# attention: switch "\" by "/" due to OS
folder_pattern = "D:/Eigene Dateien matthias/workspace/MyTestProject/mynewPythonPackage/pattern/"
folder_genome = "D:/Eigene Dateien matthias/workspace/MyTestProject/mynewPythonPackage/genome/"
#folder_pattern = "D:/Data/Matthias Schade/workspace/VirusProbeDesign/pattern"
#folder_genome = "D:/Data/Matthias Schade/workspace/VirusProbeDesign/genome"

#Name of file into which all n-grams are written (Attention: can possibly be overwritten!!!)
qgramfile = "qgrams.fa" #TODO: generate one qgramfile per pattern generically/automatically without overwriting

#Fasta-name of n-gram-sequences in 'qgramfile' (e.g.: "read")
#qgram_entryname = "read_"

#Shelve file name for saving all variables in output-folder
shlv_name = "shelved.out" #taken from: http://stackoverflow.com/questions/2960864/how-can-i-save-all-the-variables-in-the-current-python-session

#-----------------------------------------#
#-----------END OF PARAMETERS-------------#
#-----------------------------------------#


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    return d

# function to create n-grams from the patternfile of length q starting at position 'start' until reaching 'end-q+1'
def create_qgram_list(q, start, end, patternfile):
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
        posStrList = [str(j)+":"+str(j+q) for j in range(start, end - q + 1)]   
    else:
        #split the pattern into n-grams disregarding positions
        qgramlist = [pattern[i:i + q] for i in range(0, len(pattern)-q+1)]
        #create a position list for each qgramlist: 'starting pos: ending pos' in sense as given in patternfile
        posStrList = [str(j)+":"+str(j+q) for j in range(0, len(pattern)-q+1)]
                
    #print "within:", poslist
    #print qgramlist
    #print len(qgramlist)
    #print len(pattern)
    return [qgramlist ,posStrList]


# function to create a fasta-file containing qgrams
#    -file to be created/overwritten: 'qgramfile'
#    -contend to be filled into file: 'qgramlist'
def create_qgram_file(qgramfile, qgramlist, posStrList,pattern_source):
    readcount = 0
    #open/create file as writable
    with open(qgramfile, 'w') as f:
    #with open(join(fileprefix,"_",qgramfile), 'w') as f:
        #print qgramlist
        #create one fasta-entry by n-gram-entry
        for gram in qgramlist:
            #f.write(">read_" + str(readcount)) #TODO: subsitute with 'qgram_entryname'
            #f.write(">source " + pattern_source+" SequencePos "+posStrList[readcount]) 
            #f.write(">source__" + pattern_source+"("+posStrList[readcount]+")")
            f.write(">" + pattern_source+"("+posStrList[readcount]+")")
            f.write("\n")
            f.write(gram)
            f.write("\n")
            readcount += 1


#-----------------------------------
# MAIN-BODY of CODE
#-----------------------------------
if __name__=='__main__':
    
    #USer-Feedback on starting up the programm
    print "\n----STARTING UP---------"
    
    #create a range of probe-lengths to be tested
    rng_q = range(q_min,q_max+1)
    rng_q.reverse()
                
    for q in rng_q:
        
        #create a folder to dump all related information
        now = datetime.datetime.now()
        out_rel_f= now.strftime("%Y-%m-%d_%H-%M")+"_"+str(q)+"nt"
        out_f= join(os.getcwd(), out_rel_f,"readme.txt") #out_f= join(os.getcwd(), now.strftime("%Y-%m-%d_%H-%M"),"readme.txt")
        output_folder= ensure_dir(out_f)
        
        #User-feedback
        print "\nUsing probe length = ", str(q),"\n"
        #print "out_f: ", out_f
        #print "outfold_: ", output_folder        
        

        
        #calculate identity for razerS:
        if mm>0:
            ident = round((1-((mm-1)/float(q)))*100,2) #razerS requires the identity to be in percent. See "razerS -h" for details
             
        #Read in all files in the patter directory and the genome directory
        patternfiles = listdir(folder_pattern)
        genomefiles = listdir(folder_genome) 
        
        #Shelve variables
        shelve_file=join(output_folder, shlv_name)#'/tmp/shelve.out' #print "shlv_filename: ", shlv_filename
        print "\nSTARTING: dumping variables into shelve: ", shelve_file
        my_shelve = shelve.open(shelve_file,"n") # 'n' for new
        my_shelve['v'] = v #version number of this script
        my_shelve['mm'] = mm #editdistance to genome in mismatches
        my_shelve['rr'] = rr #recognition rate with which the genome was scanned through
        my_shelve['q'] = q #
        my_shelve['ident'] = ident #
        my_shelve['patternfiles'] = patternfiles #
        my_shelve['genomefiles'] = genomefiles #
        print " DONE: dumping variables."
        
        #Run through all pattern-files (e.g. all virus-segments supplied)
        for patternfile in patternfiles:
            if not patternfile.endswith(".fa"): continue #sicherheit: ueberspringt alle nicht-fa files
            #Run through all genome-files (e.g. all host-genome-chromosomes)
            for genomefile in genomefiles:
                if not genomefile.endswith(".fa"): continue #sicherheit: ueberspringt alle nicht-fa files  
                #print patternfile, genomefile
                #from the pattern-file create a list of n-grams of length q
                [qgramlist,posStrList] = create_qgram_list(q, start, end, join(folder_pattern, patternfile))
                #print "outer:", poslist
                #create a qgramfilename unique for each pattern
                qgramfilename = '_'.join([patternfile[:-3],str(str(q)+"nt"),qgramfile])
                #print "qgramfilename: ", qgramfilename
                qgramfilename = join(output_folder,qgramfilename)
                #print "qgramfilename: ", qgramfilename
                
                #create a fasta-file with all n-grams
                create_qgram_file(qgramfilename, qgramlist,posStrList,patternfile[:-3])
                #print "genome: ", join(folder_genome, genomefile)
                #print os.path.isfile(join(folder_genome, genomefile))
                #print "pattern: ",join(folder_pattern, patternfile)
                #print os.path.isfile(join(folder_pattern, patternfile))
                #genomepath = join(folder_genome, "genome.fa")
                #patternpath = join(folder_pattern, "A_PR_8_34.fa")
    
                #create a name for razerS-Output file
                razeroutputfilename = join(output_folder,genomefile[:-3]+patternfile+".result")
                #print "razeroutputfilename: ", razeroutputfilename
                
                #create a string containing all parameters to execute razer both verbose as well as with a specified output-file-name
                razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-v", "-o", razeroutputfilename,"-a"]
                #razers_arg = ["razers", "-i", str(ident), "-rr", str(rr), join(folder_genome, genomefile), qgramfilename, "-v", "-o", genomefile[:-3]+patternfile+".result","-a"]
                ##razers_arg = ["razers", join(folder_genome, genomefile), qgramfilename, "-v", "-o", genomefile[:-3]+patternfile+".result"]
                ###razers_arg = ["razers", join(folder_genome, genomefile), join(qgramfile), "-v"] #WORKING EXAMPLE
                
                #dump razerS-Call: 
                my_shelve['razers_arg'] = razers_arg

                #actually call razers
                print "Calling razers with args: ", razers_arg[1:]
                if ident<100:
                    #print "ident: ", ident
                    subprocess.call(razers_arg)
                else:
                    print "Warning: number of mismatches (between pattern and host genome) still tolerated is currently zero.\nThis makes no sense as it would allow for probes that interact with both the pattern and the genome!"
    
    my_shelve.close()            
    print "\ndone." 
    