from core.dataTypes import *
from YoungLion import File

class DataManager(File):
    def __init__(self):
        super().__init__(filefolder="./data", debug=True, debugger=None)
    def settings(self,progress:bool=False,data:Settings=None)->Settings:
        return Settings(self.json_read("settings.json")) if not progress else self.json_write("settings.json",data.to_dict())
    def loadStyle(self,style:str):
        return self.rtf_read(f"./styles/{style}.qss")