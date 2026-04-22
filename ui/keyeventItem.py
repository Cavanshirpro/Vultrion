from core.dataTypes import *
class KeyEventItem(QWidget):
    def __init__(self,name:str,description:str):
        super().__init__()
        self.name=name
        self.setObjectName("KeyEventItem")
        self.MainLayout=QGridLayout(self)
        self.MainLayout.setSpacing(8)
        self.MainLayout.setContentsMargins(5, 5, 5, 5)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        
        self.EnterButton=QCommandLinkButton()
        self.EnterButton.setObjectName(u"EnterButton")
        self.EnterButton.setText(name)
        self.EnterButton.setDescription(description)
        self.EnterButton.setToolTip(f"Execute keyevent: {name}")
        self.EnterButton.setWhatsThis(f"<h2>{name}</h2><p>{description}</p><p>Click to execute this keyevent on all selected devices.</p>")
        self.EnterButton.setStatusTip(f"Click to execute {name}")
        self.EnterButton.setMouseTracking(True)
        self.EnterButton.installEventFilter(self)
        self.MainLayout.addWidget(self.EnterButton,0,0,1,1)

        self.Logs=QTextEdit()
        self.Logs.setObjectName(u"Logs")
        self.Logs.setReadOnly(True)
        self.Logs.setToolTip("Execution results for this keyevent")
        self.Logs.setWhatsThis("Shows the output and status of the keyevent execution")
        self.MainLayout.addWidget(self.Logs,0,1,1,1)
        self.installEventFilter(self)
        