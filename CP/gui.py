# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Mon Oct 29 14:25:15 2012
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
        Dialog.resize(626, 396)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(310, 350, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
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
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(180, 10, 160, 101))
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

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "RNA counter", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_mskpath.setText(QtGui.QApplication.translate("Dialog", "Mask path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_outpath.setText(QtGui.QApplication.translate("Dialog", "Output path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_locpath.setText(QtGui.QApplication.translate("Dialog", "Loc files path...", None, QtGui.QApplication.UnicodeUTF8))

