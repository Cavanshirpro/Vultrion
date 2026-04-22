from core.dataTypes import *

for k,v in Settings.Keyevent.Methods.MetaData.__dict__.items():
    if k.startswith('_'):continue
    print(f"\033[32m{k}:\033[33m{isinstance(v,MetaData)}\033[0m")