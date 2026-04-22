from core.dataTypes import *
from ui.keyeventItem import KeyEventItem
from core.requests import DataManager
from core.keyevent import KeyeventDefinition,KeyeventQObjectWorker,KeyeventQRunnableWorker,load_keyevent_definitions


class KeyEventsTab(QWidget):
    KEYEVENT_ROLE=Qt.ItemDataRole.UserRole

    def __init__(self,parent,checkdata:Optional[CheckData],dataManagerRequest:DataManager):
        super().__init__(parent)
        self.setObjectName("KeyEventTab")
        self.MainLayout=QGridLayout(self)
        self.setLayout(self.MainLayout)
        self.checkData=checkdata
        self.checkData.changed.connect(self.on_data_changed)
        self.checkData.changed_connected_devices.connect(self.UpdateConnectedDevices)
        self.dataManager=dataManagerRequest
        self.dataManager.response.keyeventList.connect(self._on_keyevent_list_loaded)

        self.settings:Settings=None
        self._searchTimer=QTimer(self)
        self._searchTimer.setSingleShot(True)
        self._searchTimer.setInterval(140)
        self._searchTimer.timeout.connect(self.searchKeyevent)
        self._allKeyevents:Tuple[KeyeventDefinition,...]=tuple()
        self._visibleKeyevents:Tuple[KeyeventDefinition,...]=tuple()

        self.searchInput=QLineEdit(self)
        self.searchInput.setPlaceholderText("Search Keyevent...")
        self.searchInput.setClearButtonEnabled(True)
        self.searchInput.returnPressed.connect(self.searchKeyevent)
        self.searchInput.textChanged.connect(self._scheduleSearch)
        self.MainLayout.addWidget(self.searchInput,0,0,1,1)

        self.comboBox=QComboBox(self)
        self.comboBox.setEnabled(False)
        self.MainLayout.addWidget(self.comboBox,0,1,1,1)

        self.keyeventList=QListWidget(self)
        self.keyeventList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.keyeventList.setUniformItemSizes(True)
        self.keyeventList.setAlternatingRowColors(True)
        self.keyeventList.setWordWrap(False)
        self.keyeventList.setLayoutMode(QListView.LayoutMode.Batched)
        self.keyeventList.setBatchSize(48)
        self.keyeventList.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.MainLayout.addWidget(self.keyeventList,1,0,2,2)

        self.Logs=QTextEdit()
        self.Logs.setReadOnly(True)
        self.Logs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.Logs.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.MainLayout.addWidget(self.Logs,2,2,1,1)

        self.SelectedDevice:List[ConnectedDevice]=[]
        self.ConnectedIps=QListView(self)
        self.ConnectedIps.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.ConnectedIpsModel=QStandardItemModel()
        self.ConnectedIpsModel.itemChanged.connect(self.on_item_changed)
        self.ConnectedIps.setModel(self.ConnectedIpsModel)
        self.MainLayout.addWidget(self.ConnectedIps,0,2,2,1)

        self.DTPThreads:List[QThread]=[]
        self.DTPQObject:List[KeyeventQObjectWorker]=[]
        self.SWQThread:QThread=None
        self.SWQWorkers:List[KeyeventQObjectWorker]=[]
        self.ThreadPool:QThreadPool=None
        self.Runables:List[KeyeventQRunnableWorker]=[]

        self.loadKeyevents()

    def on_data_changed(self):pass

    def _scheduleSearch(self):
        self._searchTimer.start()

    def _loadSettings(self):
        loop=QEventLoop()

        def handle_settings(settings:Settings):
            self.settings=settings
            loop.quit()

        self.dataManager.response.settings.connect(handle_settings)
        QTimer.singleShot(0,self.dataManager.read.settings.emit)
        loop.exec()
        self.dataManager.response.settings.disconnect(handle_settings)

    def _requestKeyeventList(self):
        loop=QEventLoop()
        holder={"text":""}

        def handle_keyevents(source_text:str):
            holder["text"]=source_text
            loop.quit()

        self.dataManager.response.keyeventList.connect(handle_keyevents)
        QTimer.singleShot(0,self.dataManager.read.keyeventList.emit)
        loop.exec()
        self.dataManager.response.keyeventList.disconnect(handle_keyevents)
        return holder["text"]

    def _on_keyevent_list_loaded(self,_source_text:str):
        pass

    def _matchesQuery(self,keyevent:KeyeventDefinition,query:str) -> bool:
        if not query:
            return True
        searchable=f"{keyevent.code} {keyevent.name} {keyevent.description}".lower()
        return query in searchable

    def _updateSummary(self):
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        self.comboBox.addItem(f"{len(self._visibleKeyevents)} / {len(self._allKeyevents)} keyevents")
        self.comboBox.blockSignals(False)

    def _appendLog(self,line:str,keyeventWidget:Optional[KeyEventItem]=None):
        self.Logs.append(line)
        if keyeventWidget is not None:
            keyeventWidget.Logs.append(line)

    def _createKeyeventWidget(self,keyevent:KeyeventDefinition) -> KeyEventItem:
        widget=KeyEventItem(keyevent.name,keyevent.description)
        widget.EnterButton.setWhatsThis(keyevent.whats_this)
        widget.EnterButton.setToolTip(keyevent.description)
        widget.EnterButton.setStatusTip(f"Click to execute {keyevent.name} ({keyevent.code})")
        widget.EnterButton.clicked.connect(lambda _checked=False,k=keyevent,w=widget:self.RunKeyEvent(k,w))
        return widget

    def _addKeyeventToList(self,keyevent:KeyeventDefinition):
        item=QListWidgetItem(self.keyeventList)
        item.setData(self.KEYEVENT_ROLE,keyevent)
        item.setToolTip(keyevent.description)
        item.setStatusTip(keyevent.description)
        item.setWhatsThis(keyevent.whats_this)
        item.setData(Qt.ItemDataRole.WhatsThisRole,keyevent.whats_this)
        item.setSizeHint(QSize(800,120))
        widget=self._createKeyeventWidget(keyevent)
        widget.setWhatsThis(keyevent.whats_this)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.keyeventList.addItem(item)
        self.keyeventList.setItemWidget(item,widget)

    def _eligibleDevices(self) -> list[ConnectedDevice]:
        return [device for device in self.SelectedDevice if device.state == ConnectedDevice.States.DEVICE]

    def loadKeyevents(self):
        try:
            self._allKeyevents=load_keyevent_definitions(self._requestKeyeventList())
            self._visibleKeyevents=self._allKeyevents
        except Exception as error:
            self._allKeyevents=tuple()
            self._visibleKeyevents=tuple()
            self.Logs.append(f"Keyevent list load error:{error}")

        self.keyeventList.setUpdatesEnabled(False)
        self.keyeventList.blockSignals(True)
        self.keyeventList.clear()
        for keyevent in self._visibleKeyevents:
            self._addKeyeventToList(keyevent)
        self.keyeventList.blockSignals(False)
        self.keyeventList.setUpdatesEnabled(True)
        self._updateSummary()

    def RunKeyEvent(self,keyevent:Optional[KeyeventDefinition]=None,keyeventWidget:Optional[KeyEventItem]=None):
        if keyevent is None:
            return

        self._loadSettings()
        eligible_devices=self._eligibleDevices()
        if not self.settings or not eligible_devices:
            return

        start_message=f"Executing {keyevent.display_name} on {len(eligible_devices)} device(s)..."
        self._appendLog(start_message,keyeventWidget)

        if self.settings.keyevent.method == Settings.Keyevent.Methods.DedicatedThreadPerWorker:
            return self.RunKeyEventDedicatedThreadPerWorker(keyevent,eligible_devices,keyeventWidget)
        if self.settings.keyevent.method == Settings.Keyevent.Methods.SequentialWorkerQueue:
            return self.RunKeyEventSequentialWorkerQueue(keyevent,eligible_devices,keyeventWidget)
        return self.RunKeyEventThreadPool(keyevent,eligible_devices,keyeventWidget)

    def RunKeyEventDedicatedThreadPerWorker(self,keyevent:KeyeventDefinition,devices:list[ConnectedDevice],keyeventWidget:Optional[KeyEventItem]=None):
        self.DTPThreads=[]
        self.DTPQObject=[]

        for device in devices:
            thread=QThread(self)
            self.DTPThreads.append(thread)

            worker=KeyeventQObjectWorker(
                adb_path=self.settings.adb_path,
                target=device.serial,
                keycode=keyevent.code,
                keyevent_name=keyevent.name,
                checkData=self.checkData,
            )
            self.DTPQObject.append(worker)

            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(lambda t=thread:self._cleanup_thread(t))
            worker.line.connect(lambda line,widget=keyeventWidget:self._appendLog(line,widget))

            worker.moveToThread(thread)
            thread.finished.connect(thread.deleteLater)
            thread.started.connect(worker.run)
            thread.start()

    def RunKeyEventSequentialWorkerQueue(self,keyevent:KeyeventDefinition,devices:list[ConnectedDevice],keyeventWidget:Optional[KeyEventItem]=None):
        self.SWQThread=QThread(self)
        self.SWQWorkers=[]

        for device in devices:
            worker=KeyeventQObjectWorker(
                adb_path=self.settings.adb_path,
                target=device.serial,
                keycode=keyevent.code,
                keyevent_name=keyevent.name,
                checkData=self.checkData,
            )
            self.SWQWorkers.append(worker)
            worker.moveToThread(self.SWQThread)
            worker.finished.connect(worker.deleteLater)
            worker.line.connect(lambda line,widget=keyeventWidget:self._appendLog(line,widget))

        if not self.SWQWorkers:
            self.SWQThread.deleteLater()
            self.SWQThread=None
            return

        for index,worker in enumerate(self.SWQWorkers):
            if index == 0:
                self.SWQThread.started.connect(worker.run)
            else:
                self.SWQWorkers[index - 1].finished.connect(worker.run)

        self.SWQWorkers[-1].finished.connect(lambda:self._cleanup_thread_pool(self.SWQThread))
        self.SWQThread.finished.connect(self.SWQThread.deleteLater)
        self.SWQThread.start()

    def RunKeyEventThreadPool(self,keyevent:KeyeventDefinition,devices:list[ConnectedDevice],keyeventWidget:Optional[KeyEventItem]=None):
        self.ThreadPool=QThreadPool.globalInstance()
        self.Runables=[]
        completed_count=[0]
        total_count=len(devices)

        def on_complete(_success:bool,_message:str):
            completed_count[0] += 1
            if completed_count[0] == total_count:
                self._appendLog(f"=== {keyevent.display_name} completed ===",keyeventWidget)

        for device in devices:
            worker=KeyeventQRunnableWorker(
                adb_path=self.settings.adb_path,
                target=device.serial,
                keycode=keyevent.code,
                keyevent_name=keyevent.name,
                checkData=self.checkData,
            )

            worker.signal.line.connect(lambda line,widget=keyeventWidget:self._appendLog(line,widget))
            worker.signal.result.connect(on_complete)
            self.Runables.append(worker)
            self.ThreadPool.start(worker)

    def _cleanup_thread(self,thread):
        thread.quit()
        thread.wait()

    def _cleanup_thread_pool(self,thread):
        if thread is None:
            return
        thread.quit()
        thread.wait()
        if thread is self.SWQThread:
            self.SWQThread=None

    def searchKeyevent(self):
        query=self.searchInput.text().strip().lower()
        self._visibleKeyevents=tuple(
            keyevent for keyevent in self._allKeyevents if self._matchesQuery(keyevent,query)
        )

        self.keyeventList.setUpdatesEnabled(False)
        self.keyeventList.blockSignals(True)
        self.keyeventList.clear()
        for keyevent in self._visibleKeyevents:
            self._addKeyeventToList(keyevent)
        self.keyeventList.blockSignals(False)
        self.keyeventList.setUpdatesEnabled(True)
        self._updateSummary()

    def on_item_changed(self,item:QStandardItem):
        device=item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.SelectedDevice.append(device)
        elif device in self.SelectedDevice:
            self.SelectedDevice.remove(device)
        self.SelectedDevice=list(dict.fromkeys(self.SelectedDevice))

    def UpdateConnectedDevices(self,devices:List[ConnectedDevice]):
        self.ConnectedIpsModel.clear()
        for device in devices:
            item=QStandardItem(device.serial)
            item.setData(device,Qt.ItemDataRole.UserRole)
            item.setToolTip(device.__str__().replace('\033[0m','').replace('\033[32m','').replace('\033[34m',''))
            item.setStatusTip(f"Device:{device.device}\tState:{device.state}\tType:{device.type}")
            item.setCheckable(True)
            if device.state != ConnectedDevice.States.DEVICE:
                item.setEnabled(False)
            item.setCheckState(Qt.CheckState.Checked if device in self.SelectedDevice else Qt.CheckState.Unchecked)
            item.setEditable(False)
            if device.type == ConnectedDevice.Types.TCPIP:
                item.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWireless))
            elif device.type == ConnectedDevice.Types.USB:
                item.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.InsertLink))
            self.ConnectedIpsModel.appendRow(item)
