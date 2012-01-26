import fileinput
import os
from os.path import join
from dircache import listdir

#path = "C:\Users\MJS\Workspace_2\Berufspraktikum\SpotTracking" # change this as desired
path = os.getcwd()

outfilename = "Spot_Tracker_Results.mdf"
trackID = 1

writestring = "MTrackJ 1.5.0 Data File\n"
writestring += "Displaying true true true 1 2 0 4 100 10 0 0 0 2 1 12 0 false false false false\n"
writestring += "Assembly 1 FF0000\n"
writestring += "Cluster 1 FFFF00\n"

l = listdir(path)
for infilename in l:
    if infilename.endswith(".xls"):
        writestring += "Track %i FF0000 true\n" % trackID
        
        for i, line in enumerate(fileinput.input([join(path, infilename)])):
            if not fileinput.isfirstline():
                writestring += "Point " + str(i) + " "
                linelist = line.split()
                writestring += linelist[1]+" " # x
                writestring += linelist[2]+" " # y
                writestring += "1.0 %.1f " % float(linelist[0]) # z, t
                writestring += "1.0\n" # c

        trackID += 1

writestring += "End of MTrackJ Data File\n"

outfile = open(join(path, outfilename), "w")
outfile.write(writestring)
outfile.close()

print "Done."