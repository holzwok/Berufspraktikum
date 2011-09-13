name = getTitle;
path = getInfo("image.directory");
n = nSlices();
//run("Z Project...", "start=1 stop="+d2s(n,0)+" projection=[Average Intensity]");
setAutoThreshold("MaxEntropy dark");
run("Z Project...", "start=1 stop="+d2s(n,0)+" projection=[Max Intensity]");
run("Save", "save=["+path+name+"-max.tif]");
selectWindow(name+"-max.tif");
//run("Convert to Mask");
//run("Set Measurements...", "area center stack display redirect=None decimal=6");
//run("Analyze Particles...", "size=0-320 circularity=0.00-1.00 show=Masks display");
//run("Save", "save=["+path+name+"-mask.tif]");
//selectWindow(name+"-max.tif");
close();
//selectWindow(name+"-mask.tif");
//close();
saveAs("Measurements", path+name+".xls"); 



