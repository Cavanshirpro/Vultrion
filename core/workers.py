from core.dataTypes import *
import subprocess,ipaddress
from PySide6.QtCore import QObject,Signal,Slot
import os

def get_total_ips(cidr:str) -> int:
    try:
        net=ipaddress.ip_network(cidr,strict=False)
        return len(list(net.hosts()))
    except Exception:
        return 0


class NMapConnect(QObject):
    ips=Signal(list)
    failedIps=Signal(list)
    progress=Signal(int)
    finished=Signal()
    line=Signal(str)

    def __init__(self,target="192.168.1.0/24",parent=None):
        super().__init__(parent)
        self.target=target
        self._process=None
        self._running=False

    def setTarget(self,target:str):self.target=target

    def stop(self):
        self._running=False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:self._process.kill()
                except Exception:pass
                

    @Slot()
    def run(self):
        reachable=[]
        unreachable=[]
        self._running=True
        self.line.emit(f"Starting nmap scan for {self.target}")
        try:
            self._process=subprocess.Popen(
                ["nmap","-sn",self.target,"-oN","-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            for line in iter(self._process.stdout.readline,''):
                if not self._running:break
                line=line.strip()
                self.line.emit(line)
                if "Nmap scan report for" in line:
                    parts=line.split()
                    ip=parts[-1]
                    reachable.append(ip)
                    self.progress.emit(len(reachable))

                # İstersen debug için aç:
                #print(line)


            # proses bitmesini bekle
            self._process.wait()
            self.line.emit("Nmap scan completed")
            err=self._process.stderr.read()
            if err:self.line.emit(f"Nmap stderr:{err}")

        except Exception as e:
            self.line.emit(f"Nmap subprocess error:{e}")

        finally:
            self.ips.emit(reachable)
            self.failedIps.emit(unreachable)
            self.finished.emit()


class ADBConnect(QObject):
    ips=Signal(list)
    failedIps=Signal(list)
    progress=Signal(int)
    finished=Signal()
    line=Signal(str)
    
    def __init__(self,adb_path:Optional[str]=None,target:Optional[str]=None,checkData:CheckData=None,parent=None):
        super().__init__(parent)
        self.target=target
        self.adb_path=adb_path
        self.checkData=checkData
        self._process=None
        self._running=False

    def setTarget(self,target:str):self.target=target

    def stop(self):
        self._running=False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:self._process.kill()
                except Exception:pass

    @Slot()
    def run(self):
        reachable=[]
        unreachable=[]
        self._running=True
        if os.name=='nt':
            si=subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow=0
        try:
            self._process=subprocess.Popen(
                [self.adb_path+'/adb.exe',"connect",self.target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=si
            )
            for line in iter(self._process.stdout.readline,''):
                if not self._running:break
                line=line.strip()
                if line:
                    self.line.emit(line)
                    if "error" in line.lower() or "refused" in line.lower() or 'cannot' in line.lower():
                        unreachable.append(self.target)
                    elif "connected to" in line.lower():
                        ip=self.target
                        reachable.append(ip)
                        self.progress.emit(len(reachable))
                        self.checkData.data.connected_devices.append(ConnectedDevice({"serial":ip,"type":ConnectedDevice.TCPIP}))
                        self.checkData.data.connected_devices=list(set(self.checkData.data.connected_devices))
                        self.checkData.changed_connected_devices.emit(self.checkData.data.connected_devices)
            self._process.wait()
            err=self._process.stderr.read()
            if err:
                self.line.emit(f"ADB stderr:{err}")
                if not unreachable and not reachable:unreachable.append(self.target)
        except Exception as e:
            self.line.emit(f"ADB subprocess error:{e}")
            unreachable.append(self.target)
        finally:
            self.ips.emit(reachable)
            self.failedIps.emit(unreachable)
            self.finished.emit()

class ADBDisconnect(QObject):
    ips=Signal(list)
    failedIps=Signal(list)
    progress=Signal(int)
    finished=Signal()
    line=Signal(str)
    
    def __init__(self,adb_path:Optional[str]=None,target:Optional[str]=None,checkData:CheckData=None,parent=None):
        super().__init__(parent)
        self.target=target
        self.adb_path=adb_path
        self.checkData=checkData
        self._process=None
        self._running=False

    def setTarget(self,target:str):self.target=target

    def stop(self):
        self._running=False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:self._process.kill()
                except Exception:pass

    @Slot()
    def run(self):
        reachable=[]
        unreachable=[]
        self._running=True
        if os.name=='nt':
            si=subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow=0
        try:
            self._process=subprocess.Popen(
                [self.adb_path+'/adb.exe',"disconnect",self.target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=si
            )
            for line in iter(self._process.stdout.readline,''):
                if not self._running:break
                line=line.strip()
                if line:
                    self.line.emit(line)
                    if "disconnected" in line.lower():
                        ip=self.target
                        reachable.append(ip)
                        self.progress.emit(len(reachable))
                        self.checkData.data.connected_devices.remove(ConnectedDevice({"serial":ip,"type":ConnectedDevice.TCPIP}))
                        self.checkData.changed_connected_devices.emit(self.checkData.data.connected_devices)
                    elif "error" in line.lower() or "refused" in line.lower():
                        unreachable.append(self.target)
            self._process.wait()
            err=self._process.stderr.read()
            if err:
                self.line.emit(f"ADB stderr:{err}")
                if not unreachable and not reachable:unreachable.append(self.target)
        except Exception as e:
            self.line.emit(f"ADB subprocess error:{e}")
            unreachable.append(self.target)
        finally:
            self.ips.emit(reachable)
            self.failedIps.emit(unreachable)
            self.finished.emit()

class ScanDevices(QObject):
    devices=Signal(list)
    finished=Signal()
    line=Signal(str)

    def __init__(self,adb_path:str=None,checkData:CheckData=None):
        super().__init__(objectName="ScanDevices")
        self.adb_path=adb_path
        self.checkData=checkData
        self._process=None
        self._running=False

    def stop(self):
        self._running=False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:self._process.kill()
                except Exception:pass

    @Slot()
    def run(self):
        result:list[ConnectedDevice]=[]
        self._running=True

        if os.name=='nt':
            si=subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow=0
        else:si=None

        try:
            self._process=subprocess.Popen(
                [self.adb_path + '/adb.exe',"devices","-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=si
            )

            for raw_line in iter(self._process.stdout.readline,''):
                if not self._running:break

                line=raw_line.strip()
                if not line:continue

                self.line.emit(line)

                if line.startswith("List of devices"):continue

                parts=line.split()
                if len(parts)<2:continue

                serial=parts[0]
                state=parts[1]

                data={
                    "serial":serial,
                    "state":state,
                    "type":ConnectedDevice.Types.TCPIP if ":" in serial else ConnectedDevice.Types.USB
                }

                for item in parts[2:]:
                    if ":" not in item:continue
                    k,v=item.split(":",1)
                    data[k]=v

                device=ConnectedDevice(data)
                result.append(device)

            self._process.wait()

            err=self._process.stderr.read()
            if err:self.line.emit(f"ADB stderr:{err}")

        except Exception as e:self.line.emit(f"ADB subprocess error:{e}")

        finally:
            result=list({d.serial:d for d in result}.values())

            if self.checkData:
                self.checkData.data.connected_devices=result
                self.checkData.changed_connected_devices.emit(result)

            self.devices.emit(result)
            self.finished.emit()

