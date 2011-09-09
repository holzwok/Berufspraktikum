# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Fri Sep  9 13:37:13 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_notepad(object):
    def setupUi(self, notepad):
        notepad.setObjectName(_fromUtf8("notepad"))
        notepad.resize(838, 907)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../../../../../../martin/Downloads/9790.jpg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        notepad.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(notepad)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(400, 820, 261, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.button_save = QtGui.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(400, 780, 261, 27))
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(500, 20, 261, 271))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.button_change_cellid_parameters = QtGui.QPushButton(self.groupBox)
        self.button_change_cellid_parameters.setGeometry(QtCore.QRect(10, 200, 241, 27))
        self.button_change_cellid_parameters.setObjectName(_fromUtf8("button_change_cellid_parameters"))
        self.layoutWidget = QtGui.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 180, 161))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.button_load_default_cellid_parameters = QtGui.QPushButton(self.groupBox)
        self.button_load_default_cellid_parameters.setGeometry(QtCore.QRect(10, 230, 241, 27))
        self.button_load_default_cellid_parameters.setObjectName(_fromUtf8("button_load_default_cellid_parameters"))
        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(200, 30, 41, 161))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.max_dist_over_waist = QtGui.QTextEdit(self.widget)
        self.max_dist_over_waist.setObjectName(_fromUtf8("max_dist_over_waist"))
        self.verticalLayout_4.addWidget(self.max_dist_over_waist)
        self.max_split_over_minor_axis = QtGui.QTextEdit(self.widget)
        self.max_split_over_minor_axis.setObjectName(_fromUtf8("max_split_over_minor_axis"))
        self.verticalLayout_4.addWidget(self.max_split_over_minor_axis)
        self.min_pixels_per_cell = QtGui.QTextEdit(self.widget)
        self.min_pixels_per_cell.setObjectName(_fromUtf8("min_pixels_per_cell"))
        self.verticalLayout_4.addWidget(self.min_pixels_per_cell)
        self.max_pixels_per_cell = QtGui.QTextEdit(self.widget)
        self.max_pixels_per_cell.setObjectName(_fromUtf8("max_pixels_per_cell"))
        self.verticalLayout_4.addWidget(self.max_pixels_per_cell)
        self.log_window = QtGui.QTextEdit(self.centralwidget)
        self.log_window.setGeometry(QtCore.QRect(10, 610, 651, 161))
        self.log_window.setObjectName(_fromUtf8("log_window"))
        self.prepare_structure = QtGui.QPushButton(self.centralwidget)
        self.prepare_structure.setGeometry(QtCore.QRect(540, 340, 221, 27))
        self.prepare_structure.setObjectName(_fromUtf8("prepare_structure"))
        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(19, 20, 441, 271))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.layoutWidget1 = QtGui.QWidget(self.groupBox_2)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 30, 154, 161))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.working_directory = QtGui.QPushButton(self.layoutWidget1)
        self.working_directory.setObjectName(_fromUtf8("working_directory"))
        self.verticalLayout_2.addWidget(self.working_directory)
        self.cell_id_executable = QtGui.QPushButton(self.layoutWidget1)
        self.cell_id_executable.setObjectName(_fromUtf8("cell_id_executable"))
        self.verticalLayout_2.addWidget(self.cell_id_executable)
        self.fiji_executable = QtGui.QPushButton(self.layoutWidget1)
        self.fiji_executable.setObjectName(_fromUtf8("fiji_executable"))
        self.verticalLayout_2.addWidget(self.fiji_executable)
        self.spottyR_file = QtGui.QPushButton(self.layoutWidget1)
        self.spottyR_file.setObjectName(_fromUtf8("spottyR_file"))
        self.verticalLayout_2.addWidget(self.spottyR_file)
        self.layoutWidget2 = QtGui.QWidget(self.groupBox_2)
        self.layoutWidget2.setGeometry(QtCore.QRect(170, 30, 251, 161))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lineEditworking_directory = QtGui.QLineEdit(self.layoutWidget2)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEditworking_directory.setFont(font)
        self.lineEditworking_directory.setObjectName(_fromUtf8("lineEditworking_directory"))
        self.verticalLayout_3.addWidget(self.lineEditworking_directory)
        self.lineEditcell_id_executable = QtGui.QLineEdit(self.layoutWidget2)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEditcell_id_executable.setFont(font)
        self.lineEditcell_id_executable.setObjectName(_fromUtf8("lineEditcell_id_executable"))
        self.verticalLayout_3.addWidget(self.lineEditcell_id_executable)
        self.lineEditfiji_executable = QtGui.QLineEdit(self.layoutWidget2)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEditfiji_executable.setFont(font)
        self.lineEditfiji_executable.setObjectName(_fromUtf8("lineEditfiji_executable"))
        self.verticalLayout_3.addWidget(self.lineEditfiji_executable)
        self.lineEditspottyR_file = QtGui.QLineEdit(self.layoutWidget2)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEditspottyR_file.setFont(font)
        self.lineEditspottyR_file.setObjectName(_fromUtf8("lineEditspottyR_file"))
        self.verticalLayout_3.addWidget(self.lineEditspottyR_file)
        self.pb_save_preferences = QtGui.QPushButton(self.groupBox_2)
        self.pb_save_preferences.setGeometry(QtCore.QRect(10, 200, 411, 27))
        self.pb_save_preferences.setObjectName(_fromUtf8("pb_save_preferences"))
        self.pb_load_preferences = QtGui.QPushButton(self.groupBox_2)
        self.pb_load_preferences.setGeometry(QtCore.QRect(10, 230, 411, 27))
        self.pb_load_preferences.setObjectName(_fromUtf8("pb_load_preferences"))
        self.groupBox_3 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 290, 431, 221))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.widget1 = QtGui.QWidget(self.groupBox_3)
        self.widget1.setGeometry(QtCore.QRect(0, 30, 151, 111))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.pb_images_directory = QtGui.QPushButton(self.widget1)
        self.pb_images_directory.setObjectName(_fromUtf8("pb_images_directory"))
        self.verticalLayout_5.addWidget(self.pb_images_directory)
        self.label_5 = QtGui.QLabel(self.widget1)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_5.addWidget(self.label_5)
        self.label_6 = QtGui.QLabel(self.widget1)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_5.addWidget(self.label_6)
        self.widget2 = QtGui.QWidget(self.groupBox_3)
        self.widget2.setGeometry(QtCore.QRect(160, 30, 261, 111))
        self.widget2.setObjectName(_fromUtf8("widget2"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.widget2)
        self.verticalLayout_6.setMargin(0)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.le_images_directory = QtGui.QLineEdit(self.widget2)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.le_images_directory.setFont(font)
        self.le_images_directory.setObjectName(_fromUtf8("le_images_directory"))
        self.verticalLayout_6.addWidget(self.le_images_directory)
        self.le_niba_id = QtGui.QLineEdit(self.widget2)
        self.le_niba_id.setObjectName(_fromUtf8("le_niba_id"))
        self.verticalLayout_6.addWidget(self.le_niba_id)
        self.le_dic_id = QtGui.QLineEdit(self.widget2)
        self.le_dic_id.setObjectName(_fromUtf8("le_dic_id"))
        self.verticalLayout_6.addWidget(self.le_dic_id)
        self.widget3 = QtGui.QWidget(self.groupBox_3)
        self.widget3.setGeometry(QtCore.QRect(1, 150, 421, 64))
        self.widget3.setObjectName(_fromUtf8("widget3"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.widget3)
        self.verticalLayout_7.setMargin(0)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pb_save_session = QtGui.QPushButton(self.widget3)
        self.pb_save_session.setObjectName(_fromUtf8("pb_save_session"))
        self.horizontalLayout.addWidget(self.pb_save_session)
        self.pb_apply_session = QtGui.QPushButton(self.widget3)
        self.pb_apply_session.setObjectName(_fromUtf8("pb_apply_session"))
        self.horizontalLayout.addWidget(self.pb_apply_session)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.pb_load_session = QtGui.QPushButton(self.widget3)
        self.pb_load_session.setObjectName(_fromUtf8("pb_load_session"))
        self.verticalLayout_7.addWidget(self.pb_load_session)
        notepad.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(notepad)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 838, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        notepad.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(notepad)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        notepad.setStatusBar(self.statusbar)

        self.retranslateUi(notepad)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), notepad.close)
        QtCore.QMetaObject.connectSlotsByName(notepad)

    def retranslateUi(self, notepad):
        notepad.setWindowTitle(QtGui.QApplication.translate("notepad", "Spot Analyser", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("notepad", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.button_save.setText(QtGui.QApplication.translate("notepad", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("notepad", "Cell ID Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.button_change_cellid_parameters.setText(QtGui.QApplication.translate("notepad", "Change cell ID parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("notepad", "max dist over waist", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("notepad", "max split over minor axis", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("notepad", "min pixels per cell", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("notepad", "max pixels per cell", None, QtGui.QApplication.UnicodeUTF8))
        self.button_load_default_cellid_parameters.setText(QtGui.QApplication.translate("notepad", "Load default cell ID parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.prepare_structure.setText(QtGui.QApplication.translate("notepad", "Prepare folder structure", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("notepad", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.working_directory.setText(QtGui.QApplication.translate("notepad", "Working directory...", None, QtGui.QApplication.UnicodeUTF8))
        self.cell_id_executable.setText(QtGui.QApplication.translate("notepad", "Cell ID executable...", None, QtGui.QApplication.UnicodeUTF8))
        self.fiji_executable.setText(QtGui.QApplication.translate("notepad", "Fiji executable...", None, QtGui.QApplication.UnicodeUTF8))
        self.spottyR_file.setText(QtGui.QApplication.translate("notepad", "spotty.R file...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_save_preferences.setText(QtGui.QApplication.translate("notepad", "Save preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_load_preferences.setText(QtGui.QApplication.translate("notepad", "Load preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("notepad", "Session data", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_images_directory.setText(QtGui.QApplication.translate("notepad", "Images directory...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("notepad", "NIBA ID (e.g. w1NIBA)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("notepad", "DIC ID (e.g. w2DIC)", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_save_session.setText(QtGui.QApplication.translate("notepad", "Save session...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_apply_session.setText(QtGui.QApplication.translate("notepad", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_load_session.setText(QtGui.QApplication.translate("notepad", "Load session...", None, QtGui.QApplication.UnicodeUTF8))

