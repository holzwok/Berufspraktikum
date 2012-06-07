name = substring(getTitle, 0, lengthOf(getTitle)-4);
path = getInfo("image.directory");

run("Smooth");
run("8-bit");
run("Make Binary");
run("Dilate");
run("Dilate");
run("Dilate");
run("Dilate");
run("Dilate");
run("Dilate");
run("Dilate");
run("Close-");
run("Fill Holes");

saveAs("Tiff", path+name+"_mask.tif");
