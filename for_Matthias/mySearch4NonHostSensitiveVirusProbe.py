'''
Designing a Virus-Probe lacking host-target-sequence

Created on 13.04.2012

@author: Matthias Schade, Martin Seeger
         Molecular Biophysics, Humboldt-University Berlin, Germany
'''



#----------------------------------------
#IMPORT CLASSES/FUNCTIONS
#----------------------------------------
from Bio import SeqIO
from Bio import Entrez
import datetime
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from collections import OrderedDict
import pprint
import pickle
from time import sleep
#from Bio.Seq import Seq
#from Bio.Alphabet import NucleotideAlphabet
#from Bio.Alphabet import IUPAC


#----------------------------------------
#INPUT-PARAMERS
#----------------------------------------
##set global email adress with NCBI/Entrez:
Entrez.email = "matthiasschade.de@googlemail.com" #necessary???
#handle = Entrez.efetch(db="nucleotide", id=idlist, retmode="xml")
#records = Entrez.read(handle)

#Probe length in nucleotides (10-30)
nProbeLen = 20

#Virus-Genome: Nucleotide Sequence for which a complementary probe shall be found
seq_v_file = "V01099.fa" #seq_H_taxid = "V01099" # M1
rng_v = range(450,454) #nucleotides to be considered: start and end nucleotide

#Host Genome : http://www.ncbi.nlm.nih.gov/genome/seq/BlastGen/BlastGen.cgi?taxid=9615
#seq_H = ""      #full sequence if available
#seq_H_taxid = 9615 #taxonomy identifier
BLAST_orgn="Canis familiaris[orgn]"

#BLAST-algorithm used
BLAST_algr = "blastn"

#BLAST-database used
#    large: "nt", "genbank", 
#    dog: "9615_genomic" (dog genomic), "dog_9615" (SNP database for dog),
#    human: "9606_genomic" (human genomic)
BLAST_db = "nt"

#Histlist_size returned by blast from query
qHitSize = 5

#required minimum identity for blast hit to be returned
qPerIdent = 50

#Rejection criterion: how many mismatches allowed
#nMM = 2 

#query-result filenames for saving: output format will be ['results_file'####.xml]
results_file = "test"

#Maximum OS-dependent length of filename 
maxFileLen=100

#Name of file for dumping results as pickle
pickle_file = "my_pickle"

#add a delay in between two queries to the internet-database (
queryDelay=1 #sleeps for 5 seconds


#----------------------------------------
# FUNCTIONS
#----------------------------------------
#Function to generate sequences of a defined length. Returns a Sorted Dict with unique strings (as key) and occurrence-number as value
def generat_seqs(seq_v_file, rng_v, nProbeLen):
    #read in file with nucleotides
    seq_v = SeqIO.read(seq_v_file, "fasta")
    
    #User-Feedback
    desc=seq_v.description
    print 
    print '    Virus-sequence loaded: ', desc
    print '    Length of Virus-sequence [nt]: ', len(seq_v)
    print 
    
    #create empty list for query-sequences
    queries = []
    
    #create list of sequences of length 'nProbeLen'
    for i, n in enumerate(rng_v): 
        #extract relevant sequence from virus-genome
        if n+nProbeLen <= len(seq_v):
            seq_now = seq_v.seq[n:n+nProbeLen] #string containing nucleotide sequence only
            queries.append(str(seq_now))
    
    #reduce query-list to unique entries with value as occurrence-count
    querydict = dict((j, queries.count(j)) for j in set(queries))
    
    #sort dict by key-value, beginning with the largest values
    querydict2= OrderedDict(sorted(querydict.items(), reverse=True, key=lambda t: t[1]))
    
    #return
    return querydict2 #note: ordered dict

def getBestHSP(blast_records):
    #for the best hit get the number of positive matches
    #return both the best HSP_positive and the number of records checked
    hspMax=0    #best identity hit
    k=0
    try:
        blast_record = blast_records.next()
        for alignment in blast_record.alignments:
            k=k+1
            m=0
            for hsp in alignment.hsps:
                m=m+1
                #print hsp.positives, k, m
                if hsp.positives>hspMax:
                    hspMax=hsp.positives
    except:
        print "the end of checking for HSP."
    #return
    return [hspMax,k]



#----------------------------------------
# PROGRAM
#----------------------------------------

#track time consumption
t1start = datetime.datetime.now()

