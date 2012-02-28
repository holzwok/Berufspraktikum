#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import pylab as pl
from datetime import date
from os.path import join
from PyQt4 import QtCore, QtGui

from set_cell_id_parameters import set_parameters, load_parameters
from main import prepare_structure, replace_decimal_separators,\
    run_fiji_standard_mode_select_quarter_slices, copy_DIC_files_to_processed
from main import copy_NIBA_files_to_processed, link_DIC_files_to_processed,\
    run_fiji_standard_mode, create_map_image_data, create_symlinks,\
    prepare_b_and_f_single_files, run_cellid,\
    load_fiji_results_and_create_mappings, create_mappings_filename2pixel_list,\
    load_cellid_files_and_create_mappings_from_bounds, cluster_with_spotty,\
    aggregate_spots, make_plots, rename_dirs
from MainWindow import Ui_notepad
from global_vars import SIC_SCRIPTS, SIC_PROCESSED, SIC_RESULTS,\
    FIJI_STANDARD_SCRIPT, PARAM_DICT, SIC_FILE_CORRESPONDANCE, SIC_BF_LISTFILE,\
    SIC_F_LISTFILE, SIC_CELLID_PARAMS, GMAX, SIC_DATA_PICKLE , FIJI_SLICE_SCRIPT
from plot_functions import histogram_intensities, scatterplot_intensities,\
    spots_per_cell_distribution,\
    plot_time2ratio_between_one_dot_number_and_cell_number,\
    draw_spots_for_session


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

        QtCore.QObject.connect(self.ui.prepare_structure, QtCore.SIGNAL("clicked()"), self.prepare_files_and_folder_structure)
        QtCore.QObject.connect(self.ui.pb_run_fiji, QtCore.SIGNAL("clicked()"), self.run_fiji)
        QtCore.QObject.connect(self.ui.pb_run_cell_id, QtCore.SIGNAL("clicked()"), self.run_cell_id)
        QtCore.QObject.connect(self.ui.pb_run_spotty, QtCore.SIGNAL("clicked()"), self.run_spotty)
        QtCore.QObject.connect(self.ui.pb_aggregate_and_plot, QtCore.SIGNAL("clicked()"), self.aggregate_and_plot)
        QtCore.QObject.connect(self.ui.pb_run_all_steps, QtCore.SIGNAL("clicked()"), self.run_all_steps)
        QtCore.QObject.connect(self.ui.pb_mark_detected_spots, QtCore.SIGNAL("clicked()"), self.mark_detected_spots)
        
        QtCore.QObject.connect(self.ui.pushButton_2, QtCore.SIGNAL("clicked()"), self.end_session)
        
        # load last preferences and last session into GUI if possible
        l = os.listdir(os.curdir)
        lastprefs = "last_preferences.pref"
        lastsession = "last_session.ssn"
        if lastprefs in l:
            preferences_file = open(lastprefs, 'r')
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
        if lastsession in l:
            session_file = open(lastsession, 'r')
            session_dict = pickle.load(session_file)
            global SIC_ORIG 
            SIC_ORIG_PATH = session_dict["imagesdir"]
            SIC_ORIG = SIC_ORIG_PATH.split(r"/")[-1]
            global NIBA_ID 
            NIBA_ID = session_dict["niba_id"] 
            global DIC_ID 
            DIC_ID = session_dict["dic_id"]
            self.ui.le_images_directory.setText(SIC_ORIG_PATH)
            self.ui.le_niba_id.setText(NIBA_ID)
            self.ui.le_dic_id.setText(DIC_ID)
        
        self.ui.log_window.setText("Welcome to Spotalyser 0.9!")

    
    def change_cell_id_dialog(self):
        cellID1 = self.ui.lineEdit_max_dist_over_waist.text()
        cellID2 = self.ui.lineEdit_max_split_over_minor_axis.text()
        cellID3 = self.ui.lineEdit_min_pixels_per_cell.text()
        cellID4 = self.ui.lineEdit_max_pixels_per_cell.text()
        cellID5 = self.ui.lineEdit_background_reject_factor.text()
        cellID6 = self.ui.lineEdit_tracking_comparison.text()
        
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
        if cellID5 != "":
            param_dict["background_reject_factor"] = float(cellID5)
        if cellID6 != "":
            param_dict["tracking_comparison"] = float(cellID6)
            
        param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)
        set_parameters(param_dict, param_file)
        
        log_text = "Loading default cell ID parameters for unspecified values.\n"
        log_text += "Setting cell ID parameters to: "+str(param_dict)
        print log_text
        self.ui.log_window.setText(log_text)

    def load_cell_id_dialog(self):
        global SIC_ROOT
        global SIC_SCRIPTS
        global SIC_CELLID_PARAMS

        print "param_dict =", load_parameters(param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS))
        param_dict = load_parameters(param_file=join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS))
        self.ui.lineEdit_max_dist_over_waist.setText(str(param_dict["max_dist_over_waist"]))
        self.ui.lineEdit_max_split_over_minor_axis.setText(str(param_dict["max_split_over_minor_axis"]))
        self.ui.lineEdit_min_pixels_per_cell.setText(str(param_dict["min_pixels_per_cell"]))
        self.ui.lineEdit_max_pixels_per_cell.setText(str(param_dict["max_pixels_per_cell"]))
        self.ui.lineEdit_background_reject_factor.setText(str(param_dict["background_reject_factor"]))
        self.ui.lineEdit_tracking_comparison.setText(str(param_dict["tracking_comparison"]))
        

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
        global SIC_ROOT 
        global SIC_CELLID 
        global SIC_FIJI 
        global SIC_SPOTTY 
        preferences_dict = {}
        preferences_dict["workingdir"] = SIC_ROOT
        preferences_dict["cellidexe"] = SIC_CELLID
        preferences_dict["fijiexe"] = SIC_FIJI
        preferences_dict["spottyfile"] = SIC_SPOTTY
        defaultFileName = "Preferences_"+str(date.today())+".pref"
        filename = str(QtGui.QFileDialog.getSaveFileName(None, QtCore.QString("Save preferences..."), defaultFileName))
        if filename:
            preferences_file = open(filename, 'w')
            pickle.dump(preferences_dict, preferences_file)

    def load_preferences_dialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        if filename:
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
        SIC_ORIG_PATH = str(imagesdir)
        SIC_ORIG = SIC_ORIG_PATH.split(r"/")[-1]

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
        if filename:
            session_file = open(filename, 'w')
            pickle.dump(session_dict, session_file)

    def apply_session_dialog(self):
        global SIC_ORIG 
        SIC_ORIG_PATH = str(self.ui.le_images_directory.text()) 
        SIC_ORIG = SIC_ORIG_PATH.split(r"/")[-1]
        global NIBA_ID 
        NIBA_ID = str(self.ui.le_niba_id.text())
        global DIC_ID 
        DIC_ID = str(self.ui.le_dic_id.text())
    
    def load_session_dialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Select", ".")
        if filename:
            session_file = open(filename, 'r')
            session_dict = pickle.load(session_file)
            global SIC_ORIG 
            SIC_ORIG_PATH = session_dict["imagesdir"]
            SIC_ORIG = SIC_ORIG_PATH.split(r"/")[-1]
            global NIBA_ID 
            NIBA_ID = session_dict["niba_id"] 
            global DIC_ID 
            DIC_ID = session_dict["dic_id"]
            self.ui.le_images_directory.setText(SIC_ORIG_PATH)
            self.ui.le_niba_id.setText(NIBA_ID)
            self.ui.le_dic_id.setText(DIC_ID)
    
    def prepare_files_and_folder_structure(self):
        global SIC_ROOT 
        global SIC_FIJI 
        SIC_ROOT = str(self.ui.lineEditworking_directory.text()) 
        SIC_FIJI = str(self.ui.lineEditfiji_executable.text())
        fiji = SIC_FIJI
        path = SIC_ROOT
        skip = [SIC_ORIG, SIC_SCRIPTS, "orig", "orig1", "orig2", "orig3", "orig4", "orig5", "orig6"]
        create_dirs = [SIC_PROCESSED, SIC_RESULTS]
        #check_for = [join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT), join(SIC_ROOT, SIC_ORIG)]
        check_for = [FIJI_STANDARD_SCRIPT, FIJI_SLICE_SCRIPT, join(SIC_ROOT, SIC_ORIG)] # Should check fiji scripts in eclipse workspace
        prepare_structure(path, skip, create_dirs, check_for, fiji)
        copy_NIBA_files_to_processed(join(SIC_ROOT, SIC_ORIG), join(SIC_ROOT, SIC_PROCESSED), NIBA_ID)
        link_DIC_files_to_processed(join(SIC_ROOT, SIC_ORIG), join(SIC_ROOT, SIC_PROCESSED), DIC_ID)
        #copy_DIC_files_to_processed(join(SIC_ROOT, SIC_ORIG), join(SIC_ROOT, SIC_PROCESSED), DIC_ID)

    def run_fiji(self):
        global SIC_ROOT 
        global SIC_PROCESSED 
        global SIC_FIJI 
        fiji = SIC_FIJI
        path = join(SIC_ROOT, SIC_PROCESSED)
        #script_filename = join(SIC_ROOT, SIC_SCRIPTS, FIJI_STANDARD_SCRIPT)
        #slice_filename = join(SIC_ROOT, SIC_SCRIPTS, FIJI_SLICE_SCRIPT)
        script_filename = join(os.getcwd(), FIJI_STANDARD_SCRIPT)
        slice_filename = join(os.getcwd(), FIJI_SLICE_SCRIPT)
        niba = NIBA_ID
        dic = DIC_ID
        #run_fiji_standard_mode(path, script_filename, niba, fiji)
        run_fiji_standard_mode_select_quarter_slices(path, script_filename, slice_filename, niba, dic, fiji)
        
    def run_cell_id(self):
        global SIC_ROOT 
        global SIC_PROCESSED 
        global SIC_LINKS 
        global SIC_FILE_CORRESPONDANCE 
        global NIBA_ID 
        global DIC_ID 
        global SIC_CELLID 
        global SIC_CELLID_PARAMS 
        filename = join(SIC_ROOT, SIC_PROCESSED, SIC_FILE_CORRESPONDANCE)
        path = join(SIC_ROOT, SIC_PROCESSED)
        niba = NIBA_ID
        dic = DIC_ID
        options_fn = join(SIC_ROOT, SIC_SCRIPTS, SIC_CELLID_PARAMS)
        output_prefix = join(SIC_ROOT, SIC_PROCESSED)
        niba2dic, dic2niba, o2n = create_map_image_data(filename, path, niba, dic)
        sourcepath = join(SIC_ROOT, SIC_PROCESSED)
        targetpath = join(SIC_ROOT, SIC_PROCESSED)
        create_symlinks(o2n, sourcepath, targetpath)
        prepare_b_and_f_single_files(niba2dic, o2n, path)
        run_cellid(path, SIC_CELLID, join(SIC_ROOT, SIC_PROCESSED, SIC_BF_LISTFILE),
               join(SIC_ROOT, SIC_PROCESSED, SIC_F_LISTFILE),
               options_fn,
               output_prefix)
        global d
        d = {
            "niba2dic" : niba2dic,
            "dic2niba" : dic2niba,
            "o2n" : o2n,
        }

    def run_spotty(self):
        global SIC_ROOT 
        global SIC_PROCESSED 
        global SIC_LINKS 
        global SIC_SPOTTY 
        SIC_ROOT = str(self.ui.lineEditworking_directory.text()) 
        path = join(SIC_ROOT, SIC_PROCESSED)
        #cellid_results_path = join(SIC_ROOT, SIC_PROCESSED)
        headers, data = load_fiji_results_and_create_mappings(path)
        filename2pixel_list = create_mappings_filename2pixel_list((headers, data), path)
        global d
        o2n = d["o2n"]
        filename2cells, filename2hist, filename2cell_number = load_cellid_files_and_create_mappings_from_bounds(filename2pixel_list, o2n, path)
        spotty=SIC_SPOTTY
        cluster_with_spotty(path, spotty, GMAX) # TODO: GMAX from GUI
        d["filename2pixel_list"] = filename2pixel_list
        d["headers"] = headers
        d["data"] = data
        d["filename2cells"] = filename2cells
        d["filename2hist"] = filename2hist
        d["filename2cell_number"] = filename2cell_number
        
    def aggregate_and_plot(self):
        global SIC_ORIG
        global SIC_ROOT 
        global SIC_PROCESSED 
        global SIC_RESULTS 
        global SIC_DATA_PICKLE 
        path = join(SIC_ROOT, SIC_PROCESSED)
        global d

        try:
            d
        except NameError:
            d = pickle.load(file(join(SIC_ROOT, SIC_PROCESSED, SIC_DATA_PICKLE)))
            
        o2n = d["o2n"]
        spots = aggregate_spots(o2n, path)
        d["spots"] = spots
        pickle.dump(d, file(join(SIC_ROOT, SIC_RESULTS, SIC_DATA_PICKLE), "w"))
        histogram_intensities(spots, path)
        scatterplot_intensities(spots, path)
        spots_per_cell_distribution(spots, path)
        rename_dirs(SIC_ORIG, path)
        pl.show()

    def run_all_steps(self):
        global SIC_ROOT 
        global SIC_PROCESSED
        
        self.prepare_files_and_folder_structure()
        self.run_fiji()
        self.run_cell_id()
        self.run_spotty()
        self.aggregate_and_plot()
        #FIXME: why does this not work under Windows?
        if not self.ui.cb_decimal_separator.isChecked(): # then we want to replace . by ,
            path=join(SIC_ROOT, SIC_PROCESSED)
            print "replacing decimal separators on path =", path
            replace_decimal_separators(path)
        pl.show()

    def file_save(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getOpenFileName()
        from os.path import isfile
        if isfile(self.filename):
            file = open(self.filename, 'w')
            file.write(self.ui.editor_window.toPlainText())
            file.close()
        
    def mark_detected_spots(self):
        global SIC_ROOT 
        global SIC_PROCESSED
        SIC_ROOT = str(self.ui.lineEditworking_directory.text()) 
        path = join(SIC_ROOT, SIC_PROCESSED)
        
        print SIC_ROOT
        
        draw_spots_for_session(path=join(SIC_ROOT, SIC_PROCESSED), infofile="all_spots.xls")        # FIXME: load

    def end_session(self):
        # auto-save machine to preferences file
        # auto-save session to session file 
        global SIC_ROOT 
        global SIC_ORIG 
        global SIC_SCRIPTS 
        global SIC_CELLID 
        global SIC_FIJI 
        global SIC_SPOTTY 
        global NIBA_ID 
        NIBA_ID = str(self.ui.le_niba_id.text())
        global DIC_ID 
        DIC_ID = str(self.ui.le_dic_id.text())
        try:
            # save current preferences to last_preferences.pref
            preferences_dict = {}
            preferences_dict["workingdir"] = str(self.ui.lineEditworking_directory.text())
            preferences_dict["cellidexe"] = str(self.ui.lineEditcell_id_executable.text())
            preferences_dict["fijiexe"] = str(self.ui.lineEditfiji_executable.text())
            preferences_dict["spottyfile"] = str(self.ui.lineEditspottyR_file.text())
            preferences_file = open(join(os.curdir, "last_preferences.pref"), "w")
            pickle.dump(preferences_dict, preferences_file)

            # save current session to last_session.ssn
            session_dict = {}
            session_dict["imagesdir"] = str(self.ui.le_images_directory.text())
            session_dict["niba_id"] = str(self.ui.le_niba_id.text())
            session_dict["dic_id"] = str(self.ui.le_dic_id.text())
            session_file = open(join(os.curdir, "last_session.ssn"), 'w')
            pickle.dump(session_dict, session_file)

        # This is so that the window closes no matter which variables are set
        except:
            pass
        self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
    