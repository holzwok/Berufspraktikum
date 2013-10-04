CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:11710

LoadImages:[module_num:1|svn_version:\'11587\'|variable_revision_number:11|show_window:True|notes:\x5B\'x\'\x5D]
    File type to be loaded:individual images
    File selection method:Text-Exact match
    Number of images in each group?:3
    Type the text that the excluded images have in common:Do not use
    Analyze all subfolders within the selected folder?:None
    Input image file location:Default Input Folder\x7C.
    Check image sets for missing or duplicate files?:No
    Group images by metadata?:No
    Exclude certain files?:No
    Specify metadata fields to group by:
    Select subfolders to analyze:
    Image count:2
    Text that these images have in common (case-sensitive):C001
    Position of this image in each group:d0.tif
    Extract metadata from where?:File name
    Regular expression that finds metadata in the file name:.*C001.*
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
    Position of this image in each group:2
    Extract metadata from where?:File name
    Regular expression that finds metadata in the file name:.*C002.*
    Type the regular expression that finds metadata in the subfolder path:.*\x5B\\\\/\x5D(?P<Date>.*)\x5B\\\\/\x5D(?P<Run>.*)$
    Channel count:1
    Group the movie frames?:No
    Grouping method:Interleaved
    Number of channels per group:3
    Load the input as images or objects?:Images
    Name this loaded image:dye
    Name this loaded object:Nuclei
    Retain outlines of loaded objects?:No
    Name the outline image:LoadedImageOutlines
    Channel number:1
    Rescale intensities?:Yes

MakeProjection:[module_num:2|svn_version:\'10826\'|variable_revision_number:2|show_window:True|notes:\x5B\x5D]
    Select the input image:DNA
    Type of projection:Sum
    Name the output image:projection_DNA
    Frequency:6.0

MakeProjection:[module_num:3|svn_version:\'10826\'|variable_revision_number:2|show_window:True|notes:\x5B\x5D]
    Select the input image:dye
    Type of projection:Sum
    Name the output image:projection_dye
    Frequency:6.0

SaveImages:[module_num:4|svn_version:\'10822\'|variable_revision_number:7|show_window:True|notes:\x5B\'\'\x5D]
    Select the type of image to save:Image
    Select the image to save:projection_DNA
    Select the objects to save:None
    Select the module display window to save:OutlinedNuc
    Select method for constructing file names:Single name
    Select image name for file prefix:DNA
    Enter single file name:projection_DNA
    Do you want to add a suffix to the image file name?:Yes
    Text to append to the image name:_projection
    Select file format to use:tif
    Output file location:Default Output Folder\x7CNone
    Image bit depth:16
    Overwrite existing files without warning?:Yes
    Select how often to save:Last cycle
    Rescale the images? :Yes
    Save as grayscale or color image?:Grayscale
    Select colormap:Default
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:No

SaveImages:[module_num:5|svn_version:\'10822\'|variable_revision_number:7|show_window:True|notes:\x5B\x5D]
    Select the type of image to save:Image
    Select the image to save:projection_dye
    Select the objects to save:None
    Select the module display window to save:OutlinedNuc
    Select method for constructing file names:Single name
    Select image name for file prefix:DNA
    Enter single file name:projection_dye
    Do you want to add a suffix to the image file name?:Yes
    Text to append to the image name:_projection
    Select file format to use:tif
    Output file location:Default Output Folder\x7CNone
    Image bit depth:16
    Overwrite existing files without warning?:Yes
    Select how often to save:Last cycle
    Rescale the images? :Yes
    Save as grayscale or color image?:Grayscale
    Select colormap:Default
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:No
