macro "ZProject" {
DIR=getDirectory("Select directory which contains the image NG files");
NAMES=getFileList(DIR);
count=0;
for (i=0; i<NAMES.length; i++) {
	if (endsWith(NAMES[i], "NG.TIF")) {
		open(DIR+NAMES[i]);
		run("Z Project...", "start=1 stop="+nSlices+" projection=[Max Intensity]");
		selectWindow("MAX_"+NAMES[i]);
		file = "MAX_"+NAMES[i];
		save(DIR+file);
		selectWindow(NAMES[i]);
		close();
	}
	else if (endsWith(NAMES[i], "Qusar610.TIF")){
		open(DIR+NAMES[i]);
		run("Z Project...", "start=1 stop="+nSlices+" projection=[Max Intensity]");
		selectWindow("MAX_"+NAMES[i]);
		file = "MAX_"+NAMES[i];
		save(DIR+file);
		selectWindow(NAMES[i]);
		close();

	}
} 
