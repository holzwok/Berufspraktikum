import fileinput

infilename = "Spot Tracker Results.xls"
outfilename = "Spot Tracker Results.mdf"

infile = open(infilename, 'r')

writestring = "MTrackJ 1.5.0 Data File\n"
writestring += "Displaying true true true 1 2 0 4 100 10 0 0 0 2 1 12 0 false false false false\n"
writestring += "Assembly 1 FF0000\n"
writestring += "Cluster 1 FFFF00\n"
writestring += "Track 1 FF0000 true\n"

for i, line in enumerate(fileinput.input([infilename])):
    if not fileinput.isfirstline():
        writestring += "Point " + str(i) + " "
        linelist = line.split()
        writestring += linelist[1]+" " # x
        writestring += linelist[2]+" " # y
        writestring += linelist[0]+" " # t
        writestring += "1.0\n" # z

writestring += "End of MTrackJ Data File\n"

print writestring

outfile = open(outfilename, "w")
outfile.write(writestring)
outfile.close()