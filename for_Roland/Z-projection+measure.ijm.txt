macro "Macro 1 [3]" {
dir=getDirectory("oider grandlhuaba");
listFiles(dir); 

function listFiles(dir) {
list = getFileList(dir);
for (i=0; i<list.length; i++) {
if (startsWith(list[i], "s_C001") && endsWith(list[i], ".tif")) {
open(dir+list[i]);
}
}}

run("Images to Stack");
count=nSlices;
print(count);
selectWindow("Stack");
run("Z Project...", "start=1 stop="+count+" projection=[Average Intensity]");
selectWindow("AVG_Stack");
run("Select All");
run("Measure");
selectWindow("Stack");
close();
selectWindow("AVG_Stack");
close();
}