import sys 
from PyQt4 import QtGui, QtCore
from gui import Ui_Dialog as Dlg

class MeinDialog(QtGui.QDialog, Dlg): 
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        self.setupUi(self)
        # Slots einrichten 
        self.connect(self.pb_mskpath, QtCore.SIGNAL("clicked()"), self.pb_mskpath_clicked) 
        self.connect(self.pb_outpath, QtCore.SIGNAL("clicked()"), self.pb_outpath_clicked)
        self.connect(self.pb_locpath, QtCore.SIGNAL("clicked()"), self.pb_locpath_clicked)

    def pb_mskpath_clicked(self): 
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".")
        if filename:
            #preferences_file = open(filename, 'r')
            self.le_mskpath.setText(filename)
        #self.close()
        
    def pb_outpath_clicked(self): 
        print "Adresse: %s" % self.le_outpath.text() 

        '''
        if self.agb.checkState(): 
            print "AGBs akzeptiert" 
        if self.newsletter.checkState(): 
            print "Katalog bestellt" 
        '''
        self.close()

    def pb_locpath_clicked(self): 
        print self.le_locpath.text()
        self.close()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv) 
    dialog = MeinDialog() 
    dialog.show() 
    sys.exit(app.exec_())