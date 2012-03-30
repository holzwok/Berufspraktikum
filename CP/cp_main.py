from dircache import listdir

path = "/home/basar/Personal/Martin_Seeger/CellProfiler_work/output"

l = listdir(path)
for infilename in l:
    if infilename.startswith("MAX_"):
        print infilename
        # maske anwenden:
        # mit .loc file mergen
        # nur punkte filtern/einzeichnen, fuer die maske == true
        # test
        