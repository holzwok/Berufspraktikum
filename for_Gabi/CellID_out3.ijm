macro "open_oif_stacks Macro" {
    PATH=getDirectory("Please Choose the Oif Directory"); // Opens a dialog window for the selection of the directory.
    PATHOUT=PATH+"Cell_ID_Out/";
    File.makeDirectory(PATHOUT);
    list = getFileList(PATH);

    highestVar= 0;
    highestGrad2= 0;
    highestAutoCorr= 0;
    
    focusedVar=0;
    focusedGrad2=0;
    focusedAutoCorr=0;
    focusedSlice=0;
    
    Var_threshold = 0.0;
    theta = 5.0;
    counter=0;

    for(i=0; i<list.length; i++) {
        if (!endsWith(list[i], "/")){
	    print("***********" + list[i] + "************");
            run("Bio-Formats Importer", "check_for_upgrades open=" + PATH +list[i]+" autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");
            getDimensions(w,h,channels,slices,frames);
	    //run("Color Balance...");
	    //run("Enhance Contrast", "saturated=0.35");
            for(k=3; k<slices-1; k++) {
                Stack.setPosition(1,k,1)
                run("Clear Results");
                run("Set Measurements...", "  mean redirect=None decimal=5");
                run("Measure");
                mean = getResult("Mean");
                selectWindow("Results");
                run("Close");
                W = getWidth();
                H = getHeight();
                
		b = 0;
		normVar = 0; // Set to 0 which is out of focus

		for (j=0; j<H; j++) {
                   for (l=0; l<W; l++) {
		      p = getPixel(l,j);
		      t = (p-mean)*(p-mean);
		      b += t;
                  }
                }
           
                normVar = b/(H*W*mean); // Maximum value is best-focused, decreasing as defocus increases
                print("Normalized variance of slice " + k + ": " + normVar); // This can also (should) be changed to return(normVar)
                if (normVar > highestVar){
                    highestVar = normVar;
                    focusedVar=k;
                }

		Stack.setPosition(2,k,1)

		grad2 = 0; // Set to 0 which is out of focus
		autoCorr = 0; // Set to 0 which is out of focus


		for (j=0; j<H-2; j++) {
                   for (l=0; l< (W-2) ; l++) {
		      p = getPixel(l,j);
		      px1 = getPixel(l+1,j);
		      px2 = getPixel(l+2,j);

		      py1 = getPixel(l,j+1);
		      py2 = getPixel(l,j+2);

		      tx = (p-px2)*(p-px2);
		      if (tx > theta) grad2 += tx;

		      ty = (p-py2)*(p-py2);
		      if (ty > theta) grad2 += ty;

		      temp = p*px1 - p*px2;
		      temp += p*py1 - p*py2;
		      autoCorr += temp;
                  }
                }

		if (grad2 > highestGrad2){
                    highestGrad2 = grad2;
                    focusedGrad2=k;
                }
		
		if (autoCorr > highestAutoCorr){
                    highestAutoCorr = autoCorr;
                    focusedAutoCorr = k;
                }

		temp = (focusedVar + focusedAutoCorr)/2.0; 

		focusedSlice = round( temp ); 


		 print("Highest normalized Variance of stack: " + highestVar + " at slice: " + focusedVar);
		 print("Highest Brenner gradient of stack: " + highestGrad2 + " at slice: " + focusedGrad2);
		 print("Highest AutoCorrelation of stack: " + highestAutoCorr+ " at slice: " + focusedAutoCorr);
		 print("Currently focused slice: " + focusedSlice);
            }
	    


            Stack.setPosition(2,focusedSlice,1);

            startSlice=focusedSlice-2;
            endSlice=focusedSlice+2;
            if ((startSlice>0) && (endSlice<slices+1) && ( highestVar > Var_threshold)){
		counter=counter+1;
		
		stackTitle= getTitle();
		run("Duplicate...", "title=" +  stackTitle + " duplicate channels=2 slices=" + focusedSlice);
		saveAs("Tiff", PATH+"Cell_ID_Out/BF_Position"+counter+"_time0_focus");
		run("Close");

                run("Z Project...", "start=startSlice stop=endSlice projection=[Average Intensity]");
		//averageTitle=getTitle();
		fileTitle=File.nameWithoutExtension;
		//print(fileTitle);
		run("Stack to Images");
		//selectWindow("AVG_"+fileTitle+"-1-0002");
		selectImage(nImages);
		saveAs("Tiff",PATH+"Cell_ID_Out/BF_Position"+counter+"_time0");
		close();

		selectImage(nImages);
		//selectWindow("AVG_"+fileTitle+"-1-0001");
		saveAs("Tiff", PATH+"Cell_ID_Out/GFP_Position"+counter+"_time0");
		close();

		print("Finally focused: " + focusedSlice );
		print("--------------------------------");

            }

	    highestVar = 0;
	    highestGrad2 = 0;
	    highestAutoCorr = 0;


            while (nImages>0) {
                selectImage(nImages);
                print(nImages);
                close();
                }
	    
            
        }
    }
    
    for (i=1; i<counter+1; i++){
	GFP_FILE=File.open(PATHOUT+"GFP_" + i + ".txt");
        print(GFP_FILE,"GFP_Position"+i+"_time0.tif");
	File.close(GFP_FILE);
    }

    for (i=1; i<counter+1; i++){
	BF_FILE=File.open(PATHOUT+"BF_" + i + ".txt");
        print(BF_FILE,"BF_Position"+i+"_time0.tif");
	File.close(BF_FILE);
    }
    
}