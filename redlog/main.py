# -*- coding: utf-8 -*-

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

import sys
from PyQt4 import QtCore, QtGui
from redlog.ui.window import Ui_MainWindow as MainUiDialog
from redlog.ui.login import Ui_Dialog as LoginUiDialog
from redlog.ui import resources
from redlog import settings
from redlog import models

# Load Qt resources
resources.qInitResources()

class IssuesUpdater(QtCore.QThread):
    def __init__(self, lock, base_url, username, password, parent=None):
        super(IssuesUpdater, self).__init__(parent)
        self.lock = lock
        self.base_url = base_url
        self.username = username
        self.password = password
        self.stopped = False
        self.mutex = QtCore.QMutex()
        self.path = None
        self.completed = False

    def run(self):
        store = models.RemoteIssuesStore(self.base_url, self.username, self.password)
        
        try:
            issues = store.get_issues()
            cache = models.LocalStore()
            cache.set_issues(issues)
            self.emit(QtCore.SIGNAL("IssuesUpdated()"))
        except Exception, e:
            print e
            self.emit(QtCore.SIGNAL("IssuesUpdatedError()"))
        
        self.stop()
    
    def stop(self): 
        with QtCore.QMutexLocker(self.mutex):
            self.stopped = True

class TimeSubmitter(QtCore.QThread):
    def __init__(self, lock, base_url, username, password, parent=None):
        super(TimeSubmitter, self).__init__(parent)
        self.lock = lock
        self.base_url = base_url
        self.username = username
        self.password = password
        self.issue = None
        self.stopped = False
        self.mutex = QtCore.QMutex()
        self.path = None 
        self.completed = False

    def run(self):
        isError = False
        if self.issue != None:
            store = models.RemoteIssuesStore(self.base_url, self.username, self.password)
            localStore = models.LocalStore()
            
            try:
                spent_time = localStore.get_spent_time(self.issue[0])
                store.submit(self.issue[0], spent_time/3600.0, settings.REDMINE_ACTIVITIES.get('Mixed activity'), u'Time submitted using RedLog application v%s' % settings.REDLOG_VERSION)
            except Exception, e:
                print e
                isError = True
            
        self.issue = None
        
        if isError:
            self.emit(QtCore.SIGNAL("TimeSubmittedError()"))
        else:
            self.emit(QtCore.SIGNAL("TimeSubmitted()"))

        self.stop()

    
    def stop(self): 
        with QtCore.QMutexLocker(self.mutex):
            self.stopped = True


class LoginForm(QtGui.QDialog):
    
    def __init__(self, parent=None):
        super(LoginForm, self).__init__(parent)
        
        self.ui = LoginUiDialog()
        self.ui.setupUi(self)
        
        self.connect(self.ui.loginPushButton, QtCore.SIGNAL("clicked()"), self.saveCredentials)
        
        self.localStore = models.LocalStore()
        self.credentials = self.localStore.get_credentials()
    
    def setCredentials(self, credentials):
        self.ui.usernameLineEdit.setText(credentials.username)
        self.ui.passwordLineEdit.setText(credentials.password)
        
    def saveCredentials(self):
        username = unicode(self.ui.usernameLineEdit.text())
        password = unicode(self.ui.passwordLineEdit.text())
        self.localStore.set_credentials(username, password)
        
        self.emit(QtCore.SIGNAL("credentialsSaved()"))
        self.close()
        

