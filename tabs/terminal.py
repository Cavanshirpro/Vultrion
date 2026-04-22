from __future__ import annotations

import os
from typing import Optional

from core.dataTypes import *
from core.requests import DataManager
from core.terminalWorker import TerminalWorker
from ui.terminalInput import TerminalInput


class TerminalTab(QWidget):
    executeCommandRequested=Signal(str)
    stopCurrentRequested=Signal()
    setAdbPathRequested=Signal(object)
    requestCompletionRequested=Signal(str,int)

    def __init__(self,parent,checkdata: Optional[CheckData],dataManagerRequest: DataManager):
        super().__init__(parent)
        self.setObjectName("TerminalTab")

        self.checkData=checkdata
        self.checkData.changed.connect(self.on_data_changed)
        self.dataManager=dataManagerRequest

        self._current_cwd=os.getcwd()
        self._current_adb_path=None
        self._is_running=False

        self.MainLayout=QVBoxLayout(self)
        self.MainLayout.setContentsMargins(12,12,12,12)
        self.MainLayout.setSpacing(10)
        self.setLayout(self.MainLayout)

        self.terminal=QPlainTextEdit(self)
        self.terminal.setReadOnly(True)
        self.terminal.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.terminal.setMaximumBlockCount(5000)
        terminal_font=QFont("Consolas")
        terminal_font.setStyleHint(QFont.StyleHint.Monospace)
        terminal_font.setPointSize(11)
        self.terminal.setFont(terminal_font)
        self.dataManager.read.style.emit(self.objectName())
        self.dataManager.response.style.connect(self.get_style_sheet)

        self.MainLayout.addWidget(self.terminal)

        self.InputRow=QHBoxLayout()
        self.InputRow.setSpacing(8)
        self.MainLayout.addLayout(self.InputRow)

        self.input=TerminalInput(self)
        self.input.setPlaceholderText(self._prompt_text())
        self.input.setClearButtonEnabled(True)
        self.input.setFont(terminal_font)
        self.input.setHistory(list(self.checkData.data.last_commands))
        self.input.commandRequested.connect(self.sendCommand)
        self.input.completionRequested.connect(self.requestCompletionRequested.emit)
        self.input.textChanged.connect(self._refresh_action_states)
        self.InputRow.addWidget(self.input,1)

        self.sendButton=QPushButton("Send",self)
        self.sendButton.clicked.connect(self.sendCommand)
        self.InputRow.addWidget(self.sendButton)

        self.cancelButton=QPushButton("Cancel",self)
        self.cancelButton.clicked.connect(self.stopCurrentRequested.emit)
        self.InputRow.addWidget(self.cancelButton)

        self.workerThread=QThread(self)
        self.worker=TerminalWorker(self.checkData.data.choosen_path_for_adb)
        self.worker.moveToThread(self.workerThread)

        self.executeCommandRequested.connect(self.worker.executeCommand)
        self.stopCurrentRequested.connect(self.worker.stopCurrent)
        self.setAdbPathRequested.connect(self.worker.setAdbPath)
        self.requestCompletionRequested.connect(self.worker.requestCompletion)

        self.worker.output.connect(self.appendOutput)
        self.worker.runningChanged.connect(self.onRunningChanged)
        self.worker.cwdChanged.connect(self.onCwdChanged)
        self.worker.clearRequested.connect(self.clearTranscript)
        self.worker.completionReady.connect(self.onCompletionReady)
        self.worker.commandFinished.connect(self.onCommandFinished)

        self.workerThread.finished.connect(self.worker.deleteLater)
        self.workerThread.start()

        self._announce_session()
        self.on_data_changed()
        self._refresh_action_states()

    def get_style_sheet(self,objectName:str,style:str):
        if objectName==self.objectName():self.setStyleSheet(style)

    def _announce_session(self) -> None:
        self.appendOutput("ADBez terminal session ready.")
        self.appendOutput(f"Working directory: {self._current_cwd}")
        adb_path=self.checkData.data.choosen_path_for_adb
        if adb_path:
            self.appendOutput(f"ADB is injected into this terminal session only: {adb_path}")
        else:
            self.appendOutput("ADB path is not configured yet. Configure it in Settings to use adb directly.")
        self.appendOutput("")

    def _prompt_text(self) -> str:
        return f"{self._current_cwd}>"

    def _command_prompt(self) -> str:
        return self._prompt_text() + " "

    def _refresh_action_states(self,*_args) -> None:
        has_text=bool(self.input.text().strip())
        self.sendButton.setEnabled(has_text and not self._is_running)
        self.cancelButton.setEnabled(self._is_running)
        self.input.setEnabled(not self._is_running)
        self.input.setPlaceholderText(self._prompt_text())

    def _append_line(self,text: str) -> None:
        self.terminal.appendPlainText(text)
        scrollbar=self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def appendOutput(self,line: str) -> None:
        self._append_line(line)

    def clearTranscript(self) -> None:
        self.terminal.clear()

    def on_data_changed(self) -> None:
        adb_path=self.checkData.data.choosen_path_for_adb
        if adb_path == self._current_adb_path:
            return

        self._current_adb_path=adb_path
        self.setAdbPathRequested.emit(adb_path)

    def sendCommand(self,command: Optional[str]=None) -> None:
        command=(command if isinstance(command,str) else self.input.text()).strip()
        if not command or self._is_running:
            return

        self._remember_command(command)
        self.appendOutput(self._command_prompt() + command)
        self.input.clear()
        self.input.resetNavigation()
        self.sendButton.setEnabled(False)
        self.input.setEnabled(False)
        self.executeCommandRequested.emit(command)

    def _remember_command(self,command: str) -> None:
        history=list(self.checkData.data.last_commands)
        history.append(command)
        history=history[-200:]
        self.checkData.data.last_commands=history
        self.checkData.changed_last_commands.emit(history)
        self.input.setHistory(history)

    def onRunningChanged(self,running: bool) -> None:
        self._is_running=running
        self._refresh_action_states()

        if not running:
            self.input.setFocus()

    def onCwdChanged(self,cwd: str) -> None:
        self._current_cwd=cwd
        self._refresh_action_states()

    def onCompletionReady(self,completed_text: str,candidates: list[str]) -> None:
        previous_text=self.input.text()
        text_changed=completed_text != previous_text

        if text_changed:
            self.input.applyCompletion(completed_text)

        if len(candidates) > 1 and not text_changed:
            self.appendOutput("    ".join(candidates))

    def onCommandFinished(self,return_code: int,was_cancelled: bool) -> None:
        if was_cancelled:
            self.appendOutput("[cancelled]")
        elif return_code != 0:
            self.appendOutput(f"[exit {return_code}]")

        self.input.setFocus()
        self._refresh_action_states()

    def closeEvent(self,event: QCloseEvent) -> None:
        self.stopCurrentRequested.emit()
        self.workerThread.quit()
        self.workerThread.wait(2000)
        super().closeEvent(event)
