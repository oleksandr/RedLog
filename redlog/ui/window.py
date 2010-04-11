# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/window.ui'
#
# Created: Sun Apr 11 20:04:30 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(411, 310)
        MainWindow.setMinimumSize(QtCore.QSize(411, 310))
        MainWindow.setMaximumSize(QtCore.QSize(411, 310))
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lcdNumber = QtGui.QLCDNumber(self.centralwidget)
        self.lcdNumber.setEnabled(True)
        self.lcdNumber.setGeometry(QtCore.QRect(20, 120, 371, 81))
        self.lcdNumber.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lcdNumber.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lcdNumber.setAutoFillBackground(True)
        self.lcdNumber.setNumDigits(10)
        self.lcdNumber.setObjectName("lcdNumber")
        self.issuesComboBox = QtGui.QComboBox(self.centralwidget)
        self.issuesComboBox.setGeometry(QtCore.QRect(20, 10, 281, 26))
        self.issuesComboBox.setObjectName("issuesComboBox")
        self.openPushButton = QtGui.QPushButton(self.centralwidget)
        self.openPushButton.setGeometry(QtCore.QRect(140, 210, 131, 51))
        self.openPushButton.setObjectName("openPushButton")
        self.submitPushButton = QtGui.QPushButton(self.centralwidget)
        self.submitPushButton.setGeometry(QtCore.QRect(270, 210, 131, 51))
        self.submitPushButton.setObjectName("submitPushButton")
        self.startPushButton = QtGui.QPushButton(self.centralwidget)
        self.startPushButton.setGeometry(QtCore.QRect(10, 210, 131, 51))
        self.startPushButton.setObjectName("startPushButton")
        self.reloadPushButton = QtGui.QPushButton(self.centralwidget)
        self.reloadPushButton.setGeometry(QtCore.QRect(305, 8, 90, 30))
        self.reloadPushButton.setAutoDefault(False)
        self.reloadPushButton.setObjectName("reloadPushButton")
        self.issueTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.issueTextEdit.setGeometry(QtCore.QRect(20, 50, 371, 61))
        self.issueTextEdit.setFrameShape(QtGui.QFrame.StyledPanel)
        self.issueTextEdit.setReadOnly(True)
        self.issueTextEdit.setObjectName("issueTextEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 411, 22))
        self.menubar.setObjectName("menubar")
        self.menuRedLog = QtGui.QMenu(self.menubar)
        self.menuRedLog.setObjectName("menuRedLog")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionShowHide = QtGui.QAction(MainWindow)
        self.actionShowHide.setObjectName("actionShowHide")
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionReset_credentials = QtGui.QAction(MainWindow)
        self.actionReset_credentials.setObjectName("actionReset_credentials")
        self.menuRedLog.addAction(self.actionQuit)
        self.menuOptions.addAction(self.actionReset_credentials)
        self.menubar.addAction(self.menuRedLog.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL("triggered()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "RedLog", None, QtGui.QApplication.UnicodeUTF8))
        self.openPushButton.setText(QtGui.QApplication.translate("MainWindow", "Open Issue", None, QtGui.QApplication.UnicodeUTF8))
        self.submitPushButton.setText(QtGui.QApplication.translate("MainWindow", "Submit", None, QtGui.QApplication.UnicodeUTF8))
        self.startPushButton.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadPushButton.setText(QtGui.QApplication.translate("MainWindow", "Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRedLog.setTitle(QtGui.QApplication.translate("MainWindow", "RedLog", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShowHide.setText(QtGui.QApplication.translate("MainWindow", "Hide", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReset_credentials.setText(QtGui.QApplication.translate("MainWindow", "Reset credentials", None, QtGui.QApplication.UnicodeUTF8))

