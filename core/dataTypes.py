from typing import *
from YoungLion import DDM
import time
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class Settings(DDM):
    def __init__(self,data):
        super().__init__(data)
        self.adb_path:str=data.get("adb_path",'./adb')

class ConnectedDevice(DDM):
    class Types:
        USB=0
        TCPIP=1
    class States:
        DEVICE="device"
        OFFLINE="offline"
        UNAUTHORIZED="unauthorized"
        RECOVERY="recovery"
        SIDELOAD="sideload"
        BOOTLOADER="bootloader"
        UNKNOWN="unknown"
    def __init__(self, data):
        super().__init__(data)
        self.serial:str=data.get("serial")
        self.type:int=data.get("type", self.Types.USB)
        self.state:str=data.get("state")
        self.product:str=data.get("product")
        self.model:str=data.get("model")
        self.device:str=data.get("device",self.States.UNKNOWN)
        self.transport_id:str=data.get("transport_id")

    def __hash__(self):
        return hash(self.serial)

    def __eq__(self, other):
        return isinstance(other, ConnectedDevice) and self.serial == other.serial

class checkData(DDM):
    def __init__(self,data):
        super().__init__(data)
        self.last_entered:float=data.get("last_entered",time.time())
        self.last_commands:List[str]=data.get('last_commands',[])
        self.founded_ips:List[str]=data.get("founded_ips",[])
        self.connected_devices:List[ConnectedDevice]=data.get('connected_devices',[])
        self.did_adb_work:bool=data.get("did_adb_work",False)
        self.choosen_language:str=data.get("choosen_language",'en')
        self.choosen_path_for_adb:str=data.get("choosen_path_for_adb",None)

class CheckData(QObject):
    changed=Signal()
    changed_last_entered=Signal(float)
    changed_last_commands=Signal(list)
    changed_founded_ips=Signal(list)
    changed_connected_devices=Signal(list)
    changed_did_adb_work=Signal(bool)
    changed_choosen_language=Signal(str)
    changed_choosen_path_for_adb=Signal(str)

    def __init__(self,data:checkData):
        super().__init__()
        self._data=data
        object.__setattr__(self,'_data',data)
    def __setattr__(self,name,value):
        if name=='_data':object.__setattr__(self,'_data',value)
        else:
            if hasattr(self._data,name):
                setattr(self._data,name,value)
                self.changed.emit()
            else:object.__setattr__(self,name,value)
    def __getattr__(self,name):
        if name=='_data':return object.__getattribute__(self,'_data')
        return getattr(self._data,name)
    @property
    def data(self):return self._data
    @data.setter
    def data(self,value):
        object.__setattr__(self,'_data',value)
        self.changed.emit()
    def checkDataChanged(self):self.changed.emit()