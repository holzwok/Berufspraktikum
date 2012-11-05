# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Mon Nov 05 15:03:28 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(629, 316)
        self.verticalLayoutWidget = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 160, 101))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pb_mskpath = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_mskpath.setObjectName(_fromUtf8("pb_mskpath"))
        self.verticalLayout.addWidget(self.pb_mskpath)
        self.pb_outpath = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_outpath.setObjectName(_fromUtf8("pb_outpath"))
        self.verticalLayout.addWidget(self.pb_outpath)
        self.pb_locpath = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_locpath.setObjectName(_fromUtf8("pb_locpath"))
        self.verticalLayout.addWidget(self.pb_locpath)
        self.verticalLayoutWidget_2 = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(180, 10, 421, 101))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.le_mskpath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.le_mskpath.setEnabled(True)
        self.le_mskpath.setObjectName(_fromUtf8("le_mskpath"))
        self.verticalLayout_2.addWidget(self.le_mskpath)
        self.le_outpath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.le_outpath.setEnabled(True)
        self.le_outpath.setObjectName(_fromUtf8("le_outpath"))
        self.verticalLayout_2.addWidget(self.le_outpath)
        self.le_locpath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.le_locpath.setEnabled(True)
        self.le_locpath.setObjectName(_fromUtf8("le_locpath"))
        self.verticalLayout_2.addWidget(self.le_locpath)
        self.pb_close = QtGui.QPushButton(Dialog)
        self.pb_close.setGeometry(QtCore.QRect(470, 250, 141, 23))
        self.pb_close.setObjectName(_fromUtf8("pb_close"))
        self.verticalLayoutWidget_3 = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(20, 120, 160, 151))
        self.verticalLayoutWidget_3.setObjectName(_fromUtf8("verticalLayoutWidget_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.cb_populate = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_populate.setObjectName(_fromUtf8("cb_populate"))
        self.verticalLayout_3.addWidget(self.cb_populate)
        self.cb_plot = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_plot.setObjectName(_fromUtf8("cb_plot"))
        self.verticalLayout_3.addWidget(self.cb_plot)
        self.cb_cross = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_cross.setObjectName(_fromUtf8("cb_cross"))
        self.verticalLayout_3.addWidget(self.cb_cross)
        self.cb_annotate = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_annotate.setObjectName(_fromUtf8("cb_annotate"))
        self.verticalLayout_3.addWidget(self.cb_annotate)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.pb_run = QtGui.QPushButton(self.verticalLayoutWidget_3)
        self.pb_run.setObjectName(_fromUtf8("pb_run"))
        self.verticalLayout_3.addWidget(self.pb_run)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "RNA counter", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_mskpath.setText(QtGui.QApplication.translate("Dialog", "Mask path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_outpath.setText(QtGui.QApplication.translate("Dialog", "Output path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_locpath.setText(QtGui.QApplication.translate("Dialog", "Loc files path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_close.setText(QtGui.QApplication.translate("Dialog", "Save and close", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Functions", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_populate.setText(QtGui.QApplication.translate("Dialog", "Populate Database", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_plot.setText(QtGui.QApplication.translate("Dialog", "Create plots", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cross.setText(QtGui.QApplication.translate("Dialog", "Draw crosses", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_annotate.setText(QtGui.QApplication.translate("Dialog", "Annotate cells", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_run.setText(QtGui.QApplication.translate("Dialog", "Run selected", None, QtGui.QApplication.UnicodeUTF8))

