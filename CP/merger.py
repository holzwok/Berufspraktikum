# documentation changes by Dominique Sydow

import sys # python standard library
import pickle # python standard library
from os import curdir # python standard library
from os.path import join # python standard library
from PyQt4 import QtGui, QtCore

from gui import Ui_Dialog as Dlg

from merger_methods import setup_db, create_tables, insert_cells, insert_locs #, token_1, token_2
from merger_methods import insert_spots, enhance_spots, enhance_cells, enhance_locs
from merger_methods import scatter_plot_two_modes, plot_and_store_mRNA_frequency
from merger_methods import draw_crosses, annotate_cells, add_median_to_cells, insert_summary
#Konstantin's code
from merger_methods import eval_dtr, merge_tables


lastprefs = "last_preferences.pref"

class MeinDialog(QtGui.QDialog, Dlg): 
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        # QDialog is the base class of dialog windows.
        # A dialog window is a top-level window mostly used for short-term tasks and brief communications with the user.
        
        self.setupUi(self)

        # setup slots (all push buttons)
        self.connect(self.pb_mskpath, QtCore.SIGNAL("clicked()"), self.pb_mskpath_clicked) 
        self.connect(self.pb_outpath, QtCore.SIGNAL("clicked()"), self.pb_outpath_clicked)
        self.connect(self.pb_locpath, QtCore.SIGNAL("clicked()"), self.pb_locpath_clicked)
        self.connect(self.pb_run, QtCore.SIGNAL("clicked()"), self.pb_run_clicked)
        self.connect(self.pb_close, QtCore.SIGNAL("clicked()"), self.end_session)
        
        # try to fill slots with last session's values from preferences file
        try:
            preferences_file = open(lastprefs, 'r')
            preferences_dict = pickle.load(preferences_file)
        except:
            pass
        try:
            mskpath = preferences_dict["mskpath"]
            self.le_mskpath.setText(mskpath)
        except:
            pass
        try:
            outpath = preferences_dict["outpath"]
            self.le_outpath.setText(outpath)
        except:
            pass
        try:
            locpath = preferences_dict["locpath"]
            self.le_locpath.setText(locpath)
        except:
            pass
        try:
            channeltokens = preferences_dict["channeltokens"]
            self.le_channeltoken.setText(channeltokens)
        except:
            pass


    
    def pb_mskpath_clicked(self): 
        # pb_mskpath_clicked opens current directory in file systems manager for user to select a directory
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".") # "Select" - window name  # "." - current directory
        if filename:
            self.le_mskpath.setText(filename)
        #self.close()
        
    def pb_outpath_clicked(self): 
        # pb_outpath_clicked opens current directory in file systems manager for user to select a directory
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            self.le_outpath.setText(filename)
        #self.close()

    def pb_locpath_clicked(self): 
        # pb_locpath_clicked opens current directory in file systems manager for user to select a directory
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            self.le_locpath.setText(filename)
        #self.close()
    

    
    def pb_run_clicked(self):
        # pb_run_clicked start main functions from merger_methods.py if selected

        print "\n... STARTING PROGRAM ...\n"

        locpath = str(self.le_locpath.text())
        mskpath = str(self.le_mskpath.text())
        outpath = str(self.le_outpath.text())

        if mskpath==locpath:
            print "please change maskpath (must not equal locpath), aborting."
            sys.exit()

        channeltokens = str(self.le_channeltoken.text()).strip().split(" ")
        print "you selected: channeltoken(s) =", channeltokens

        # if checkbox "Normalisation per cell (instead of per image folder)" is selected
        # variable declaration: normalisation per cell is called group_by_cell
        if self.cb_group_by_cell.isChecked():
            group_by_cell = True
        else:
            group_by_cell = False
        print "you selected: group_by_cell = ", group_by_cell, "\n"
        
        con = setup_db(path=outpath, dbname='myspots.db')

        #if checkbox "mother-daughter" is selected
        if self.cb_md.isChecked():
        	OP_MODE = "MD"
        else:
        	OP_MODE =""

        # if checkbox "Populate Database" is selected
        if self.cb_populate.isChecked():
            print "POPULATING DATABASE..."
            print "-------------------------------------------------------"
            create_tables(con, OP_MODE)
            insert_cells(con, mskpath, OP_MODE)
            insert_locs(con, locpath, channeltokens)
            insert_spots(con, locpath, mskpath, channeltokens, OP_MODE)
            enhance_spots(con, channeltokens,group_by_cell)
            enhance_cells(con, channeltokens)
            enhance_locs(con)
            insert_summary(con, channeltokens)
            print "done populating database."
            print "-------------------------------------------------------\n"

        # if checkbox "Add medians" is selected
        if self.cb_add_medians.isChecked():
            print "ADDING MEDIANS TO CELLS..."
            print "-------------------------------------------------------"
            add_median_to_cells(con, channeltokens, group_by_cell)
            print "done adding medians to cells."
            print "-------------------------------------------------------\n"

        # if checkbox "Create plots" is selected
        if self.cb_plot.isChecked():
            print "CREATING SCATTER PLOTS..."
            print "-------------------------------------------------------"
            if len(channeltokens)>=2:
                for i in range(0, len(channeltokens)-1):
                    for j in range(i+1, len(channeltokens)):
                        print "creating scatter plot for", channeltokens[i], "vs", channeltokens[j]
                        scatter_plot_two_modes(con, outpath, channeltokens[i], channeltokens[j])
            else:
                print "need at least two channel tokens to create scatter plot"
            
            print "CREATING HISTOGRAMS..."
            print "-------------------------------------------------------"
            for token in channeltokens:
                print "creating frequency plot for", token
                plot_and_store_mRNA_frequency(con, token, outpath)
            print "done creating scatter plots."
            print "-------------------------------------------------------\n"

        # if checkbox "Draw crosses" is selected
        if self.cb_cross.isChecked():
            print "DRAWING CROSSES..."
            print "-------------------------------------------------------"
            draw_crosses(con, locpath, outpath)
            print "done drawing crosses."
            print "-------------------------------------------------------\n"
        
        # if checkbox "Annotate cells" is selected
        if self.cb_annotate.isChecked():
            print "ANNOTATING CELLS..."
            print "-------------------------------------------------------"
            annotate_cells(con, locpath, outpath)
            print "done annotating cells."
            print "-------------------------------------------------------\n"

        #Konstantin's code
	#if table dtrs exist -> merge daughter's and mother's data together
	#has to be done after all procedures
        if eval_dtr(con):
            print "CREATING MERGED RESULTS TABLE"
            print "-------------------------------------------------------"
            merge_tables(con)
            print "done creating table."
            print "-------------------------------------------------------\n"

    def end_session(self):
        # auto-save machine to preferences file
        # auto-save session to session file 
        try:
            # save current preferences to last_preferences.pref
            print "saving preferences to", join(curdir, lastprefs), "...\n"
            preferences_dict = {}
            preferences_dict["mskpath"] = str(self.le_mskpath.text())
            preferences_dict["locpath"] = str(self.le_locpath.text())
            preferences_dict["outpath"] = str(self.le_outpath.text())
            preferences_dict["channeltokens"] = str(self.le_channeltoken.text())
            #preferences_dict["populate"] = self.cb_populate.isChecked()
            #print self.cb_populate.isChecked()

            preferences_file = open(join(curdir, lastprefs), "w")
            pickle.dump(preferences_dict, preferences_file)
            print "... BYE ...\n"
        # This is so that the window closes no matter what
        except:
            pass
        self.close()

############################################################################
############################################################################
############################################################################
# when typing in the terminal:
# $ ipython merger.py
# the following if statement is called
# which calls some functions that are responsible for the whole programm
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv) 
        # Every PyQt4 application must create an application object. 
        # The application object is located in the QtGui module. 
        # The sys.argv parameter is a list of arguments from a command line. 
        # Python scripts can be run from the shell. 
        # It is a way how we can control the startup of our scripts. 

    dialog = MeinDialog() 

    dialog.show() 

    sys.exit(app.exec_())
        # Finally, we enter the mainloop of the application. 
        # The event handling starts from this point. 
        # The mainloop receives events from the window system and dispatches them to the application widgets. 
        # The mainloop ends if we call the exit() method or the main widget is destroyed. 
        # The sys.exit() method ensures a clean exit. 
        # The environment will be informed how the application ended.
