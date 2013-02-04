#!/usr/bin/env python
# -*- coding: iso-8859-1 -*- # Umlaute!

from os.path import join

pathname = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Project_Björn"
filename = "Uncharacterized results-table.tsv"
outfilename = "out.Uncharacterized results-table.tsv"

outline = ""
with open(join(pathname, filename), "r") as infile: 
    with open(join(pathname, outfilename), 'w') as outfile:
        for line in infile:
            linelist = line.split("\t")
            feature_type = linelist[5]
            if feature_type=="Uncharacterized":
                keep_score = 10
            else:
                keep_score = 0
            
            outline = "\t".join(linelist) + "\t" + str(keep_score) + '\n' # gibt noch komische Formatierung
            #print outline
            outfile.write(outline)

#print outline
