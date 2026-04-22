import sys,ctypes,os
from core.dataTypes import *
from ctypes import wintypes
from pathlib import Path

IS_WINDOWS=sys.platform.startswith("win")
IS_LINUX=sys.platform.startswith("linux")
IS_MAC=sys.platform=="darwin"

user32:ctypes.WinDLL=ctypes.windll.user32 if IS_WINDOWS else None

GWL_STYLE=-16
WS_CHILD=0x40000000
WS_POPUP=0x80000000
WS_CAPTION=0x00C00000
WS_SYSMENU=0x00080000
WS_THICKFRAME=0x00040000
WS_MINIMIZEBOX=0x00020000
WS_MAXIMIZEBOX=0x00010000

SW_SHOW=5

EnumWindowsProc=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM) if IS_WINDOWS else None

def find_window_by_pid_windows(pid:int)->bool|None:
    if not IS_WINDOWS:return None
    found=[]
    @EnumWindowsProc
    def enum_proc(hwnd,lparam):
        if not user32.IsWindowVisible(hwnd):return True
        window_pid=wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd,ctypes.byref(window_pid))
        if window_pid.value!=pid:return True
        length=user32.GetWindowTextLengthW(hwnd)
        if length>0:found.append(int(hwnd));return False
        return True
    user32.EnumWindows(enum_proc,0)
    return found[0] if found else None

def find_window_by_pid_x11(pid:int):
    if not IS_LINUX:return None

    if os.environ.get("WAYLAND_DISPLAY") and not os.environ.get("DISPLAY"):return None

    try:from Xlib import X,display
    except Exception:return None

    try:
        d=display.Display()
        root=d.screen().root
        pid_atom=d.intern_atom("_NET_WM_PID")
        queue=[root]
        visited=set()
        while queue:
            w=queue.pop(0)
            if w.id in visited:continue
            visited.add(w.id)
            try:
                prop=w.get_full_property(pid_atom,X.AnyPropertyType)
                if prop and prop.value and int(prop.value[0])==pid:return int(w.id)
            except Exception:pass

            try:
                children=w.query_tree().children
                queue.extend(children)
            except Exception:pass
    except Exception:return None
    return None


def find_native_window_by_pid(pid:int):
    if IS_WINDOWS:return find_window_by_pid_windows(pid)
    if IS_LINUX:return find_window_by_pid_x11(pid)
    return None

class ScrcpyDock(QDockWidget):
    def __init__(
        self,scrcpy_program:str,*,capture_orientation_lock:bool=True,
        display_orientation:Union[str,None]=None,
        angle:Union[int,None]=None,):
        super().__init__("Scrcpy")
        self.scrcpy_program=str(Path(scrcpy_program).resolve()) if Path(scrcpy_program).exists() else scrcpy_program
        self.capture_orientation_lock=capture_orientation_lock
        self.display_orientation=display_orientation
        self.angle=angle
        self.scrcpy_hwnd=None
        self.embedded_window=None
        self._closing=False
        self._attached=False
        self.host=QWidget()
        self.host.setLayout(QVBoxLayout())
        self.host.layout().setContentsMargins(0,0,0,0)
        self.host.layout().setSpacing(0)
        self.host.installEventFilter(self)
        self.setWidget(self.host)
        self.status=QLabel("Scrcpy starting...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.host.layout().addWidget(self.status)
        self.process=QProcess(self)
        self.process.setProgram(self.scrcpy_program)
        self.process.finished.connect(self._on_process_finished)
        self.attach_timer=QTimer(self)
        self.attach_timer.setInterval(100)
        self.attach_timer.timeout.connect(self.try_attach)
        self.health_timer=QTimer(self)
        self.health_timer.setInterval(500)
        self.health_timer.timeout.connect(self.ensure_alive)
    def build_args(self):
        args=[]
        if self.capture_orientation_lock:args.append("--capture-orientation=@")
        if self.display_orientation is not None:args.append(f"--display-orientation={self.display_orientation}")
        if self.angle is not None: args.append(f"--angle={self.angle}")
        return args
    def start(self):
        if self.process.state()!=QProcess.ProcessState.NotRunning:return
        self.process.start(self.scrcpy_program,self.build_args())
        if not self.process.waitForStarted(5000):raise RuntimeError(f"scrcpy failed to start:{self.scrcpy_program}")
        self.attach_timer.start()
        self.health_timer.start()
        self.status.setText("Waiting for the window......")

    def try_attach(self):
        if self._closing or self._attached:return
        if self.process.state()!=QProcess.ProcessState.Running:return
        pid=int(self.process.processId())
        native_id=find_native_window_by_pid(pid)
        if not native_id:return

        qwindow=QWindow.fromWinId(native_id)
        if qwindow is None:return self.status.setText("This platform does not support foreign window embedding.")

        self.scrcpy_hwnd=native_id

        lay=self.host.layout()
        while lay.count():
            item=lay.takeAt(0)
            w=item.widget()
            if w:w.setParent(None)

        self.embedded_window=qwindow
        self.container=QWidget.createWindowContainer(qwindow,self.host)
        self.container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        lay.addWidget(self.container)

        if IS_WINDOWS:
            try:
                style=user32.GetWindowLongW(native_id,GWL_STYLE)
                style&=~(WS_POPUP|WS_CAPTION|WS_SYSMENU|WS_THICKFRAME|WS_MINIMIZEBOX|WS_MAXIMIZEBOX)
                style|=WS_CHILD
                user32.SetWindowLongW(native_id,GWL_STYLE,style)
            except Exception:pass
            try:user32.ShowWindow(native_id,SW_SHOW)
            except Exception:pass

        self._attached=True
        self.status.hide()

        QTimer.singleShot(0,self.sync_geometry)

    def sync_geometry(self):
        if not self._attached:return
        if self.container:self.container.updateGeometry()
        if self.embedded_window:
            self.embedded_window.resize(self.host.size())
            self.embedded_window.setGeometry(0,0,self.host.width(),self.host.height())

    def ensure_alive(self):
        if self._closing:return

        if self._attached:
            if self.scrcpy_hwnd is None:return
            if IS_WINDOWS and user32 and not user32.IsWindow(self.scrcpy_hwnd):return self._reset_and_retry()
            self.sync_geometry()
            return

        self.try_attach()

    def _reset_and_retry(self):
        self._attached=False
        self.scrcpy_hwnd=None
        self.embedded_window=None

        lay=self.host.layout()
        while lay.count():
            item=lay.takeAt(0)
            w=item.widget()
            if w:w.setParent(None)

        self.status.setText("Bağlantı koptu,yeniden deneniyor...")
        self.status.show()

    def eventFilter(self,obj,event):
        if obj is self.host and event.type()==QEvent.Type.Resize:self.sync_geometry()
        return super().eventFilter(obj,event)

    def closeEvent(self,event):
        self._closing=True
        self.attach_timer.stop()
        self.health_timer.stop()

        if self.process.state()==QProcess.ProcessState.Running:
            self.process.terminate()
            if not self.process.waitForFinished(2500):
                self.process.kill()
                self.process.waitForFinished(1500)

        super().closeEvent(event)

    def _on_process_finished(self):
        self._attached=False
        self.scrcpy_hwnd=None
        self.embedded_window=None
