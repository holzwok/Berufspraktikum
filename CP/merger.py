import sys 
import pickle
from os import curdir
from os.path import join
from PyQt4 import QtGui, QtCore
from gui import Ui_Dialog as Dlg
from merger_methods import setup_db, create_tables, insert_cells, insert_locs, token_1, token_2
from merger_methods import insert_spots, enhance_spots, enhance_cells, enhance_locs
from merger_methods import scatter_plot_two_modes, plot_and_store_mRNA_frequency
from merger_methods import draw_crosses, annotate_cells


lastprefs = "last_preferences.pref"

class MeinDialog(QtGui.QDialog, Dlg): 
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        self.setupUi(self)
        # Slots einrichten 
        self.connect(self.pb_mskpath, QtCore.SIGNAL("clicked()"), self.pb_mskpath_clicked) 
        self.connect(self.pb_outpath, QtCore.SIGNAL("clicked()"), self.pb_outpath_clicked)
        self.connect(self.pb_locpath, QtCore.SIGNAL("clicked()"), self.pb_locpath_clicked)
        self.connect(self.pb_run, QtCore.SIGNAL("clicked()"), self.pb_run_clicked)
        self.connect(self.pb_close, QtCore.SIGNAL("clicked()"), self.end_session)
        try:
            preferences_file = open(lastprefs, 'r')
            preferences_dict = pickle.load(preferences_file)
            mskpath = preferences_dict["mskpath"]
            outpath = preferences_dict["outpath"]
            locpath = preferences_dict["locpath"]
            self.le_mskpath.setText(mskpath)
            self.le_outpath.setText(outpath)
            self.le_locpath.setText(locpath)
            '''
            populate = preferences_dict["populate"]
            print "populate:", populate, type(populate)
            if populate:
                self.pb_populate.setCheckState(True) 
                print "???????????????????????????????"       
                print self.pb_populate.checkState
            '''
        except:
            pass

    def pb_mskpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            self.le_mskpath.setText(filename)
        #self.close()
        
    def pb_outpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            self.le_outpath.setText(filename)
        #self.close()

    def pb_locpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            self.le_locpath.setText(filename)
        #self.close()
        
    def pb_run_clicked(self):
        locpath = str(self.le_locpath.text())
        mskpath = str(self.le_mskpath.text())
        outpath = str(self.le_outpath.text())
        con = setup_db(path=locpath, dbname='myspots.db')
        if self.cb_populate.isChecked():
            print "populating database..."
            create_tables(con)
            insert_cells(con, mskpath)
            insert_locs(con, locpath)
            insert_spots(con, locpath, mskpath)
            enhance_spots(con)
            enhance_cells(con)
            enhance_locs(con)
            print "done populating database."
            print "-------------------------------------------------------"
        if self.cb_plot.isChecked():
            scatter_plot_two_modes(con, outpath)
            plot_and_store_mRNA_frequency(con, token_1, outpath)
            plot_and_store_mRNA_frequency(con, token_2, outpath)
        if self.cb_cross.isChecked():
            draw_crosses(con, locpath, outpath)
        if self.cb_annotate.isChecked():
            annotate_cells(con, outpath)

    def end_session(self):
        # auto-save machine to preferences file
        # auto-save session to session file 
        try:
            # save current preferences to last_preferences.pref
            print "saving preferences to", join(curdir, lastprefs), "..."
            preferences_dict = {}
            preferences_dict["mskpath"] = str(self.le_mskpath.text())
            preferences_dict["locpath"] = str(self.le_locpath.text())
            preferences_dict["outpath"] = str(self.le_outpath.text())
            preferences_dict["populate"] = self.cb_populate.isChecked()
            #print self.cb_populate.isChecked()

            preferences_file = open(join(curdir, lastprefs), "w")
            pickle.dump(preferences_dict, preferences_file)
            print "bye."
        # This is so that the window closes no matter what
        except:
            pass
        self.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv) 
    dialog = MeinDialog() 
    dialog.show() 
    sys.exit(app.exec_())
