name = substring(getTitle, 0, lengthOf(getTitle)-1-3);
path = getInfo("image.directory");
n = nSlices();
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
	saveAs("Tiff", path+name+"-"+fillstring+i+".tif");
	close();
}