#User-Feedback
print '-------------------------------------------------------------'
print ' Designing a Virus-Probe lacking virus-host target-sequence  '
print '-------------------------------------------------------------'
print
print 'Input-Parameters'
print '    BLAST-Parameters: ', BLAST_algr, BLAST_db, qHitSize, qPerIdent, BLAST_orgn
print '    Virus-Genome-Parameters: ', seq_v_file, len(rng_v)
print '    Probe-Length (nt): ', nProbeLen
print

#Get generated list of sequences of Virus-Genome
#seq_v = SeqIO.read(seq_v_file, "fasta")
qdict = generat_seqs(seq_v_file, rng_v, nProbeLen)
#create list with sequences only #qSeqLs = sorted(set(qdict.iterkeys())) #WHY 'SORTED'



#create empty dic 
resultsLs={}

i=0
for q in qdict:
#for q in qSeqLs:
    i=i+1
    #print q
    #print datetime.datetime.now(), ': Query started for ', len(qSeqLs),' sequence(s)...'
    print datetime.datetime.now(), '- - Query with(h=',qHitSize,'i=',qPerIdent,') started for',len(q),'nt-long sequence: ', q
    
    #QUERY
    #    result_handle = NCBIWWW.qblast("blastn", "nt", q, hitlist_size=5, perc_ident=50, megablast=True, entrez_query="Canis familiaris[orgn]")
    #    result_handle = NCBIWWW.qblast("blastn", "nt", ["ACCCTG", "ACTTCTG"], entrez_query="Canis familiaris[orgn]")
    #    result_handle = NCBIWWW.qblast("blastn", "nt", q)
    result_handle = NCBIWWW.qblast(BLAST_algr, BLAST_db, q, hitlist_size=qHitSize, perc_ident=qPerIdent, entrez_query=BLAST_orgn)
    
    #Parse Results
    blast_records = NCBIXML.parse(result_handle)
    
    #for the best hit get the number of positive matches
    [hspMax,k]=getBestHSP(blast_records)
    
    #User-Feedback
    if k>0:
        print datetime.datetime.now(), '- -     ... resulting in ', k, ' records fulfilling the requirements with best matching-identity of',hspMax,'/',nProbeLen
    else:
        print datetime.datetime.now(), '- -     ... resulting in 0 records fulfilling the requirements, meaning: this sequence is predicted 100% hybridize a sequence from the specified database.'
            
    #Create a filename for results of the current sequence
    if len(q)<maxFileLen:
        saveFName = str(q + "_vs_"+str(BLAST_db)+str('_%04d' % i) + ".xml")
    else:
        saveFName = str(results_file + str('_%04d' % i) + ".xml")

    #Calculate missmatch-number
    if k>0:
        mm =  nProbeLen-hspMax
    else:
        mm= 0
        
    #Create output dic with 
    #    "sequence: occurences in virusgenome, lowest mismatch in hostgenome, results-filename" 
    resultsLs[q] = [qdict[q], mm,saveFName]
    
    #Save file
    save_file = open(saveFName, "w") #save_file = open("my_blast.xml", "w")
    save_file.write(result_handle.read())
    save_file.close()
    
    #close handle for results
    result_handle.close()
    
    #sleep
    if queryDelay>0:
        print '            User-defined delay [s]:', queryDelay
        sleep(queryDelay) #delays query by value in sec
    

#User-Feedback on Results
print '--------------------------------------------------'
print 'Total Runtime for',i,'queries: ', datetime.datetime.now()-t1start
print '--------------------------------------------------'
print
print 'Input-Parameters'
print '    BLAST-Parameters: ', BLAST_algr, BLAST_db, qHitSize, qPerIdent, BLAST_orgn
print '    Virus-Genome-Parameters: ', seq_v_file, len(rng_v)
print '    Probe-Length (nt): ', nProbeLen
print
print 'Results:' 
print '    Sequence     [freq in virus, min(MM) in host]'

#sort resultLs by missmatches found:
#resultsLs= OrderedDict(sorted(resultsLs.items(), reverse=True, key=lambda t: t[1]))
pprint.pprint(resultsLs)

#Save resultsLs
#file = open("pickle.pck", "w") # write mode
filePCK = open(str(pickle_file)+"_"+str(nProbeLen)+"nts.pck", "w") # write mode
pickle.dump(resultsLs, filePCK)