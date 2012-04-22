import fileinput
import os
import re
from os.path import join
from dircache import listdir

path = "C:\Users\MJS\Dropbox\Studium\Berufspraktikum\Project Tracking Chris" # change this as desired
#path = os.getcwd()

outfilename = "Spot_Tracker_Results.mdf"
trackID = 1

writestring = "MTrackJ 1.4.1 Data File\n"
writestring += "Displaying true true true 1 2 0 4 100 10 0 0 0 2 1 12 0 false false false false\n"
writestring += "Assembly 1 FF0000\n"
writestring += "Cluster 1 FFFF00\n"

l = listdir(path)
for infilename in l:
    if infilename.endswith(".xls"):
        writestring += "Track %i FF0000 true\n" % trackID
        
        # read offset time as the minimum integer in the filename
        try:
            toffset = min(map(int, re.findall(r'\d+', infilename))) #extract integers, map them to ints, take minimum
        except:
            toffset = 0 # if no int is in the filename
        print toffset
        for i, line in enumerate(fileinput.input([join(path, infilename)])):
            if not fileinput.isfirstline():
                writestring += "Point " + str(i) + " "
                linelist = line.split()
                writestring += linelist[1]+" " # x
                writestring += linelist[2]+" " # y
                writestring += "1.0 %.1f " % float(linelist[0]) # z (slice), t (frame)
                writestring += "1.0\n" # c (channel)

        trackID += 1

writestring += "End of MTrackJ Data File\n"

outfile = open(join(path, outfilename), "w")
print writestring
outfile.write(writestring)
outfile.close()

print "Done."