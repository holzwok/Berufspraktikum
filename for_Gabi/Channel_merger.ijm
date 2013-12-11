
PREPATH = "\\\\Biodata\\molbp\\GabiSchreiber\\051213_Mating_with_cheater\\Mating_with cheater\\";
FILETRUNK = "s_C001Z0";
PROCESSED = "Kachel5_processed\\";
File.makeDirectory(PREPATH + PROCESSED);

// Build stacks of 13 frames
for(t=1; t<=24; t++) {
    if(t<10) {
    	TIME = "0" + t;
    }
    else {
    	TIME = t;
    }
    DIR = "Kachel5_grün__" + TIME + ".oif.files\\";
    PATH = PREPATH + DIR;
    for(i=1; i<=13; i++) {
        if(i<10) {
            TIFNAME = PATH + FILETRUNK + "0" + i + ".tif";
        }
        else {
            TIFNAME = PATH + FILETRUNK + i + ".tif";
        }
        open(TIFNAME);
    }
    run("Images to Stack", "name=GFP_Stack_T1 title=[] use keep");
    saveAs("Tiff", PREPATH + PROCESSED + "Stack_Kachel5_GFP_T" + TIME + ".tif");
    run("Close All");
}

// Build time stacks
for(t=1; t<=24; t++) {
    if(t<10) {
    	TIME = "0" + t;
    }
    else {
    	TIME = t;
    }
}