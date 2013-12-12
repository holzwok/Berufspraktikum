
NT = 24; // number of times
NF = 13; // number of frames in stack
COLOR = "grün";
CHANNEL = "C002";
KACHEL = "4";

PREPATH = "\\\\Biodata\\molbp\\GabiSchreiber\\051213_Mating_with_cheater\\Mating_with cheater\\";
FILETRUNK = "s_" + CHANNEL + "Z0";
PROCESSED = "Kachel" + KACHEL + "_processed\\";
File.makeDirectory(PREPATH + PROCESSED);

// 1. Build stacks of 13 frames
print("1. Building stacks...");
for(t=1; t<=NT; t++) {
    if(t<10) {
    	TIME = "0" + t;
    }
    else {
    	TIME = t;
    }
    DIR = "Kachel" + KACHEL + "_" + COLOR + "__" + TIME + ".oif.files\\";
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
    saveAs("Tiff", PREPATH + PROCESSED + "Stack_Kachel" + KACHEL + "_GFP_" + COLOR + "_" + CHANNEL + "_T" + TIME + ".tif");
    run("Close All");
}

// 2. Build time stacks
print("2. Building time stacks...");
for(t=1; t<=NT; t++) {
    if(t<10) {
    	TIME = "0" + t;
    }
    else {
    	TIME = t;
    }
    open(PREPATH + PROCESSED + "Stack_Kachel" + KACHEL + "_GFP_" + COLOR + "_" + CHANNEL + "_T" + TIME + ".tif");
}
run("Concatenate...", "all_open title=Timestack_Kachel" + KACHEL + "_GFP_" + COLOR + ".tif");
run("Stack to Hyperstack...", "order=xyztc channels=1 slices=" + NF + " frames=" + NT + " display=Color");
saveAs("Tiff", PREPATH + PROCESSED + "Timestack_Kachel" + KACHEL + "_GFP_" + COLOR + "_" + CHANNEL + ".tif");
run("Close All");

print("Finished Channel_merger script.");
