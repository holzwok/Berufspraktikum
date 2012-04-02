from os import listdir, remove, rename
from os.path import exists, join
from shutil import copyfile

outpath = '/home/basar/Personal/Martin_Seeger/working_directory/Movie_2.oif.files'

lout = listdir(outpath)
for filename in sorted(lout):
    if ".tif" in filename and not "~" in filename:
        # make backup copies
        if exists(filename+"~"): remove(filename+"~")
        if exists(filename): copyfile(filename, filename+"~")
        
        # 1st try: we use Z-stack position as position token
        # 2nd try: we make a stack and create a fixed position token

        timetoken = filename[-7:-4]
        positiontoken = filename[-11:-8]
        if "C001" in filename:
            imagetype = "NIBA"
        elif "C002" in filename:
            imagetype = "DIC"
        newfilename = "_".join([timetoken, positiontoken, imagetype+".TIF"])
        rename(join(outpath, filename), join(outpath, newfilename))
        print newfilename

#s_C001Z001T001.tif  C001= GFP Kanal; Z001= ganz oben im Z-Stack, T001= erste Aufnahme
#s_C002Z001T017.tif  C002= Hellfeld; Z001= ganz oben im Z-Stack, T017= 17te Aufnahme

# we need to rename to:
# anything_time_position_token.TIF