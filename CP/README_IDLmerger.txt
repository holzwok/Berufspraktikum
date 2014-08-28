README for IDLmerger
by Dominique Sydow (dominique.sydow@gmail.com)
06.08.2014


1.  What is IDLmerger for? 
##########################
IDLmerger is a python based tool for the quantitative analysis of mRNA fluorescence microscopy images.


2. What does IDLmerger do? 
###########################
1. creating a database (called myspots.db) that contains all the following information:
    - assigning each measured spot to a cell
    - calculating the number of RNA per spot and per cell:
    - therefore normalising the fluorescence intensity of each spot with the median intensity (median intensity refers to one RNA)
      - of all spots per given image folder/experiment OR 
      - of all spots per cell 
    - calculating the number of RNA per spot and per cell without transcription sites 
   (definition for transcription site: 3 or more RNAs per spot)
2. creating a (relative) histogram for amount of RNAs per cell
3. creating a scatter plot comparing RNA amount per cell for 2 channel modes (if more than 2 microscopy channel modes considered in analysis)
4. annotating cells and drawing crosses on spots on bright field images


3. Input for IDLmerger 
#######################
- mask-file   (bright field image processed to image file containing mask cells)
- loc-file    (single molecule fluorescence image processed to text file containing spot position and intensity)
- image-file  (bright field image)

CAUTION: file names
- choose a description for experiment and channel mode and name your files as follows:
  mask-file  <experiment>_<channel mode>.tif
  loc-file   <experiment>_<channel mode>.loc
  image-file <experiment>_<channel mode>_mask_cells.tif
- e.g. experiment is MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1 and channel mode is w3CY5:
  mask-file  MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5_mask_cells.tif
  loc-file   MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.loc
  image-file MAX_20140107_Pcl1_Sic1_A1_0min_50pc_1_w3CY5.tif
- you can use one mask for several channel modes: 
  mode of mask-file name can differ from mode of loc-file and image-file name 
- you will have to give your channel as input - 
  that name has to correspond (at least) partly to the name choosen in your file naming (e.g. CY5 for w3CY5)

CAUTION: directory structure
- path to mask-files must not equal path to loc-files 
- recommended structure: make 3 directories called 
  mask (containing mask-files), output (containing all output) and loc (containing loc-files and image-files)


4. Options of IDLmerger 
########################
- create database
- normalisation per cell or per image folder
- add median per cell to database (only if normalisation per cell is choosen)
- create histogram for amount of RNAs per cell
- create scatter plot for RNA frequency in comparison (if more than 2 channel modes considered in analysis)
- annotate cells and draw crosses on spots on bright field images


5. Software acquirements 
#########################
- python 2.7.6*
- additional packages for python:
   - numpy 1.8.1* (http://www.scipy.org/install.html)
   - matplotlib 1.3.1* (http://matplotlib.org/users/installing.html)
   - pandas 0.13.1* (http://pandas.pydata.org/pandas-docs/stable/install.html)
   - pyqt4 4.8.5* (http://pyqt.sourceforge.net/Docs/PyQt4/installation.html)	
   - pil 2.3.0* (http://www.pythonware.com/products/pil/)
- Sqliteman or SQLite Data Browser (database viewer)

* IDLmerger is tested for displayed versions, may run with others also

IDL merger consists of 3 files, these have to be stored in the same folder:
- merger.py (combining merger_methods.py and gui.py)
- merger_methods.py (containing methods for database, calculation, ...)
- gui.py (containing GUI)


6. How to use IDLmerger? 
#########################
run program on Linux:
- go to directory containing merger.py, merger_methods.py and gui.py
- run in terminal: python merger.py

run program on Windows:
- e.g. with IDLE Python: load merger.py and run

once merger.py is started, a user interface pops up which takes the following input:
- enter path to mask-files ("Mask path..."), path to loc- and image-files ("Loc files path...") and path to output ("Output path...")
- enter channel modes separated by space
- choose functions
- choose normalisation type (per image folder or per cell), default is per image folder
- click "run selected" to run the program
- exit with "save and close" to save your input as preferences





