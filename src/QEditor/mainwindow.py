from PySide6.QtCore import Qt, Signal, Slot, QCoreApplication, qDebug  # for enum flags
from PySide6.QtWidgets import QMainWindow, QFileDialog, QDockWidget, QMessageBox, QTabWidget, QWidget
from .editor.codeEditorWidget import CodeEditorWidget
from .welcomePage import WelcomePage
from .editor.tabsManager import TabsManager
import os

from .ui.ui_mainwindow import Ui_mainWindow


class MainWindow(QMainWindow):
    # Signals
    externalFile = Signal(str)

    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self.editor_tabs_dock = QDockWidget('', self)

        self.tabs_manager = TabsManager(parent=self)
        self.tabs_manager.tabs_empty.connect(lambda: self.close_editor_tabs(self.editor_tabs_dock))

        tabs = self.tabs_manager
        self.editor_tabs_dock.setWidget(self.tabs_manager.tabs)
        self.editor_tabs_dock.resize(self.size())

        self.addDockWidget(Qt.TopDockWidgetArea, self.editor_tabs_dock)

        self.externalFile.connect(
            lambda filepath: tabs.add_editor_tab(
                t := CodeEditorWidget(parent=self.editor_tabs_dock, filepath=filepath),
                t.get_file_base_name()))
        self.check_cmd_args()

    @Slot()
    def on_actionNew_triggered(self):
        new_editor = CodeEditorWidget(parent=self.editor_tabs_dock, filepath=None)
        self.tabs_manager.add_editor_tab(new_editor, new_editor.get_file_base_name())

    @Slot()
    def on_actionOpen_triggered(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')
        tabs = self.tabs_manager.tabs
        if filename[0] != '':
            # check if already opened
            for i in range(tabs.count()):
                page = tabs.widget(i)
                if isinstance(page, CodeEditorWidget):
                    if page.filepath == filename[0]:
                        return

            self.tabs_manager.add_editor_tab(ce := CodeEditorWidget(self.editor_tabs_dock, filename[0]),
                                             ce.get_file_base_name())

    @Slot()
    def on_actionSave_triggered(self):
        tabs = self.tabs_manager.tabs
        editor = tabs.currentWidget()
        if not isinstance(editor, CodeEditorWidget):
            return

        if editor.is_new_file():
            # new file to save
            name = QFileDialog.getSaveFileName(self, 'Save File')
            if name[0] == '':
                return
            filepath = name[0]
        else:
            filepath = editor.filepath

        with open(filepath, 'wb') as f:
            f.write(editor.get_content())
        editor.filepath = filepath
        tabs.setTabText(tabs.currentIndex(), editor.get_file_base_name())

    @Slot()
    def close_editor_tabs(self, dock_tabs: QDockWidget):
        dock_tabs.close()

    def add_welcome_page(self):
        page = WelcomePage(self)
        page.resize(self.size())
        self.tabs_manager.add_editor_tab(page, 'Welcome')

    def check_cmd_args(self):
        argv = QCoreApplication.arguments()
        if len(argv) > 1:
            if os.path.exists(argv[1]):
                qDebug(b'opening file from command line (could be file drop on executable)')
                self.externalFile.emit(argv[1])
            else:
                QMessageBox.information(self, 'Error', 'Invalid file', QMessageBox.Ok)
        else:
            self.add_welcome_page()