class MainWindow(QtGui.QMainWindow):    
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.ui = MainUiDialog()
        self.ui.setupUi(self)
        
        self.ui.lcdNumber.display("00:00:00")
        self.ui.startPushButton.setEnabled(False)
        self.ui.openPushButton.setEnabled(False)
        self.ui.submitPushButton.setEnabled(False)
        self.connect(self.ui.reloadPushButton, QtCore.SIGNAL("clicked()"), self.reloadIssues)
        self.connect(self.ui.startPushButton, QtCore.SIGNAL("clicked()"), self.toggleTimer)
        self.connect(self.ui.openPushButton, QtCore.SIGNAL("clicked()"), self.openIssue)
        self.connect(self.ui.submitPushButton, QtCore.SIGNAL("clicked()"), self.submitTime)
        self.connect(self.ui.issuesComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.issueIndexSelected)
        self.connect(self.ui.actionShowHide, QtCore.SIGNAL("triggered()"), self.toggleVisibility)
        self.connect(self.ui.actionReset_credentials, QtCore.SIGNAL("triggered()"), self.resetCredentials)
        
        self.qtimer = QtCore.QTimer()
        self.qtimer.setInterval(settings.TICKING_INTERVAL)
        self.connect(self.qtimer, QtCore.SIGNAL("timeout()"), self.timerTick)

        self.localStore = models.LocalStore()
        self.issues = self.localStore.get_issues()
                
        self.lock = QtCore.QReadWriteLock()
        
        credentials = self.localStore.get_credentials()
        if len(credentials) == 0:
            self.issuesUpdater = IssuesUpdater(self.lock, settings.REDMINE_BASE_URL, '', '')
            self.timeSubmitter = TimeSubmitter(self.lock, settings.REDMINE_BASE_URL, '', '')
        else:
            self.issuesUpdater = IssuesUpdater(self.lock, settings.REDMINE_BASE_URL, credentials[0], credentials[1])
            self.timeSubmitter = TimeSubmitter(self.lock, settings.REDMINE_BASE_URL, credentials[0], credentials[1])

        self.connect(self.issuesUpdater, QtCore.SIGNAL("IssuesUpdated()"), self.issuesReloaded)
        self.connect(self.issuesUpdater, QtCore.SIGNAL("IssuesUpdatedError()"), self.issuesReloadError)
        self.connect(self.timeSubmitter, QtCore.SIGNAL("TimeSubmitted()"), self.timeSubmitted)
        self.connect(self.timeSubmitter, QtCore.SIGNAL("TimeSubmittedError()"), self.timeSubmitError)
        
        self.loginForm = LoginForm(self)
        self.connect(self.loginForm, QtCore.SIGNAL("credentialsSaved()"), self.reloadIssues)
        self.connect(self.loginForm, QtCore.SIGNAL("credentialsSaved()"), self.credentialsSaved)
        
        self.issuesReloaded()
        
        self.updateLCD()
        self.ui.statusbar.showMessage(u"Application loaded")
        
        icon = QtGui.QIcon(":/Icon.png")
        self.setWindowIcon(icon)
                
        #self.tray = QtGui.QSystemTrayIcon(self)
        #self.tray.setIcon(icon)
        #menu = QtGui.QMenu(self)
        #self.systemTrayShowHideAction = menu.addAction("Quit")
        #self.connect(self.systemTrayShowHideAction, QtCore.SIGNAL("triggered()"), self.toggleVisibility)
        #menu.addSeparator()
        #self.systemTracyQuitAction = menu.addAction("Quit")
        #self.connect(self.systemTracyQuitAction, QtCore.SIGNAL("triggered()"), self.close)
        #self.tray.setContextMenu(menu)
        #self.tray.show()
    
    def show(self):
        super(MainWindow, self).show()
        self.ui.actionShowHide.setText(u"Hide")
        #self.systemTrayShowHideAction.setText(u"Hide")

    def hide(self):
        super(MainWindow, self).hide()
        self.ui.actionShowHide.setText(u"Show")
        #self.systemTrayShowHideAction.setText(u"Show")
    
    def toggleVisibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()
    
    def reloadIssues(self):
        credentials = self.localStore.get_credentials()
        if len(credentials) == 0:
            self.loginForm.show()
            return
        
        self.ui.statusbar.showMessage(u"Loading issues...")
        self.ui.issuesComboBox.setEnabled(False)
        self.ui.reloadPushButton.setEnabled(False)
        self.ui.startPushButton.setEnabled(False)
        self.ui.openPushButton.setEnabled(False)
        self.ui.submitPushButton.setEnabled(False)
        
        self.issuesUpdater.start()

    def issuesReloaded(self):
        self.issues = self.localStore.get_issues()
        
        self.ui.issuesComboBox.clear()
        self.ui.issuesComboBox.addItem(u"--- Select an issue to track ---")
        
        for issue in self.issues:
            self.ui.issuesComboBox.addItem(models.cleanup_issue_title(issue[1]))
        
        self.ui.issuesComboBox.setCurrentIndex(0)
        
        self.ui.statusbar.showMessage(u"Issues updated")
        self.ui.issuesComboBox.setEnabled(True)
        self.ui.reloadPushButton.setEnabled(True)
    
    def issuesReloadError(self):
        self.ui.statusbar.showMessage(u"Failed to reload issues")
        self.ui.issuesComboBox.setEnabled(True)
        self.ui.reloadPushButton.setEnabled(True)        

    def issueIndexSelected(self, index):
        try:
            current_issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
        except IndexError:
            current_issue = None
        if index == 0:
            self.ui.startPushButton.setEnabled(False)
            self.ui.openPushButton.setEnabled(False)
            self.ui.submitPushButton.setEnabled(False)
            self.ui.issueTextEdit.setPlainText('')
        elif index != -1:
            self.ui.startPushButton.setEnabled(True)
            self.ui.openPushButton.setEnabled(True)
            self.ui.submitPushButton.setEnabled(True)
            self.ui.issueTextEdit.setPlainText(current_issue[1])
        
        self.updateLCD()

    def updateLCD(self):
        if self.ui.issuesComboBox.currentIndex() == 0:
            self.ui.lcdNumber.display("00:00:00")
        else:
            try:
                current_issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
                spent_time = self.localStore.get_spent_time(current_issue[0])
            except IndexError:
                spent_time = 0
            if spent_time == 0:
                self.ui.lcdNumber.display("00:00:00")
            else:
                self.ui.lcdNumber.display(models.format_lcd_time(spent_time))

    def toggleTimer(self):
        if self.qtimer.isActive():
            self.qtimer.stop()
            self.ui.startPushButton.setText(u'Start')
            self.ui.submitPushButton.setEnabled(True)
            self.ui.reloadPushButton.setEnabled(True)
            self.ui.issuesComboBox.setEnabled(True)
        else:
            self.qtimer.start()
            self.ui.startPushButton.setText(u'Stop')
            self.ui.submitPushButton.setEnabled(False)
            self.ui.reloadPushButton.setEnabled(False)
            self.ui.issuesComboBox.setEnabled(False)
    
    def timerTick(self):
        current_issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
        self.localStore.increment_time(settings.TICKING_INTERVAL/1000.0, current_issue[0])
        self.updateLCD()
    
    def openIssue(self):
        try:
            issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
            url = "%s/time_entries/" % issue[2]
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        except IndexError:
            pass
    
    def submitTime(self):
        reply = QtGui.QMessageBox.question(self, "Redlog - Time Submission", "You are about to submit your time to Redmine.\nAre you sure?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default, QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
        if reply == QtGui.QMessageBox.Yes:
            self.ui.issuesComboBox.setEnabled(False)
            self.ui.reloadPushButton.setEnabled(False)
            self.ui.startPushButton.setEnabled(False)
            self.ui.openPushButton.setEnabled(False)
            self.ui.submitPushButton.setEnabled(False)
            
            self.ui.statusbar.showMessage(u"Submitting time to %s" % settings.REDMINE_BASE_URL)
            
            self.timeSubmitter.issue = self.issues[self.ui.issuesComboBox.currentIndex()-1] 
            self.timeSubmitter.start()
    
    def timeSubmitted(self):
        issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
        self.localStore.reset_issue(issue[0])
        
        self.ui.issuesComboBox.setEnabled(True)
        self.ui.reloadPushButton.setEnabled(True)
        self.ui.startPushButton.setEnabled(True)
        self.ui.openPushButton.setEnabled(True)
        self.ui.submitPushButton.setEnabled(True)
        
        self.ui.statusbar.showMessage(u"Time submitted for #%s" % issue[0])
        
        self.updateLCD()
    
    def timeSubmitError(self):
        issue = self.issues[self.ui.issuesComboBox.currentIndex()-1]
        
        self.ui.issuesComboBox.setEnabled(True)
        self.ui.reloadPushButton.setEnabled(True)
        self.ui.startPushButton.setEnabled(True)
        self.ui.openPushButton.setEnabled(True)
        self.ui.submitPushButton.setEnabled(True)
        
        self.ui.statusbar.showMessage(u"Failed to submit time for issue #%s" % issue[0])
        

    def credentialsSaved(self):
        credentials = self.localStore.get_credentials()
        if len(credentials) > 0:
            self.issuesUpdater.username = credentials[0]
            self.issuesUpdater.password = credentials[1]
            self.timeSubmitter.username = credentials[0]
            self.timeSubmitter.password = credentials[1]
    
    def resetCredentials(self):
        self.localStore.reset_credentials()
        self.ui.statusbar.showMessage(u"Reseted credentials.")
    
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            #self.hide()
            event.accept()
            return
        else:
            super(MainWindow, self).changeEvent(event)
    
    def closeEvent(self, event):
        sys.exit()

def start():
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.raise_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()

if __name__ == '__main__':
    start()

