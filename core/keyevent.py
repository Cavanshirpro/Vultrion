from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core.dataTypes import *


@dataclass(frozen=True, slots=True)
class KeyeventDefinition:
    code: int
    name: str
    description: str
    whats_this: str

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.code})"


def _keyevent_source_path() -> Path:
    return Path(__file__).resolve().parent.parent / "source" / "keyeventList.txt"


def parse_keyevent_definitions(source_text: str) -> tuple[KeyeventDefinition, ...]:
    definitions: list[KeyeventDefinition] = []

    for line_number, raw_line in enumerate(source_text.splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue

        try:
            code_text, name, description, whats_this = line.split(":", 3)
        except ValueError as error:
            raise ValueError(f"Invalid keyevent definition at line {line_number}: {raw_line!r}") from error

        definitions.append(
            KeyeventDefinition(
                code=int(code_text),
                name=name.strip(),
                description=description.strip(),
                whats_this=whats_this.strip(),
            )
        )

    return tuple(definitions)


def load_keyevent_definitions(source_text: Optional[str] = None) -> tuple[KeyeventDefinition, ...]:
    if source_text is None:
        source_text = _keyevent_source_path().read_text(encoding="utf-8")
    return parse_keyevent_definitions(source_text)


def _get_adb_path(adb_path: str) -> str:
    adb_exec = "adb.exe" if platform.system() == "Windows" else "adb"
    normalized = os.path.normpath(adb_path)
    if os.path.isfile(normalized):
        return normalized
    return os.path.join(normalized, adb_exec)


def _get_startup_info():
    if platform.system() == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        return si
    return None


def _build_keyevent_command(adb_path: str, target: str, keycode: int | str) -> list[str]:
    return [_get_adb_path(adb_path), "-s", target, "shell", "input", "keyevent", str(keycode)]


class KeyeventQObjectWorker(QObject):
    finished = Signal()
    line = Signal(str)

    def __init__(
        self,
        adb_path: Optional[str] = None,
        target: Optional[str] = None,
        keycode: Optional[int] = None,
        keyevent_name: Optional[str] = None,
        checkData: CheckData = None,
        parent=None,
    ):
        super().__init__(parent)
        self.target = target
        self.keycode = keycode
        self.keyevent_name = keyevent_name or str(keycode)
        self.adb_path = adb_path
        self.checkData = checkData
        self._process = None
        self._running = False

    def setTarget(self, target: str):
        self.target = target

    def setKeyevent(self, keycode: int, keyevent_name: Optional[str] = None):
        self.keycode = keycode
        self.keyevent_name = keyevent_name or str(keycode)

    def stop(self):
        self._running = False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass

    @Slot()
    def run(self):
        self._running = True
        si = _get_startup_info()
        try:
            self._process = subprocess.Popen(
                _build_keyevent_command(self.adb_path, self.target, self.keycode),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=si,
            )
            for line in iter(self._process.stdout.readline, ""):
                if not self._running:
                    break
                line = line.strip()
                if line:
                    self.line.emit(line)

            return_code = self._process.wait()
            err = self._process.stderr.read().strip()
            if err:
                self.line.emit(f"{self.target}: {err}")
            elif return_code == 0:
                self.line.emit(f"{self.target}: [OK] {self.keyevent_name} ({self.keycode})")
            else:
                self.line.emit(f"{self.target}: {self.keyevent_name} ({self.keycode}) failed with exit code {return_code}")
        except Exception as error:
            self.line.emit(f"{self.target}: ADB subprocess error: {error}")
        finally:
            self.finished.emit()


class KeyeventQRunnableSignal(QObject):
    finished = Signal()
    line = Signal(str)
    result = Signal(bool, str)


class KeyeventQRunnableWorker(QRunnable):
    def __init__(
        self,
        adb_path: Optional[str] = None,
        target: Optional[str] = None,
        keycode: Optional[int] = None,
        keyevent_name: Optional[str] = None,
        checkData: CheckData = None,
        parent=None,
    ):
        super().__init__()
        self.target = target
        self.keycode = keycode
        self.keyevent_name = keyevent_name or str(keycode)
        self.adb_path = adb_path
        self.checkData = checkData
        self._process = None
        self._running = False
        self.signal = KeyeventQRunnableSignal()

    def setTarget(self, target: str):
        self.target = target

    def setKeyevent(self, keycode: int, keyevent_name: Optional[str] = None):
        self.keycode = keycode
        self.keyevent_name = keyevent_name or str(keycode)

    def stop(self):
        self._running = False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass

    def run(self):
        self._running = True
        si = _get_startup_info()
        try:
            self._process = subprocess.Popen(
                _build_keyevent_command(self.adb_path, self.target, self.keycode),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=si,
            )
            for line in iter(self._process.stdout.readline, ""):
                if not self._running:
                    break
                line = line.strip()
                if line:
                    self.signal.line.emit(line)

            return_code = self._process.wait()
            err = self._process.stderr.read().strip()
            if err:
                message = f"{self.target}: {err}"
                self.signal.line.emit(message)
                self.signal.result.emit(False, message)
            elif return_code == 0:
                message = f"{self.target}: [OK] {self.keyevent_name} ({self.keycode})"
                self.signal.line.emit(message)
                self.signal.result.emit(True, message)
            else:
                message = f"{self.target}: {self.keyevent_name} ({self.keycode}) failed with exit code {return_code}"
                self.signal.line.emit(message)
                self.signal.result.emit(False, message)
        except Exception as error:
            message = f"{self.target}: ADB subprocess error: {error}"
            self.signal.line.emit(message)
            self.signal.result.emit(False, message)
        finally:
            self.signal.finished.emit()
