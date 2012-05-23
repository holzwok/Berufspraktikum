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
 
 
 
#---------------PARAMETERS----------------#
#length of probe to be designed
q = 20

#position of starting nucleotide included into query
start = 540

#position of last nucleotide included into query
end = 760

#Input folders:
#    -from the pattern (e.g. virus) a list of n-grams is created to be matched against the genome (e.g. host)
#    -the genome is used for targeting each of the n-grams against
# attention: switch "\" by "/" due to OS
folder_pattern = "D:/Eigene Dateien matthias/workspace/MyTestProject/mynewPythonPackage/pattern/"
folder_genome = "D:/Eigene Dateien matthias/workspace/MyTestProject/mynewPythonPackage/genome/"

#Name of file into which all n-grams are written (Attention: can possibly be overwritten!!!)
qgramfile = "qgrams.fa" #TODO: generate one qgramfile per pattern generically/automatically without overwriting
#Fasta-name of n-gram-sequences in 'qgramfile' (e.g.: "read")
qgram_entryname = "read_"
#-----------END OF PARAMETERS----------------#



# function to create n-grams from the patternfile of length q starting at position 'start' until reaching 'end-q+1'
def create_qgram_list(q, start, end, patternfile):
    pattern = ""
    #read in the patternfile
    with open(patternfile, 'r') as f:
        for line in f:
            if not line.startswith(">"):
                pattern += line.strip()
    
    #split the pattern into n-grams beginning from starting position
    qgramlist = [pattern[i:i + q] for i in range(start, end - q + 1)]
    
    #print qgramlist
    #print len(qgramlist)
    #print len(pattern)
    return qgramlist


# function to create a fasta-file containing qgrams
#    -file to be created/overwritten: 'qgramfile'
#    -contend to be filled into file: 'qgramlist'
def create_qgram_file(qgramfile, qgramlist):
    readcount = 0
    #open/create file as writable
    with open(qgramfile, 'w') as f:
        #print qgramlist
        #create one fasta-entry by n-gram-entry
        for gram in qgramlist:
            f.write(">read_" + str(readcount)) #TODO: subsitute with 'qgram_entryname'
            f.write("\n")
            f.write(gram)
            f.write("\n")
            readcount += 1


# MAIN-BODY of CODE
if __name__=='__main__':
    
    #USer-Feedback on starting up the programm
    print "\n----STARTING UP---------"
     
    #Read in all files in the patter directory and the genome directory
    patternfiles = listdir(folder_pattern)
    genomefiles = listdir(folder_genome) 
    
    #Run through all pattern-files (e.g. all virus-segments supplied)
    for patternfile in patternfiles:
        if not patternfile.endswith(".fa"): continue #sicherheit: ueberspringt alle nicht-fa files
        #Run through all genome-files (e.g. all host-genome-chromosomes)
        for genomefile in genomefiles:
            if not genomefile.endswith(".fa"): continue #sicherheit: ueberspringt alle nicht-fa files  
            #print patternfile, genomefile
            #from the pattern-file create a list of n-grams of length q
            qgramlist = create_qgram_list(q, start, end, join(folder_pattern, patternfile))
            #create a fasta-file with all n-grams
            create_qgram_file(join(qgramfile), qgramlist)    
            #print "genome: ", join(folder_genome, genomefile)
            #print os.path.isfile(join(folder_genome, genomefile))
            #print "pattern: ",join(folder_pattern, patternfile)
            #print os.path.isfile(join(folder_pattern, patternfile))
            #genomepath = join(folder_genome, "genome.fa")
            #patternpath = join(folder_pattern, "A_PR_8_34.fa")

            #create a string containing all parameters to execute razer both verbose as well as with a specified output-file-name            
            razers_arg = ["razers", join(folder_genome, genomefile), join(qgramfile), "-v", "-o", genomefile[:-3]+patternfile+".result"]
            #razers_arg = ["razers", join(folder_genome, genomefile), join(qgramfile), "-v"] #WORKING EXAMPLE
                      
            #actually call razers
            #print " ".join(razers_arg)
            subprocess.Popen(razers_arg)
            
            
    print "\ndone." 
    