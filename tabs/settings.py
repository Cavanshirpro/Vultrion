import platform,shutil,os
from core.dataTypes import *
from core.requests import DataManager


class SettingsTab(QWidget):
    def __init__(self,parent,checkdata:Optional[CheckData],dataManagerRequest:DataManager):
        super().__init__(parent)
        self.setObjectName("SettingsTab")
        self.MainLayout=QGridLayout(self)
        self.setLayout(self.MainLayout)
        self.checkData=checkdata
        self.checkData.changed.connect(self.on_data_changed)
        self.dataManager=dataManagerRequest
        self.dataManager.response.settings.connect(self.get_settings)

        self.settings:Settings=None

        # ADB Path
        self.adbPathLabel=QLabel("<h1>ADB Path:</h1>")
        self.adbPathLabel.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.MainLayout.addWidget(self.adbPathLabel,0,1,1,1)

        self.adbPathLine=QLineEdit()
        self.adbPathLine.setToolTip("Path to Android SDK platform-tools directory (contains adb executable)")
        self.adbPathLine.setWhatsThis("<h2>ADB Path Configuration</h2><p>This field displays the location of Android SDK platform-tools. The program requires ADB (Android Debug Bridge) to connect to and manage Android devices. Use 'Auto Find' to automatically detect it or 'Change' to manually select the path.</p>")
        self.adbPathLine.setEnabled(False)
        self.MainLayout.addWidget(self.adbPathLine,0,2,1,1)

        self.adbChangePathQPushButton=QPushButton("Change")
        self.adbChangePathQPushButton.setToolTip("Select ADB path manually")
        self.adbChangePathQPushButton.setWhatsThis("Manually browse and select the path to Android SDK platform-tools directory")
        self.adbChangePathQPushButton.setStatusTip("Click to choose ADB path")
        self.adbChangePathQPushButton.clicked.connect(self.adbChangePath)
        self.MainLayout.addWidget(self.adbChangePathQPushButton,0,3,1,1)

        self.adbAutoFindQPushButton=QPushButton("Auto Find")
        self.adbAutoFindQPushButton.setToolTip("Automatically search for ADB installation")
        self.adbAutoFindQPushButton.setWhatsThis("Searches common Android SDK paths and system PATH for ADB installation")
        self.adbAutoFindQPushButton.setStatusTip("Click to auto-detect ADB")
        self.adbAutoFindQPushButton.clicked.connect(self.adbAutoFind)
        self.MainLayout.addWidget(self.adbAutoFindQPushButton,0,4,1,1)

        # Keyevent Method
        self.keyeventMethodGroupBox=QGroupBox("Keyevent Method",self)
        self.keyeventMethodGroupBox.setToolTip("Select keyevent execution method")
        self.keyeventMethodGroupBox.setWhatsThis("<h2>Keyevent Execution Methods</h2><p>Choose how to execute keyevents across multiple devices. Different methods offer varying levels of parallelism and resource usage.</p>")
        self.keyeventMethodGroupBox.setLayout(QVBoxLayout(self.keyeventMethodGroupBox))
        self.MainLayout.addWidget(self.keyeventMethodGroupBox,1,1,1,4)

        self.keyeventMethodListWidget=QListWidget()
        self.keyeventMethodListWidget.setSelectionMode(self.keyeventMethodListWidget.SelectionMode.SingleSelection)
        self.keyeventMethodListWidget.setToolTip("Available keyevent execution strategies")
        self.keyeventMethodListWidget.setWhatsThis("Select the execution method that best suits your needs. Hover over each option to see its details.")
        self.keyeventMethodGroupBox.layout().addWidget(self.keyeventMethodListWidget)
        self.keyeventMethodButtonGroup=QButtonGroup()
        self.keyeventMethodButtonGroup.setExclusive(True)
        self.keyeventMethodButtonGroup.buttonClicked.connect(lambda btn: self.changeKeyEventMethod(btn))


        self.dataManager.read.settings.emit()
    

    def get_settings(self,data:Settings):
        self.settings=data

        self.checkData.data.did_adb_work=os.path.exists(self.settings.adb_path)
        self.checkData.data.choosen_path_for_adb=self.settings.adb_path
        self.checkData.data.keyeventMethod=self.settings.keyevent.method

        self.checkData.changed_choosen_path_for_adb.emit(self.settings.adb_path)
        self.checkData.changed_did_adb_work.emit(self.checkData.data.did_adb_work)
        self.checkData.changed_keyeventMethod.emit(self.settings.keyevent.method)
        self.checkData.changed.emit()
        
        self.adbPathLine.setText(self.settings.adb_path)
        self.adbPathLine.setStatusTip(self.settings.adb_path)
        self.keyeventMethodListWidget.clear()
        for key,method in Settings.Keyevent.Methods.MetaData.__dict__.items():
            if key.startswith("_"):continue
            item=QListWidgetItem()
            radio=QRadioButton(method.name)
            self.keyeventMethodButtonGroup.addButton(radio)
            if key==self.settings.keyevent.method:radio.setChecked(True)
            radio.setToolTip(f"<h2>{method.brief}</h2>\n{method.description}")
            radio.setStatusTip(method.brief)
            radio.setWhatsThis(method.description)
            item.setData(Qt.ItemDataRole.UserRole,key)
            self.keyeventMethodListWidget.addItem(item)
            self.keyeventMethodListWidget.setItemWidget(item,radio)

    def changeKeyEventMethod(self,button:QRadioButton):
        for i in range(self.keyeventMethodListWidget.count()):
            item=self.keyeventMethodListWidget.item(i)
            widget=self.keyeventMethodListWidget.itemWidget(item)
            if widget==button:method=item.data(Qt.ItemDataRole.UserRole)
            
        self.checkData.data.keyeventMethod=method
        self.settings.keyevent.method=method
        self.dataManager.write.settings.emit(self.settings)
        self.checkData.changed_keyeventMethod.emit(method)
        self.checkData.changed.emit()
        
        
    def on_data_changed(self):pass
    def try_find_adb(self):
        system=platform.system()
        found_path=None

        if system == "Windows":
            tries=[
                "C:/platform-tools/adb.exe",
                "C:/Android/platform-tools/adb.exe",
                "C:/Users/Public/Android/platform-tools/adb.exe",
                os.path.expanduser("~") + "/AppData/Local/Android/Sdk/platform-tools/adb.exe",
                os.path.expanduser("~") + "/AppData/Local/Android/platform-tools/adb.exe",
                "C:/Program Files/Android/android-sdk/platform-tools/adb.exe",
                "C:/Program Files (x86)/Android/android-sdk/platform-tools/adb.exe",
                shutil.which("adb.exe") or "adb.exe"
            ]
        else:
            tries=[
                shutil.which("adb"),
                "adb",
                os.path.expanduser("~") + "/Android/Sdk/platform-tools/adb",
                os.path.expanduser("~") + "/Library/Android/sdk/platform-tools/adb",
                "/usr/bin/adb",
                "/usr/local/bin/adb",
                "/opt/android-sdk/platform-tools/adb",
                "/opt/android/platform-tools/adb",
                "/snap/bin/adb",
            ]
        tries=list(set(t for t in tries if t is not None))
        
        for path in tries:
            try:
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    found_path=path
                    break
                elif path.endswith('adb') and not path.endswith('.exe') and system == "Windows":
                    exe_path=path + ".exe"
                    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                        found_path=exe_path
                        break
            except (OSError, IOError):
                continue

        if found_path:
            return os.path.dirname(os.path.normpath(found_path))
        return None
            
                
    def adbAutoFind(self):
        found_path=self.try_find_adb()
        if found_path:
            
            self.settings.adb_path=found_path
            self.dataManager.write.settings.emit(self.settings)
            
            self.adbPathLine.setText(found_path)
            self.adbPathLine.setStatusTip(found_path)

            self.checkData.data.did_adb_work=True
            self.checkData.data.choosen_path_for_adb=found_path
            self.checkData.changed_did_adb_work.emit(True)
            self.checkData.changed_choosen_path_for_adb.emit(found_path)
            self.checkData.changed.emit()
            
            
            QMessageBox.information(self, "ADB Found", f"ADB found at:\n{found_path}")
        else:
            
            QMessageBox.warning(self, "ADB Not Found", 
                              "ADB could not be found automatically.\n\n"
                              "Please install Android SDK/platform-tools or specify the path manually.")
                
    def adbChangePath(self):
        folder=QFileDialog.getExistingDirectory(
            self,
            "Select Folder For Adb",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        self.settings.adb_path=folder
        self.dataManager.write.settings.emit(self.settings)
        self.adbPathLine.setText(folder)
        self.adbPathLine.setStatusTip(folder)
        self.checkData.data.did_adb_work=os.path.exists(self.settings.adb_path)
        self.checkData.data.choosen_path_for_adb=self.settings.adb_path
        self.checkData.changed_did_adb_work.emit(self.checkData.data.did_adb_work)
        self.checkData.changed_choosen_path_for_adb.emit(self.settings.adb_path)
        self.checkData.changed.emit()
