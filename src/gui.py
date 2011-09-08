#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from MainWindow import Ui_notepad

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_notepad()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.button_change_cellid_parameters,QtCore.SIGNAL("clicked()"), self.file_dialog)
        QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
    
    def file_dialog(self):
        print self.ui.max_dist_over_waist.toPlainText()
        print self.ui.max_split_over_minor_axis.toPlainText()
        print self.ui.min_pixels_per_cell.toPlainText()
        print self.ui.max_pixels_per_cell.toPlainText()
        
        
        # File handling: later
        self.parameter_file_name = 'parameters.txt'
        from os.path import isfile
        if isfile(self.parameter_file_name):
            file = open(self.parameter_file_name, 'w')
            file.write(self.ui.editor_window.toPlainText())
            file.close()
            text = open(self.parameter_file_name).read()
            self.ui.editor_window.setText(text)
            # TODO: getText+...
        else:
            print "not a file:", self.parameter_file_name
            self.ui.log_window.setText("not a file: "+self.parameter_file_name)


    def file_save(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getOpenFileName()
        from os.path import isfile
        if isfile(self.filename):
            file = open(self.filename, 'w')
            file.write(self.ui.editor_window.toPlainText())
            file.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())