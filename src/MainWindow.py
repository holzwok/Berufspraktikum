# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Thu Sep  8 11:18:21 2011
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
        notepad.resize(671, 907)
        self.centralwidget = QtGui.QWidget(notepad)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(400, 820, 261, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.button_save = QtGui.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(400, 780, 261, 27))
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(390, 20, 261, 261))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.max_dist_over_waist = QtGui.QTextEdit(self.groupBox)
        self.max_dist_over_waist.setGeometry(QtCore.QRect(200, 30, 50, 27))
        self.max_dist_over_waist.setObjectName(_fromUtf8("max_dist_over_waist"))
        self.max_split_over_minor_axis = QtGui.QTextEdit(self.groupBox)
        self.max_split_over_minor_axis.setGeometry(QtCore.QRect(200, 70, 50, 27))
        self.max_split_over_minor_axis.setObjectName(_fromUtf8("max_split_over_minor_axis"))
        self.min_pixels_per_cell = QtGui.QTextEdit(self.groupBox)
        self.min_pixels_per_cell.setGeometry(QtCore.QRect(200, 110, 50, 27))
        self.min_pixels_per_cell.setObjectName(_fromUtf8("min_pixels_per_cell"))
        self.max_pixels_per_cell = QtGui.QTextEdit(self.groupBox)
        self.max_pixels_per_cell.setGeometry(QtCore.QRect(200, 150, 50, 27))
        self.max_pixels_per_cell.setObjectName(_fromUtf8("max_pixels_per_cell"))
        self.button_change_cellid_parameters = QtGui.QPushButton(self.groupBox)
        self.button_change_cellid_parameters.setGeometry(QtCore.QRect(10, 190, 241, 27))
        self.button_change_cellid_parameters.setObjectName(_fromUtf8("button_change_cellid_parameters"))
        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(10, 30, 180, 151))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtGui.QLabel(self.widget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.button_load_default_cellid_parameters = QtGui.QPushButton(self.groupBox)
        self.button_load_default_cellid_parameters.setGeometry(QtCore.QRect(10, 220, 241, 27))
        self.button_load_default_cellid_parameters.setObjectName(_fromUtf8("button_load_default_cellid_parameters"))
        self.log_window = QtGui.QTextEdit(self.centralwidget)
        self.log_window.setGeometry(QtCore.QRect(10, 610, 651, 161))
        self.log_window.setObjectName(_fromUtf8("log_window"))
        self.prepare_structure = QtGui.QPushButton(self.centralwidget)
        self.prepare_structure.setGeometry(QtCore.QRect(80, 300, 221, 27))
        self.prepare_structure.setObjectName(_fromUtf8("prepare_structure"))
        notepad.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(notepad)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 671, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        notepad.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(notepad)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        notepad.setStatusBar(self.statusbar)

        self.retranslateUi(notepad)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), notepad.close)
        QtCore.QMetaObject.connectSlotsByName(notepad)

    def retranslateUi(self, notepad):
        notepad.setWindowTitle(QtGui.QApplication.translate("notepad", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
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

