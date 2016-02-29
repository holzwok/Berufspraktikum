# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Sat Mar 22 10:05:10 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
# read documentation for help
# http://zetcode.com/gui/pyqt4/ (PyQt4 tutorial)
# http://qt-project.org/doc/qt-4.8/qtgui.html 
# (QtGui module contains for example the following classes: QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QSpacerItem, QSizePolicy, QApplication)
# http://qt-project.org/doc/qt-4.8/qtcore.html 
# (QtCore module contains for example the following classes: QString, QRect, QMetaObject)

try:
    _fromUtf8 = QtCore.QString.fromUtf8 
    # QtCore.QString - provides a Unicode character string
    # QtCore.QString.fromUtf8 - returns a QString initialized with the first size bytes of the UTF-8 string str
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(629, 316)
        
        # GUI (Graphical User Interface) elements are for example widgets/controls like buttons, sliders, hyperlinks, ...
        
        # widget containing command buttons "Mask path..." (maskpath), "Output path..." (outpath), "Loc files path..." (locpath)
        # widgets verticalLayout in widget verticalLayoutWidget
        self.verticalLayoutWidget = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 160, 101)) #QtCore.QRect - defines a rectangle in the plane using integer precision
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget) #QtGui.QVBoxLayout - lines up widgets vertically
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        ## insert command button for maskpath into widget
        self.pb_mskpath = QtGui.QPushButton(self.verticalLayoutWidget) # QtGui.QPushButton - provides a command button  # pb - push button
        self.pb_mskpath.setObjectName(_fromUtf8("pb_mskpath"))
        self.verticalLayout.addWidget(self.pb_mskpath)
        ## insert command button for outpath into widget
        self.pb_outpath = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_outpath.setObjectName(_fromUtf8("pb_outpath"))
        self.verticalLayout.addWidget(self.pb_outpath)
        ## insert command button for locpath into widget
        self.pb_locpath = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_locpath.setObjectName(_fromUtf8("pb_locpath"))
        self.verticalLayout.addWidget(self.pb_locpath)
        

        # widget containing one-line text editors for maskpath, outpath, locpath
        self.verticalLayoutWidget_2 = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(180, 10, 421, 101))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        ## insert one-line text editor for maskpath into widget
        self.le_mskpath = QtGui.QLineEdit(self.verticalLayoutWidget_2) # QtGui.QLineEdit - is a one-line text editor that allows the user to enter and edit a single line of plain text
        self.le_mskpath.setEnabled(True)
        self.le_mskpath.setObjectName(_fromUtf8("le_mskpath"))
        self.verticalLayout_2.addWidget(self.le_mskpath)
        ## insert one-line text editor for outpath into widget
        self.le_outpath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.le_outpath.setEnabled(True)
        self.le_outpath.setObjectName(_fromUtf8("le_outpath"))
        self.verticalLayout_2.addWidget(self.le_outpath)
        ## insert one-line text editor for locpath into widget
        self.le_locpath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.le_locpath.setEnabled(True)
        self.le_locpath.setObjectName(_fromUtf8("le_locpath"))
        self.verticalLayout_2.addWidget(self.le_locpath)
        

        # command button "Save and close"
        self.pb_close = QtGui.QPushButton(Dialog)
        self.pb_close.setGeometry(QtCore.QRect(470, 250, 141, 23))
        self.pb_close.setObjectName(_fromUtf8("pb_close"))
        

        # widget containing text display "Functions" and checkboxes "Populate Database", "Add medians", "Create plots", "Draw crosses", "Annotate cells"
        self.verticalLayoutWidget_3 = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(20, 120, 160, 165))
        self.verticalLayoutWidget_3.setObjectName(_fromUtf8("verticalLayoutWidget_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        ## insert text display "Functions" into widget
        self.label = QtGui.QLabel(self.verticalLayoutWidget_3) # QtGui.QLabel - provides a text or image display
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        ## insert checkbox "Populate Database" into widget
        self.cb_populate = QtGui.QCheckBox(self.verticalLayoutWidget_3) # QtGui.QCheckBox - provides a checkbox with a text label
        self.cb_populate.setObjectName(_fromUtf8("cb_populate"))
        self.verticalLayout_3.addWidget(self.cb_populate)
        ## insert checkbox "Add medians" into widget
        self.cb_add_medians = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_add_medians.setObjectName(_fromUtf8("cb_add_medians"))
        self.verticalLayout_3.addWidget(self.cb_add_medians)
        ## insert checkbox "Create plots" into widget
        self.cb_plot = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_plot.setObjectName(_fromUtf8("cb_plot"))
        self.verticalLayout_3.addWidget(self.cb_plot)
        ## insert checkbox "Draw crosses" into widget
        self.cb_cross = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_cross.setObjectName(_fromUtf8("cb_cross"))
        self.verticalLayout_3.addWidget(self.cb_cross)
        ## insert checkbox "Annotate cells" into widget
        self.cb_annotate = QtGui.QCheckBox(self.verticalLayoutWidget_3)
        self.cb_annotate.setObjectName(_fromUtf8("cb_annotate"))
        self.verticalLayout_3.addWidget(self.cb_annotate)
        
        # command button "Run selected"
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding) 
        # QtGui.QSpacerItem - provides blank space in a layout
        # QtGui.QSizePolicy - is a layout attribute describing horizontal and vertical resizing policy
        self.verticalLayout_3.addItem(spacerItem)
        self.pb_run = QtGui.QPushButton(self.verticalLayoutWidget_3)
        self.pb_run.setObjectName(_fromUtf8("pb_run"))
        self.verticalLayout_3.addWidget(self.pb_run)
        
        # widget containing channel tokens and group by cell widgets:
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(180, 120, 421, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        # insert text display "Enter channel tokens (sep. by space):" into widget
        self.label_2 = QtGui.QLabel(self.horizontalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        # insert one-line text editor belonging to "Enter channel tokens (sep. by space):" into widget
        self.le_channeltoken = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.le_channeltoken.setObjectName(_fromUtf8("le_channeltoken"))
        self.horizontalLayout.addWidget(self.le_channeltoken)
        # insert checkbox "Group by cell?" into widget
        self.cb_group_by_cell = QtGui.QCheckBox(Dialog)
        self.cb_group_by_cell.setGeometry(QtCore.QRect(180, 170, 421, 17))
        self.cb_group_by_cell.setObjectName(_fromUtf8("cb_group_by_cell"))

        '''Konstantin's code '''
        #widget containing mother-daughter related stuff
        self.verticalLayoutWidget_md = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget_md.setGeometry(QtCore.QRect(180, 200, 421, 62))
        self.verticalLayoutWidget_md.setObjectName(_fromUtf8("verticalLayoutWidgetMD"))
        self.verticalLayout_md = QtGui.QVBoxLayout(self.verticalLayoutWidget_md)
        self.verticalLayout_md.setMargin(0)
        self.verticalLayout_md.setObjectName(_fromUtf8("verticalLayoutMD"))
        #insert checkbox 
        self.cb_md = QtGui.QCheckBox(self.verticalLayoutWidget_md)
        self.cb_md.setObjectName(_fromUtf8("cb_md"))
        self.verticalLayout_md.addWidget(self.cb_md)
        '''KC end'''

        # so far all widgets are defined by widget manner and an object name
        # the function retranslateUi sets all widgets with a text readable by the user
        self.retranslateUi(Dialog)

        # QtCore.QMetaObject - contains meta-information about Qt objects
        # it is responsible for the signals and slots inter-object communication mechanism, runtime type information, and the Qt property system
        QtCore.QMetaObject.connectSlotsByName(Dialog) 

    def retranslateUi(self, Dialog):
        # QtGui.QApplication - manages the GUI application's control flow and main settings
        #                    - provides localization of strings that are visible to the user via translate()
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "RNA counter", None, QtGui.QApplication.UnicodeUTF8)) 
        self.pb_mskpath.setText(QtGui.QApplication.translate("Dialog", "Mask path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_outpath.setText(QtGui.QApplication.translate("Dialog", "Output path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_locpath.setText(QtGui.QApplication.translate("Dialog", "Loc files path...", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_close.setText(QtGui.QApplication.translate("Dialog", "Save and close", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Functions", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_populate.setText(QtGui.QApplication.translate("Dialog", "Populate Database", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_add_medians.setText(QtGui.QApplication.translate("Dialog", "Add medians", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_plot.setText(QtGui.QApplication.translate("Dialog", "Create plots", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_cross.setText(QtGui.QApplication.translate("Dialog", "Draw crosses", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_annotate.setText(QtGui.QApplication.translate("Dialog", "Annotate cells", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_run.setText(QtGui.QApplication.translate("Dialog", "Run selected", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Enter channel tokens (sep. by space):", None, QtGui.QApplication.UnicodeUTF8))
        self.cb_group_by_cell.setText(QtGui.QApplication.translate("Dialog", "Normalisation per cell (instead of per image folder)", None, QtGui.QApplication.UnicodeUTF8))
        '''Konstantin's Code'''
        self.cb_md.setText(QtGui.QApplication.translate("Dialog", "analyse daughter cells seperately", None, QtGui.QApplication.UnicodeUTF8))

