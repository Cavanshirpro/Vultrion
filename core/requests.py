from core.dataTypes import *

class DataManagerRead(QObject):
    settings=Signal()
    style=Signal(str,str)
    keyeventList=Signal()
class DataManagerWrite(QObject):
    settings=Signal(Settings)
class DataManagerResponse(QObject):
    settings=Signal(Settings)
    style=Signal(str,str)
    keyeventList=Signal(str)

class DataManager(QObject):
    def __init__(self,parent):
        super().__init__(parent, objectName="DataManagerRequests")
        self.read=DataManagerRead(parent=self)
        self.write=DataManagerWrite(parent=self)
        self.response=DataManagerResponse(parent=self)
        
