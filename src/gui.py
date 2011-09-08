#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from MainWindow import Ui_notepad

from global_vars import PARAM_DICT
from set_cell_id_parameters import set_parameters


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_notepad()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.button_change_cellid_parameters,QtCore.SIGNAL("clicked()"), self.cell_id_dialog)
        QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
    
    def cell_id_dialog(self):
        cellID1 = self.ui.max_dist_over_waist.toPlainText()
        cellID2 = self.ui.max_split_over_minor_axis.toPlainText()
        cellID3 = self.ui.min_pixels_per_cell.toPlainText()
        cellID4 = self.ui.max_pixels_per_cell.toPlainText()
        
        # If the user does not enter values, the default values specified in global_vars are assumed:
        param_dict = PARAM_DICT

        if cellID1 != "":
            param_dict["max_dist_over_waist"] = float(cellID1)
        if cellID2 != "":
            param_dict["max_split_over_minor_axis"] = float(cellID2)
        if cellID3 != "":
            param_dict["min_pixels_per_cell"] = float(cellID3)
        if cellID4 != "":
            param_dict["max_pixels_per_cell"] = float(cellID4)
            
        set_parameters(param_dict)
        
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
            log_text = "Loading default cell ID parameters for unspecified values.\n"
            log_text += "Setting cell ID parameters to: "+str(param_dict)
            print log_text
            self.ui.log_window.setText(log_text)


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