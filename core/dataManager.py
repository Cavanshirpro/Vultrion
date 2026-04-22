from core.dataTypes import *
from YoungLion import File
from pathlib import Path

class DataManager(File):
    def __init__(self):
        super().__init__(filefolder=None, debug=True, debugger=None)
        self.filefolder=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    def settings(self,progress:bool=False,data:Settings=None)->Settings:
        return Settings(self.json_read("settings.json")) if not progress else self.json_write("settings.json",data.to_dict())
    def loadStyle(self,style:str):
        return self.rtf_read(f"./styles/{style}.qss")
    def keyeventList(self)->str:
        source_path=Path(__file__).resolve().parent.parent / "source" / "keyeventList.txt"
        return source_path.read_text(encoding="utf-8")
