name = getTitle;
path = getInfo("image.directory");
n = nSlices();

run("Z Project...", "start=1 stop="+d2s(n,0)+" projection=[Max Intensity]");
run("Save", "save=["+path+name+"-max.tif]");
selectWindow(name+"-max.tif");
setAutoThreshold("MaxEntropy dark");
//run("Convert to Mask");
//run("Set Measurements...", "area center stack display redirect=None decimal=6");
//run("Analyze Particles...", "size=0-320 circularity=0.00-1.00 show=Masks display");
//run("Save", "save=["+path+name+"-mask.tif]");
selectWindow(name+"-max.tif");
close();
//selectWindow(name+"-mask.tif");
//close();

name = substring(getTitle, 0, lengthOf(getTitle)-1-3);
run("Stack to Images");
for (i = 1; i <= n; i++) {
	if (i<10) {
		fillstring="000";
	}
	else {
		if (i<100) {
			fillstring="00";
		}
		else {
			if (i<1000) {
				fillstring="0";
			}
			else {
				fillstring="";
				}
			}
	}
	selectWindow(name+"-"+fillstring+i);
	saveAs("Tiff", path+name+"-"+fillstring+i+".TIF");
	print("Created file "+name+"-"+fillstring+i+".TIF");
	close();
}

