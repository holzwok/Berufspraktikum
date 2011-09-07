# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Wed Sep  7 17:02:57 2011
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
        self.pushButton_2.setGeometry(QtCore.QRect(270, 700, 261, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.button_save = QtGui.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(270, 660, 261, 27))
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(60, 40, 261, 231))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.editor_window = QtGui.QTextEdit(self.groupBox)
        self.editor_window.setGeometry(QtCore.QRect(200, 30, 50, 27))
        self.editor_window.setObjectName(_fromUtf8("editor_window"))
        self.editor_window_2 = QtGui.QTextEdit(self.groupBox)
        self.editor_window_2.setGeometry(QtCore.QRect(200, 70, 50, 27))
        self.editor_window_2.setObjectName(_fromUtf8("editor_window_2"))
        self.editor_window_3 = QtGui.QTextEdit(self.groupBox)
        self.editor_window_3.setGeometry(QtCore.QRect(200, 110, 50, 27))
        self.editor_window_3.setObjectName(_fromUtf8("editor_window_3"))
        self.editor_window_4 = QtGui.QTextEdit(self.groupBox)
        self.editor_window_4.setGeometry(QtCore.QRect(200, 150, 50, 27))
        self.editor_window_4.setObjectName(_fromUtf8("editor_window_4"))
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
        self.log_window = QtGui.QTextBrowser(self.centralwidget)
        self.log_window.setGeometry(QtCore.QRect(20, 440, 621, 192))
        self.log_window.setObjectName(_fromUtf8("log_window"))
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

