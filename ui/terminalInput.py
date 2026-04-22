from __future__ import annotations
from core.dataTypes import *


class TerminalInput(QLineEdit):
    commandRequested=Signal(str)
    completionRequested=Signal(str,int)

    def __init__(self,parent=None):
        super().__init__(parent)
        self._history: list[str]=[]
        self._history_index: int | None=None
        self._draft_text=""

    def setHistory(self,history: list[str])->None:
        self._history=list(history)
        if self._history_index is not None and self._history_index >= len(self._history):
            self._history_index=None

    def addHistoryEntry(self,command: str)->None:
        self._history.append(command)
        self._history_index=None
        self._draft_text=""

    def resetNavigation(self)->None:
        self._history_index=None
        self._draft_text=""

    def applyCompletion(self,completed_text: str)->None:
        self.setText(completed_text)
        self.setCursorPosition(len(completed_text))

    def event(self,event)->bool:
        if event.type()==QEvent.Type.ShortcutOverride and event.key()==Qt.Key.Key_Tab:
            event.accept()
            return True
        return super().event(event)

    def focusNextPrevChild(self,next: bool)->bool:
        return False

    def keyPressEvent(self,event: QKeyEvent)->None:
        key=event.key()

        if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            self.commandRequested.emit(self.text())
            event.accept()
            return

        if key==Qt.Key.Key_Up:
            self._show_previous_history()
            event.accept()
            return

        if key==Qt.Key.Key_Down:
            self._show_next_history()
            event.accept()
            return

        if key==Qt.Key.Key_Tab:
            self.completionRequested.emit(self.text(),self.cursorPosition())
            event.accept()
            return

        super().keyPressEvent(event)

    def _show_previous_history(self)->None:
        if not self._history:
            return

        if self._history_index is None:
            self._draft_text=self.text()
            self._history_index=len(self._history)-1
        elif self._history_index>0:
            self._history_index -= 1

        self._apply_history_value()

    def _show_next_history(self)->None:
        if self._history_index is None:
            return

        if self._history_index<len(self._history)-1:
            self._history_index+=1
            self._apply_history_value()
            return

        self._history_index=None
        self.setText(self._draft_text)
        self.setCursorPosition(len(self._draft_text))

    def _apply_history_value(self)->None:
        if self._history_index is None:return

        value=self._history[self._history_index]
        self.setText(value)
        self.setCursorPosition(len(value))
