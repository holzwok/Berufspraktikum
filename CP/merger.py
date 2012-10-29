import sys 
import pickle
from os import curdir
from os.path import join
from PyQt4 import QtGui, QtCore
from gui import Ui_Dialog as Dlg

lastprefs = "last_preferences.pref"

class MeinDialog(QtGui.QDialog, Dlg): 
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        self.setupUi(self)
        # Slots einrichten 
        self.connect(self.pb_mskpath, QtCore.SIGNAL("clicked()"), self.pb_mskpath_clicked) 
        self.connect(self.pb_outpath, QtCore.SIGNAL("clicked()"), self.pb_outpath_clicked)
        self.connect(self.pb_locpath, QtCore.SIGNAL("clicked()"), self.pb_locpath_clicked)
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
        except:
            pass

    def pb_mskpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            #preferences_file = open(filename, 'r')
            self.le_mskpath.setText(filename)
        #self.close()
        
    def pb_outpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            #preferences_file = open(filename, 'r')
            self.le_outpath.setText(filename)
        #self.close()

    def pb_locpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            #preferences_file = open(filename, 'r')
            self.le_locpath.setText(filename)
        #self.close()
        
    def end_session(self):
        # auto-save machine to preferences file
        # auto-save session to session file 
        try:
            # save current preferences to last_preferences.pref
            preferences_dict = {}
            preferences_dict["mskpath"] = str(self.le_mskpath.text())
            preferences_dict["locpath"] = str(self.le_locpath.text())
            preferences_dict["outpath"] = str(self.le_outpath.text())
            preferences_file = open(join(curdir, lastprefs), "w")
            pickle.dump(preferences_dict, preferences_file)
            print "saving preferences to", join(curdir, lastprefs)
        # This is so that the window closes no matter what
        except:
            pass
        self.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv) 
    dialog = MeinDialog() 
    dialog.show() 
    sys.exit(app.exec_())