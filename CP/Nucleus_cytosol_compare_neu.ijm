macro "Open All Files" {
DIR=getDirectory("Choose Folder");
NAMES=getFileList(DIR);
for (i=0; i<NAMES.length; i++) {
open(DIR+NAMES[i]);
run("Stack to Images");
close();
excelfile=replace(DIR,"tiff-export","analysis");
image1=NAMES[i];
image2=NAMES[i];
extensionnucleo=replace(image1,".tif","nucleo.xls");
extensioncyto=replace(image1,".tif","cyto.xls");
image1=replace(image1,".tif", "-0001");
image2=replace(image2,".tif", "-0002");
run("8-bit");

selectWindow(image1);
run("Threshold...");
waitForUser("Adjust threshold of DAPI and Apply!");

imageCalculator("Min create",image2,image1);
run("Measure");
selectWindow("Results");
  saveAs("Measurements", excelfile+extensioncyto); 

run("Clear Results");
selectWindow(image1);
run("Invert");
imageCalculator("Min create", image2,image1);

waitForUser("Set threshold 1-255 without pressing apply!");
run("Analyze Particles...", "size=0.01-Infinity circularity=0.01-1.00 show=Outlines display clear");
selectWindow("Results");
  saveAs("Measurements", excelfile+extensionnucleo); 

run("Clear Results");
while (nImages>0) { 
          selectImage(nImages); 
          close(); 
      } 
}
} 
