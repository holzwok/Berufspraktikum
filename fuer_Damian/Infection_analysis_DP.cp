CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:11710

LoadImages:[module_num:1|svn_version:\'11587\'|variable_revision_number:11|show_window:False|notes:\x5B\'\'\x5D]
    File type to be loaded:individual images
    File selection method:Text-Exact match
    Number of images in each group?:3
    Type the text that the excluded images have in common:Do not use
    Analyze all subfolders within the selected folder?:All
    Input image file location:Default Input Folder\x7C.
    Check image sets for missing or duplicate files?:No
    Group images by metadata?:No
    Exclude certain files?:No
    Specify metadata fields to group by:
    Select subfolders to analyze:
    Image count:2
    Text that these images have in common (case-sensitive):C001
    Position of this image in each group:d0.tif
    Extract metadata from where?:None
    Regular expression that finds metadata in the file name:None
    Type the regular expression that finds metadata in the subfolder path:None
    Channel count:1
    Group the movie frames?:No
    Grouping method:Interleaved
    Number of channels per group:2
    Load the input as images or objects?:Images
    Name this loaded image:DNA
    Name this loaded object:Nuclei
    Retain outlines of loaded objects?:No
    Name the outline image:NucleiOutlines
    Channel number:1
    Rescale intensities?:Yes
    Text that these images have in common (case-sensitive):C002
    Position of this image in each group:d1.tif
    Extract metadata from where?:None
    Regular expression that finds metadata in the file name:None
    Type the regular expression that finds metadata in the subfolder path:None
    Channel count:1
    Group the movie frames?:No
    Grouping method:Interleaved
    Number of channels per group:2
    Load the input as images or objects?:Images
    Name this loaded image:dye
    Name this loaded object:Nuclei
    Retain outlines of loaded objects?:No
    Name the outline image:NucleiOutlines
    Channel number:1
    Rescale intensities?:Yes

IdentifyPrimaryObjects:[module_num:2|svn_version:\'10826\'|variable_revision_number:8|show_window:False|notes:\x5B\'\'\x5D]
    Select the input image:DNA
    Name the primary objects to be identified:Nuclei
    Typical diameter of objects, in pixel units (Min,Max):10,50
    Discard objects outside the diameter range?:Yes
    Try to merge too small objects with nearby larger objects?:No
    Discard objects touching the border of the image?:Yes
    Select the thresholding method:Otsu Global
    Threshold correction factor:1
    Lower and upper bounds on threshold:0,1
    Approximate fraction of image covered by objects?:0.1
    Method to distinguish clumped objects:Shape
    Method to draw dividing lines between clumped objects:Intensity
    Size of smoothing filter:5
    Suppress local maxima that are closer than this minimum allowed distance:5
    Speed up by using lower-resolution image to find local maxima?:Yes
    Name the outline image:NucOutlines
    Fill holes in identified objects?:Yes
    Automatically calculate size of smoothing filter?:No
    Automatically calculate minimum allowed distance between local maxima?:Yes
    Manual threshold:0.0
    Select binary image:MoG Global
    Retain outlines of the identified objects?:Yes
    Automatically calculate the threshold using the Otsu method?:Yes
    Enter Laplacian of Gaussian threshold:.5
    Two-class or three-class thresholding?:Two classes
    Minimize the weighted variance or the entropy?:Weighted variance
    Assign pixels in the middle intensity class to the foreground or the background?:Foreground
    Automatically calculate the size of objects for the Laplacian of Gaussian filter?:Yes
    Enter LoG filter diameter:5
    Handling of objects if excessive number of objects identified:Continue
    Maximum number of objects:500
    Select the measurement to threshold with:None

MeasureObjectIntensity:[module_num:3|svn_version:\'10816\'|variable_revision_number:3|show_window:False|notes:\x5B\'Intensity of nuclei\'\x5D]
    Hidden:1
    Select an image to measure:dye
    Select objects to measure:Nuclei

DisplayDataOnImage:[module_num:4|svn_version:\'10412\'|variable_revision_number:2|show_window:True|notes:\x5B\'\'\x5D]
    Display object or image measurements?:Object
    Select the input objects:Nuclei
    Measurement to display:Intensity_MeanIntensity_dye
    Select the image on which to display the measurements:dye
    Text color:green
    Name the output image that has the measurements displayed:DisplayImage
    Font size (points):12
    Number of decimals:5
    Image elements to save:Image

ClassifyObjects:[module_num:5|svn_version:\'10720\'|variable_revision_number:2|show_window:True|notes:\x5B\'\'\x5D]
    Should each classification decision be based on a single measurement or on the combination of a pair of measurements?:Single measurement
    Hidden:3
    Select the object to be classified:Nuclei
    Select the measurement to classify by:Intensity_MeanIntensity_dye
    Select bin spacing:Custom-defined bins
    Number of bins:20
    Lower threshold:0
    Use a bin for objects below the threshold?:Yes
    Upper threshold:0.5
    Use a bin for objects above the threshold?:No
    Enter the custom thresholds separating the values between bins:0.1
    Give each bin a name?:No
    Enter the bin names separated by commas:
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Name the output image:ClassifiedNuclei
    Select the object to be classified:Nuclei
    Select the measurement to classify by:Intensity_MeanIntensity_dye
    Select bin spacing:Evenly spaced bins
    Number of bins:10
    Lower threshold:0
    Use a bin for objects below the threshold?:No
    Upper threshold:1
    Use a bin for objects above the threshold?:No
    Enter the custom thresholds separating the values between bins:0,1
    Give each bin a name?:No
    Enter the bin names separated by commas:None
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Name the output image:ClassifiedNuclei
    Select the object to be classified:Nuclei
    Select the measurement to classify by:Intensity_MeanIntensity_dye
    Select bin spacing:Evenly spaced bins
    Number of bins:50
    Lower threshold:0
    Use a bin for objects below the threshold?:No
    Upper threshold:1
    Use a bin for objects above the threshold?:No
    Enter the custom thresholds separating the values between bins:0,1
    Give each bin a name?:No
    Enter the bin names separated by commas:None
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Name the output image:ClassifiedNuclei
    Enter the object name:None
    Select the first measurement:None
    Method to select the cutoff:Mean
    Enter the cutoff value:0.5
    Select the second measurement:None
    Method to select the cutoff:Mean
    Enter the cutoff value:0.5
    Use custom names for the bins?:No
    Enter the low-low bin name:low_low
    Enter the low-high bin name:low_high
    Enter the high-low bin name:high_low
    Enter the high-high bin name:high_high
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Enter the image name:None

FilterObjects:[module_num:6|svn_version:\'10300\'|variable_revision_number:5|show_window:False|notes:\x5B\'The last approach is to filter the nuclei on the basis of the number of PH3 children. The number of PH3-positive nuclei is the same as before, but in this case, the filtered nuclei can be used downstream for further analysis.\'\x5D]
    Name the output objects:positives
    Select the object to filter:Nuclei
    Filter using classifier rules or measurements?:Measurements
    Select the filtering method:Limits
    Select the objects that contain the filtered objects:None
    Retain outlines of the identified objects?:No
    Name the outline image:FilteredObjects
    Rules file location:Default Input Folder\x7CNone
    Rules file name:rules.txt
    Measurement count:1
    Additional object count:0
    Select the measurement to filter by:Intensity_MeanIntensity_dye
    Filter using a minimum measurement value?:Yes
    Minimum value:0.25
    Filter using a maximum measurement value?:No
    Maximum value:1

CalculateMath:[module_num:7|svn_version:\'10905\'|variable_revision_number:1|show_window:False|notes:\x5B\'\'\x5D]
    Name the output measurement:PercentPositive
    Operation:Divide
    Select the numerator measurement type:Image
    Select the numerator objects:Nuclei
    Select the numerator measurement:Count_positives
    Multiply the above operand by:1
    Raise the power of above operand by:1
    Select the denominator measurement type:Image
    Select the denominator objects:None
    Select the denominator measurement:Count_Nuclei
    Multiply the above operand by:1
    Raise the power of above operand by:1
    Take log10 of result?:No
    Multiply the result by:1
    Raise the power of result by:1

IdentifySecondaryObjects:[module_num:8|svn_version:\'10826\'|variable_revision_number:7|show_window:False|notes:\x5B\x5D]
    Select the input objects:Nuclei
    Name the objects to be identified:Cells
    Select the method to identify the secondary objects:Distance - N
    Select the input image:DNA
    Select the thresholding method:Otsu Global
    Threshold correction factor:1
    Lower and upper bounds on threshold:0.000000,1.000000
    Approximate fraction of image covered by objects?:0.01
    Number of pixels by which to expand the primary objects:10
    Regularization factor:0.05
    Name the outline image:SecondaryOutlines
    Manual threshold:0.0
    Select binary image:None
    Retain outlines of the identified secondary objects?:No
    Two-class or three-class thresholding?:Two classes
    Minimize the weighted variance or the entropy?:Weighted variance
    Assign pixels in the middle intensity class to the foreground or the background?:Foreground
    Discard secondary objects that touch the edge of the image?:No
    Discard the associated primary objects?:No
    Name the new primary objects:FilteredNuclei
    Retain outlines of the new primary objects?:No
    Name the new primary object outlines:FilteredNucleiOutlines
    Select the measurement to threshold with:None
    Fill holes in identified objects?:Yes

IdentifyTertiaryObjects:[module_num:9|svn_version:\'10300\'|variable_revision_number:1|show_window:False|notes:\x5B\x5D]
    Select the larger identified objects:Cells
    Select the smaller identified objects:Nuclei
    Name the tertiary objects to be identified:Cytoplasm
    Name the outline image:CytoplasmOutlines
    Retain outlines of the tertiary objects?:No

MeasureObjectIntensity:[module_num:10|svn_version:\'10816\'|variable_revision_number:3|show_window:False|notes:\x5B\x5D]
    Hidden:1
    Select an image to measure:dye
    Select objects to measure:Cytoplasm

DisplayDataOnImage:[module_num:11|svn_version:\'10412\'|variable_revision_number:2|show_window:False|notes:\x5B\x5D]
    Display object or image measurements?:Object
    Select the input objects:Cytoplasm
    Measurement to display:Intensity_MeanIntensity_dye
    Select the image on which to display the measurements:dye
    Text color:red
    Name the output image that has the measurements displayed:DisplayImage
    Font size (points):10
    Number of decimals:2
    Image elements to save:Image

ClassifyObjects:[module_num:12|svn_version:\'10720\'|variable_revision_number:2|show_window:False|notes:\x5B\x5D]
    Should each classification decision be based on a single measurement or on the combination of a pair of measurements?:Single measurement
    Hidden:1
    Select the object to be classified:Cytoplasm
    Select the measurement to classify by:Intensity_MedianIntensity_dye
    Select bin spacing:Evenly spaced bins
    Number of bins:10
    Lower threshold:0
    Use a bin for objects below the threshold?:No
    Upper threshold:0.3
    Use a bin for objects above the threshold?:Yes
    Enter the custom thresholds separating the values between bins:0,1
    Give each bin a name?:No
    Enter the bin names separated by commas:None
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Name the output image:ClassifiedNuclei
    Enter the object name:None
    Select the first measurement:None
    Method to select the cutoff:Mean
    Enter the cutoff value:0.5
    Select the second measurement:None
    Method to select the cutoff:Mean
    Enter the cutoff value:0.5
    Use custom names for the bins?:No
    Enter the low-low bin name:low_low
    Enter the low-high bin name:low_high
    Enter the high-low bin name:high_low
    Enter the high-high bin name:high_high
    Retain an image of the objects classified by their measurements, for use later in the pipeline (for example, in SaveImages)?:No
    Enter the image name:None

ExportToSpreadsheet:[module_num:13|svn_version:\'10880\'|variable_revision_number:7|show_window:False|notes:\x5B\x5D]
    Select or enter the column delimiter:Comma (",")
    Prepend the output file name to the data file names?:Yes
    Add image metadata columns to your object data file?:No
    Limit output to a size that is allowed in Excel?:No
    Select the columns of measurements to export?:Yes
    Calculate the per-image mean values for object measurements?:No
    Calculate the per-image median values for object measurements?:No
    Calculate the per-image standard deviation values for object measurements?:No
    Output file location:Default Output Folder\x7CNone
    Create a GenePattern GCT file?:No
    Select source of sample row name:Metadata
    Select the image to use as the identifier:None
    Select the metadata to use as the identifier:None
    Export all measurements, using default file names?:Yes
    Press button to select measurements to export:Nuclei\x7CIntensity_MeanIntensity_dye,Nuclei\x7CIntensity_MeanIntensityEdge_dye
    Data to export:Do not use
    Combine these object measurements with those of the previous object?:No
    File name:DATA.csv
    Use the object name for the file name?:Yes

SaveImages:[module_num:14|svn_version:\'10822\'|variable_revision_number:7|show_window:False|notes:\x5B\x5D]
    Select the type of image to save:Image
    Select the image to save:DisplayImage
    Select the objects to save:None
    Select the module display window to save:None
    Select method for constructing file names:From image filename
    Select image name for file prefix:DNA
    Enter single file name:OrigBlue
    Do you want to add a suffix to the image file name?:Yes
    Text to append to the image name:_intensity
    Select file format to use:bmp
    Output file location:Default Output Folder\x7CNone
    Image bit depth:8
    Overwrite existing files without warning?:No
    Select how often to save:Every cycle
    Rescale the images? :No
    Save as grayscale or color image?:Grayscale
    Select colormap:gray
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:Yes

ExportToDatabase:[module_num:15|svn_version:\'10962\'|variable_revision_number:20|show_window:False|notes:\x5B\x5D]
    Database type:SQLite
    Database name:DefaultDB
    Add a prefix to table names?:No
    Table prefix:Expt_
    SQL file prefix:SQL_
    Output file location:Default Output Folder\x7CNone
    Create a CellProfiler Analyst properties file?:Yes
    Database host:
    Username:
    Password:
    Name the SQLite database file:DefaultDB.db
    Calculate the per-image mean values of object measurements?:Yes
    Calculate the per-image median values of object measurements?:No
    Calculate the per-image standard deviation values of object measurements?:No
    Calculate the per-well mean values of object measurements?:No
    Calculate the per-well median values of object measurements?:No
    Calculate the per-well standard deviation values of object measurements?:No
    Export measurements for all objects to the database?:All
    Select the objects:
    Maximum # of characters in a column name:64
    Create one table per object or a single object table?:Single object table
    Enter an image url prepend if you plan to access your files via http:
    Write image thumbnails directly to the database?:No
    Select the images you want to save thumbnails of:
    Auto-scale thumbnail pixel intensities?:Yes
    Select the plate type:None
    Select the plate metadata:None
    Select the well metadata:None
    Include information for all images, using default values?:Yes
    Hidden:1
    Hidden:1
    Hidden:0
    Select an image to include:None
    Use the image name for the display?:Yes
    Image name:Channel1
    Channel color:red
    Do you want to add group fields?:No
    Enter the name of the group:
    Enter the per-image columns which define the group, separated by commas:ImageNumber, Image_Metadata_Plate, Image_Metadata_Well
    Do you want to add filter fields?:No
    Automatically create a filter for each plate?:No
