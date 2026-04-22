import sys
from core.dataTypes import *
from tabs import *
from core.dataManager import DataManager
from core.requests import DataManager as DataManagerRequest
from core.workers import ScanDevices

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200,200,550,550)
        self.setObjectName("MainWindow")
        self.checkdata=CheckData(checkData({}))
        self.tabWidget=QTabWidget(self)
        self.tabWidget.setMovable(True)
        self.setCentralWidget(self.tabWidget)
        self.dataManager=DataManagerRequest(self)
        self.dm=DataManager()
        
        # Connect Read
        self.dataManager.read.settings.connect(lambda:self.dataManager.response.settings.emit(self.dm.settings()))
        self.dataManager.read.style.connect(lambda objectName,style:self.dataManager.response.style.emit(objectName,self.dm.loadStyle(style)))

        # Connect Write
        self.dataManager.write.settings.connect(lambda data:self.dm.settings(True,data))
        
        
        # Connect
        self.connectTab:ConnectTab=ConnectTab(self,self.checkdata,self.dataManager)
        self.tabWidget.addTab(self.connectTab,"Connect")
        
        # Find
        self.findTab=FindTab(self,self.checkdata,self.dataManager)
        self.tabWidget.addTab(self.findTab,"Find")

        # Terminal
        self.terminalTab=TerminalTab(self,self.checkdata,self.dataManager)
        self.tabWidget.addTab(self.terminalTab,"Terminal")

        # Settings
        self.settingsTab=SettingsTab(self,self.checkdata,self.dataManager)
        self.tabWidget.addTab(self.settingsTab,"Settings")

        self.ScanDevicesButton=QPushButton("ScanDevices")
        self.ScanDevicesButton.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless))
        self.ScanDevicesButton.clicked.connect(self.ScanDevices)
        self.statusBar().addPermanentWidget(self.ScanDevicesButton)

        self.scanThread=None
        self.scanWorker=None

    def ScanDevices(self):
        try:
            if self.scanThread:
                try:
                    if self.scanThread.isRunning():self.scanWorker.stop();self.scanThread.quit();self.scanThread.wait(timeout=1000)
                except RuntimeError:pass
                self.scanThread=None
        except:self.scanThread=None

        self.scanThread=QThread(self)
        self.scanWorker=ScanDevices(self.checkdata.data.choosen_path_for_adb,self.checkdata)
        self.scanWorker.moveToThread(self.scanThread)
        self.scanThread.started.connect(self.scanWorker.run)
        self.scanWorker.devices.connect(self.UpdateConnectedDevices)
        self.scanWorker.line.connect(self.statusBar().showMessage)
        self.scanWorker.finished.connect(lambda:self.statusBar().showMessage("Scanning Finished!"))
        self.scanWorker.finished.connect(self.scanThread.quit)
        self.scanWorker.finished.connect(self.scanWorker.deleteLater)
        self.scanThread.finished.connect(self.scanThread.deleteLater)
        self.scanThread.start()

    def UpdateConnectedDevices(self,devices:List[ConnectedDevice]):
        self.checkdata.data.connected_devices=devices
        self.checkdata.changed_connected_devices.emit(devices)

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet(DataManager().loadStyle('main'))
    window=MainWindow()
    window.show()
    sys.exit(app.exec())