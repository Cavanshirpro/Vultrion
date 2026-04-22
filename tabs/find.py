from core.dataTypes import *
from core.workers import NMapConnect
from core.requests import DataManager

class FindTab(QWidget):
    def __init__(self,parent,checkdata:Optional[CheckData],dataManagerRequest:DataManager):
        super().__init__(parent)
        self.setObjectName("FindTab")
        self.MainLayout=QGridLayout(self)
        self.setLayout(self.MainLayout)
        self.checkData=checkdata
        self.checkData.changed.connect(self.on_data_changed)
        self.dataManager=dataManagerRequest
        
        self.ipLabel=QLabel("<h1>IP:</h1>")
        self.MainLayout.addWidget(self.ipLabel,0,1,1,1)

        self.ipInput=QLineEdit()
        self.ipInput.setPlaceholderText("Enter IP adress")
        self.ipInput.setClearButtonEnabled(True)
        self.MainLayout.addWidget(self.ipInput,0,3,1,1)

        self.comboBox=QComboBox(self)
        self.comboBox.setPlaceholderText("Local IPs")
        self.comboBox.addItem("192.168.1.0/24")
        self.comboBox.addItem("127.0.0.0/24")

        self.comboBox.currentTextChanged.connect(self.FillToIpInput)

        self.MainLayout.addWidget(self.comboBox,0,4,1,1)

        
        self.connectButton=QCommandLinkButton(self)
        font=QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(16)
        font.setBold(True)
        self.connectButton.setFont(font)
        icon=QIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless))
        self.connectButton.setIcon(icon)
        self.connectButton.setText("Connect")
        self.connectButton.setDescription("Connect to adresss")
        self.connectButton.setAutoDefault(True)
        self.connectButton.setDefault(True)
        self.ipInput.returnPressed.connect(self.connectButton.click)
        self.connectButton.clicked.connect(self.Connection)
        self.MainLayout.addWidget(self.connectButton,2,1,1,4)
    
        self.Thread:QThread=None
        self.worker:NMapConnect=None
        
        self.progressBar=QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

        self.progressLabel=QLabel("Scanning")
        self.progressLabel.setVisible(False)

        self.cancelButton=QPushButton("Cancel")
        self.cancelButton.setVisible(False)

        
        self.MainLayout.addWidget(self.progressLabel,1,1,1,1)
        self.MainLayout.addWidget(self.progressBar,1,3,1,1)
        self.MainLayout.addWidget(self.cancelButton,1,4,1,1)

        
        self.Logs=QTextEdit()
        self.Logs.setReadOnly(True)
        self.Logs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.MainLayout.addWidget(self.Logs,3,1,1,4)

    def UploadCheckData(self,checkdata:CheckData):self.checkData=checkdata


    def on_data_changed(self):pass

    def FillToIpInput(self):self.ipInput.setText(self.comboBox.currentText())

    def Connection(self):
        import ipaddress
        target=self.ipInput.text().strip()
        if not target:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Enter Network","Please Enter Network Address (e.g. 192.168.1.0/24)")
            self.ipInput.setStyleSheet("")
            return
        
        try:
            
            ipaddress.ip_network(target, strict=False)
        except ValueError:
            self.ipInput.setStyleSheet("QLineEdit {border: 2px solid red;}")
            QMessageBox.warning(self,"Invalid Network","Please Enter a Valid Network Address (e.g. 192.168.1.0/24)")
            self.ipInput.setStyleSheet("")
            return
        try:
            if self.Thread:
                try:
                    if self.Thread.isRunning():self.worker.stop();self.Thread.quit();self.Thread.wait(timeout=1000)
                except RuntimeError:pass
                self.Thread=None
        except:self.Thread=None
        
        self.worker=NMapConnect(target=target)
        self.Thread=QThread()
        self.worker.moveToThread(self.Thread)
        self.Thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.updateProgress)
        self.worker.finished.connect(self.scanFinished)
        self.worker.line.connect(self.GetLineLog)
        self.worker.ips.connect(self.sendFoundedIps)
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

    def sendFoundedIps(self,ips:List[str]):
        self.checkData.data.founded_ips=ips
        self.checkData.changed_founded_ips.emit(ips)

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

        
        