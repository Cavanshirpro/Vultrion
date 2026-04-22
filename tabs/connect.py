from core.dataTypes import *
from core.workers import ADBConnect,ADBDisconnect
from core.requests import DataManager

class ConnectTab(QWidget):
    def __init__(self,parent,checkdata:Optional[CheckData],dataManagerRequest:DataManager):
        super().__init__(parent)
        self.setObjectName("ConnectTab")
        self.MainLayout=QGridLayout(self)
        self.setLayout(self.MainLayout)
        self.checkData=checkdata
        self.checkData.changed.connect(self.on_data_changed)
        self.checkData.changed_founded_ips.connect(self.UpdateFoundedIps)
        self.dataManager=dataManagerRequest

        
        self.ipLabel=QLabel("<h1>IP:</h1>")
        self.MainLayout.addWidget(self.ipLabel,0,1,1,1)

        self.ipInput=QLineEdit()
        self.ipInput.setPlaceholderText("Enter IP adress")
        self.ipInput.setClearButtonEnabled(True)
        self.MainLayout.addWidget(self.ipInput,0,3,1,1)

        self.comboBox=QComboBox(self)
        self.comboBox.setPlaceholderText("Founded IPs")
        self.comboBox.currentTextChanged.connect(self.FillToIpInput)

        self.MainLayout.addWidget(self.comboBox,0,4,1,1)
        
        
        self.portLabel=QLabel("<h1>Port:</h1>")
        self.MainLayout.addWidget(self.portLabel,1,1,1,1)

        self.portInput=QLineEdit()
        self.portInput.setPlaceholderText("Enter Port")
        self.portInput.setClearButtonEnabled(True)
        self.MainLayout.addWidget(self.portInput,1,3,1,2)

        
        self.connectButton=QCommandLinkButton(self)
        font=QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(16)
        font.setBold(True)
        self.connectButton.setFont(font)
        icon=QIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless))
        self.connectButton.setIcon(icon)
        self.connectButton.setText("Connect")
        self.connectButton.setDescription("Connect to address")
        self.connectButton.clicked.connect(self.Connection)
        self.ipInput.returnPressed.connect(self.connectButton.click)
        self.MainLayout.addWidget(self.connectButton,2,1,1,4)

        
        self.disconnectButton=QCommandLinkButton(self)
        self.disconnectButton.setFont(font)
        icon_disconnect=QIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkOffline))
        self.disconnectButton.setIcon(icon_disconnect)
        self.disconnectButton.setText("Disconnect")
        self.disconnectButton.setDescription("Disconnect from addresses")
        self.disconnectButton.clicked.connect(self.Disonnection)
        self.MainLayout.addWidget(self.disconnectButton,3,1,1,4)

        
        self.progressLabel=QLabel("Connecting...")
        self.progressLabel.setVisible(False)
        self.MainLayout.addWidget(self.progressLabel,4,1,1,1)

        self.progressBar=QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.MainLayout.addWidget(self.progressBar,4,3,1,1)

        self.cancelButton=QPushButton("Cancel")
        self.cancelButton.setVisible(False)
        self.MainLayout.addWidget(self.cancelButton,4,4,1,1)

        self.Thread: QThread=None
        self.worker: ADBConnect=None

        
        self.Logs=QTextEdit()
        self.Logs.setReadOnly(True)
        self.Logs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.MainLayout.addWidget(self.Logs,5,1,1,4)

    def FillToIpInput(self):self.ipInput.setText(self.comboBox.currentText())

    def on_data_changed(self):pass

    def Connection(self):
        import ipaddress
        target=self.ipInput.text().strip()
        port=self.portInput.text().strip()
        if not port:port=''
        
        
        if not target:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Enter IP","Please Enter IP Address")
            self.ipInput.setStyleSheet("")
            return
        
        try:ipaddress.ip_address(target)
        except ValueError:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Invalid IP","Please Enter a Valid IP Address")
            self.ipInput.setStyleSheet("")
            return
        
        
        if port:
            try:
                port_num=int(port)
                if port_num<1 or port_num>65535:raise ValueError
            except ValueError:
                self.portInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
                QMessageBox.warning(self,"Invalid Port","Please Enter a Valid Port (1-65535)")
                self.portInput.setStyleSheet("")
                return
        try:
            if self.Thread:
                try:
                    if self.Thread.isRunning():
                        self.worker.stop()
                        self.Thread.quit()
                        self.Thread.wait(timeout=1000)
                except RuntimeError:pass
                self.Thread=None
        except:self.Thread=None
        
        self.worker=ADBConnect(adb_path=self.checkData.data.choosen_path_for_adb,target=f"{target}:{port if port else 5555}",checkData=self.checkData)
        self.Thread=QThread()
        self.worker.moveToThread(self.Thread)
        
        self.Thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.scanFinished)
        self.worker.line.connect(self.GetLineLog)
        self.worker.progress.connect(self.updateProgress)
        self.cancelButton.clicked.connect(self.worker.stop)

        self.worker.finished.connect(self.Thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.Thread.finished.connect(self.Thread.deleteLater)
    
        
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.progressLabel.setVisible(True)
        self.cancelButton.setVisible(True)
        self.connectButton.setEnabled(False)

        self.Thread.start()

    def Disonnection(self):
        import ipaddress
        target=self.ipInput.text().strip()
        port=self.portInput.text().strip()
        if not port:port=''
        
        if not target:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Enter IP","Please Enter IP Address")
            self.ipInput.setStyleSheet("")
            return
        
        try:ipaddress.ip_address(target)
        except ValueError:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Invalid IP","Please Enter a Valid IP Address")
            self.ipInput.setStyleSheet("")
            return
        
        
        if port:
            try:
                port_num=int(port)
                if port_num<1 or port_num>65535:raise ValueError
            except ValueError:
                self.portInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
                QMessageBox.warning(self,"Invalid Port","Please Enter a Valid Port (1-65535)")
                self.portInput.setStyleSheet("")
                return
        try:
            if self.Thread:
                try:
                    if self.Thread.isRunning():
                        self.worker.stop()
                        self.Thread.quit()
                        self.Thread.wait(timeout=1000)
                except RuntimeError:pass
                self.Thread=None
        except:self.Thread=None

        self.worker=ADBDisconnect(adb_path=self.checkData.data.choosen_path_for_adb,target=f"{target}:{port if port else 5555}",checkData=self.checkData)
        self.Thread=QThread()
        self.worker.moveToThread(self.Thread)
        
        self.Thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.scanFinished)
        self.worker.line.connect(self.GetLineLog)
        self.worker.progress.connect(self.updateProgress)
        self.cancelButton.clicked.connect(self.worker.stop)

        self.worker.finished.connect(self.Thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.Thread.finished.connect(self.Thread.deleteLater)
    
        
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.progressLabel.setVisible(True)
        self.cancelButton.setVisible(True)
        self.connectButton.setEnabled(False)

        self.Thread.start()

    def GetLineLog(self,line:str):
        self.Logs.setText(self.Logs.toPlainText()+'\n'+line)
    
    def updateProgress(self,count: int):
        self.progressBar.setValue(count)
        self.progressLabel.setText(f"Found: {count}")

    def scanFinished(self):
        self.progressBar.setVisible(False)
        self.progressLabel.setVisible(False)
        self.cancelButton.setVisible(False)

        self.connectButton.setEnabled(True)

    def UpdateFoundedIps(self,ips:List[str]):
        self.comboBox.clear()
        for ip in ips:self.comboBox.addItem(ip);print(ip)