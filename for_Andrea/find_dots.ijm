//name = getTitle;
name = substring(getTitle, 0, lengthOf(getTitle)-4);
path = getInfo("image.directory");

selectWindow(name+".tif");
run("16-bit");
saveAs("Tiff", path+name+"_16-bit.tif");
setAutoThreshold("MaxEntropy dark");
//run("Threshold...");
run("Convert to Mask");
run("Set Measurements...", "area mean standard center integrated stack redirect=None decimal=6");
run("Analyze Particles...", "size=0-320 circularity=0.00-1.00 show=Masks");
saveAs("Results", path+name+"_Results.xls");
close();
selectWindow(name+"_16-bit.tif");
close();