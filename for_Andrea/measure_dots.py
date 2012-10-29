from subprocess import call
from os import listdir
from os.path import join
import matplotlib.pyplot as plt
import csv

# fiji settings
fiji = r"C:\Program Files\Fiji.app\fiji-win64.exe"
scriptname = "find_dots.ijm"

# image settings
path = r"C:\Users\MJS\git\Berufspraktikum\for_Andrea"
fileslist = ["A1.tif", "B1.tif", "C1.tif"]


def run_fiji(fileslist):
    s = "%s %s -macro %s -batch" % (fiji, join(path, file), scriptname)
    print "external call:", s
    call(s.split())


def process_results(spreadsheet):
    print spreadsheet
    spotareas = []
    for d in csv.DictReader(open(spreadsheet), delimiter='\t'):
        spotareas.append(float(d['Area']))
    return spotareas
    
    
if __name__ == "__main__":
    for file in fileslist:
        run_fiji(fileslist)

    spreadsheets = [file for file in listdir(path) if ".xls" in file]
    for spreadsheet in spreadsheets:
        spotareas = process_results(spreadsheet)

        plt.hist(spotareas, bins=100)
        #plt.title("test")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.show()
