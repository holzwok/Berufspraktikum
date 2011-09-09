#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from datetime import date
from PyQt4 import QtCore, QtGui
from MainWindow import Ui_notepad

#from global_vars import PARAM_DICT, SIC_PROCESSED, SIC_RESULTS, SIC_SCRIPTS, SIC_LINKS
from set_cell_id_parameters import set_parameters
from main import * #prepare_structure


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_notepad()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.button_change_cellid_parameters, QtCore.SIGNAL("clicked()"), self.change_cell_id_dialog)
        QtCore.QObject.connect(self.ui.button_load_default_cellid_parameters, QtCore.SIGNAL("clicked()"), self.load_cell_id_dialog)

        QtCore.QObject.connect(self.ui.working_directory, QtCore.SIGNAL("clicked()"), self.working_directory_dialog)
        QtCore.QObject.connect(self.ui.cell_id_executable, QtCore.SIGNAL("clicked()"), self.cell_id_executable_dialog)
        QtCore.QObject.connect(self.ui.fiji_executable, QtCore.SIGNAL("clicked()"), self.fiji_executable_dialog)
        QtCore.QObject.connect(self.ui.spottyR_file, QtCore.SIGNAL("clicked()"), self.spottyR_file_dialog)
        QtCore.QObject.connect(self.ui.pb_save_preferences, QtCore.SIGNAL("clicked()"), self.save_preferences_dialog)
        QtCore.QObject.connect(self.ui.pb_load_preferences, QtCore.SIGNAL("clicked()"), self.load_preferences_dialog)

        QtCore.QObject.connect(self.ui.pb_images_directory, QtCore.SIGNAL("clicked()"), self.images_directory_dialog)
        QtCore.QObject.connect(self.ui.pb_save_session, QtCore.SIGNAL("clicked()"), self.save_session_dialog)
        QtCore.QObject.connect(self.ui.pb_apply_session, QtCore.SIGNAL("clicked()"), self.apply_session_dialog)
        QtCore.QObject.connect(self.ui.pb_load_session, QtCore.SIGNAL("clicked()"), self.load_session_dialog)

        QtCore.QObject.connect(self.ui.prepare_structure, QtCore.SIGNAL("clicked()"), self.prepare_structure)

        QtCore.QObject.connect(self.ui.button_save, QtCore.SIGNAL("clicked()"), self.file_save)
    
    def change_cell_id_dialog(self):
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
        
        log_text = "Loading default cell ID parameters for unspecified values.\n"
        log_text += "Setting cell ID parameters to: "+str(param_dict)
        print log_text
        self.ui.log_window.setText(log_text)

    def load_cell_id_dialog(self):
        print "A button was clicked"
        # TODO: load

    def working_directory_dialog(self):
        workingdir = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".", options = QtGui.QFileDialog.DontResolveSymlinks)
        if workingdir:
            self.ui.lineEditworking_directory.setText(workingdir)
        global SIC_ROOT 
        SIC_ROOT = str(workingdir) 

    def cell_id_executable_dialog(self):
        cellidexe = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        if cellidexe:
            self.ui.lineEditcell_id_executable.setText(cellidexe)
        global SIC_CELLID 
        SIC_CELLID = str(cellidexe)

    def fiji_executable_dialog(self):
        fijiexe = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        if fijiexe:
            self.ui.lineEditfiji_executable.setText(fijiexe)
        global SIC_FIJI 
        SIC_FIJI = str(fijiexe)

    def spottyR_file_dialog(self):
        spottyfile = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        if spottyfile:
            self.ui.lineEditspottyR_file.setText(spottyfile)
        global SIC_SPOTTY 
        SIC_SPOTTY = str(spottyfile)

    def save_preferences_dialog(self):
        preferences_dict = {}
        preferences_dict["workingdir"] = SIC_ROOT
        preferences_dict["cellidexe"] = SIC_CELLID
        preferences_dict["fijiexe"] = SIC_FIJI
        preferences_dict["spottyfile"] = SIC_SPOTTY
        defaultFileName = "Preferences_"+str(date.today())+".pref"
        filename = str(QtGui.QFileDialog.getSaveFileName(None, QtCore.QString("Save preferences..."), defaultFileName));
        preferences_file = open(filename, 'w')
        pickle.dump(preferences_dict, preferences_file)

    def load_preferences_dialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        preferences_file = open(filename, 'r')
        preferences_dict = pickle.load(preferences_file)
        global SIC_ROOT 
        SIC_ROOT = preferences_dict["workingdir"]
        global SIC_CELLID 
        SIC_CELLID = preferences_dict["cellidexe"] 
        global SIC_FIJI 
        SIC_FIJI = preferences_dict["fijiexe"]
        global SIC_SPOTTY 
        SIC_SPOTTY = preferences_dict["spottyfile"]
        self.ui.lineEditworking_directory.setText(SIC_ROOT)
        self.ui.lineEditcell_id_executable.setText(SIC_CELLID)
        self.ui.lineEditfiji_executable.setText(SIC_FIJI)
        self.ui.lineEditspottyR_file.setText(SIC_SPOTTY)
         
    def images_directory_dialog(self):
        imagesdir = QtGui.QFileDialog.getExistingDirectory(self, "Select", ".", options = QtGui.QFileDialog.DontResolveSymlinks)
        if imagesdir:
            self.ui.le_images_directory.setText(imagesdir)
        global SIC_ORIG 
        SIC_ORIG = str(imagesdir) 

    def save_session_dialog(self):
        global NIBA_ID 
        NIBA_ID = str(self.ui.le_niba_id.text())
        global DIC_ID 
        DIC_ID = str(self.ui.le_dic_id.text())
        session_dict = {}
        session_dict["imagesdir"] = SIC_ORIG
        session_dict["niba_id"] = NIBA_ID
        session_dict["dic_id"] = DIC_ID
        defaultFileName = "Session_"+str(date.today())+".ssn"
        filename = str(QtGui.QFileDialog.getSaveFileName(None, QtCore.QString("Save session..."), defaultFileName));
        session_file = open(filename, 'w')
        pickle.dump(session_dict, session_file)

    def apply_session_dialog(self):
        global SIC_ORIG 
        SIC_ORIG = str(self.ui.le_images_directory.text()) 
        global NIBA_ID 
        NIBA_ID = str(self.ui.le_niba_id.text())
        global DIC_ID 
        DIC_ID = str(self.ui.le_dic_id.text())
    
    def load_session_dialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        session_file = open(filename, 'r')
        session_dict = pickle.load(session_file)
        global SIC_ORIG 
        SIC_ORIG = session_dict["imagesdir"]
        global NIBA_ID 
        NIBA_ID = session_dict["niba_id"] 
        global DIC_ID 
        DIC_ID = session_dict["dic_id"]
        self.ui.le_images_directory.setText(SIC_ORIG)
        self.ui.le_niba_id.setText(NIBA_ID)
        self.ui.le_dic_id.setText(DIC_ID)
    
    def prepare_structure(self):
        prepare_structure(path=SIC_ROOT,
                      skip=[SIC_ORIG, SIC_SCRIPTS, "orig", "orig1", "orig2", "orig3", "orig4", "orig5", "orig6"],
                      create_dirs=[SIC_PROCESSED, SIC_RESULTS, SIC_LINKS],
                      check_for=[join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT),
                        join(SIC_ROOT, SIC_ORIG)])

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