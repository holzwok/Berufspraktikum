name = getTitle;
path = getInfo("image.directory");
n = nSlices();
q = maxOf(floor(n/4), 1);
print("ImageJ: only keeping slice "+q+" out of "+n+".");

for (i=n; i>q; i--) {
   setSlice(i);
   //print("Deleting slice "+i+".");
   run("Delete Slice");
}

for (i=q-1; i>=1; i--) {
   setSlice(i);
   //print("Deleting slice "+i+".");
   run("Delete Slice");
}
selectWindow(name);
print("ImageJ: saving file "+path+name+".");
saveAs("Tiff", path+name+"_quarter_slice");
