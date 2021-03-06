from PySide6.QtWidgets import QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QStackedWidget
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex
from PySide6.QtGui import QMouseEvent
import os
from ..ui.ui_folder_init import Ui_folderInit


class FolderExplorer(QWidget):
    """
    A explorer for file folder, use Qt's model/view
    """
    file_clicked = Signal(str)
    ask_open_folder = Signal()

    def __init__(self, parent):
        print('folderExplorer init')
        super(FolderExplorer, self).__init__()
        self.parent = parent
        self._folder_dir_path = ''
        self._tree_view: QTreeView = None
        self.folder_model = None
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self._initial_view = FolderInit(self)
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self._initial_view)
        self.layout.addWidget(self.stacked_widget)
        self.setLayout(self.layout)
        print('folderExplorer done init')

    @property
    def folder_dir_path(self):
        return self._folder_dir_path

    @property
    def initial_view(self):
        return self._initial_view

    def open_folder(self, opened_dir):
        self._folder_dir_path = opened_dir
        self._init_folder_tree_view(self._folder_dir_path)

    def _init_folder_tree_view(self, dir_name):
        print('opened directory: ', dir_name)
        self._folder_dir_path = dir_name  # set associated dir path

        self.folder_model = QFileSystemModel()
        self._tree_view = FolderTreeView(self)
        self._tree_view.setModel(self.folder_model)
        self._tree_view.setRootIndex(self.folder_model.setRootPath(dir_name))

        # Hide columns we don't need
        self._tree_view.hideColumn(1)
        self._tree_view.hideColumn(2)
        self._tree_view.hideColumn(3)

        self._tree_view.setHeaderHidden(True)
        self.stacked_widget.addWidget(self._tree_view)
        self.stacked_widget.setCurrentWidget(self._tree_view)

    def enterEvent(self, event: QMouseEvent) -> None:
        event.accept()
        print('Entered folder explorer')


class FolderTreeView(QTreeView):
    def __init__(self, parent):
        super(FolderTreeView, self).__init__()
        self.parent = parent

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index: QModelIndex = self.indexAt(event.pos())
        if not index.isValid():
            print('invalid mousePressEvent')
            super().mousePressEvent(event)
            return

        model: QFileSystemModel = self.model()
        filepath = model.filePath(index)
        print(f"'{filepath}' clicked")

        if os.path.isfile(filepath):
            self.parent.file_clicked.emit(filepath)
        elif os.path.isdir(filepath):
            # check isExpanded twice because clicking the '>' left to item
            # will affect whether collapse or expand.
            # if we write:
            # self.collapse(index) if self.isExpanded(index) else self.expand(index)
            # super().mousePressEvent(event)
            # will mess up this process because it will expand and collapse (and vise versa)
            was_expanded = self.isExpanded(index)
            super().mousePressEvent(event)
            if event.button() == Qt.LeftButton:
                expanded = self.isExpanded(index)
                if was_expanded == expanded:
                    self.collapse(index) if expanded else self.expand(index)
        else:
            print('unknown type')
            super().mousePressEvent(event)


class FolderInit(QWidget):
    def __init__(self, parent):
        super(FolderInit, self).__init__(parent)
        self.parent = parent
        self.ui = Ui_folderInit()
        self.ui.setupUi(self)
        self.setWindowTitle('No Folder Opened')

    @Slot()
    def open_folder(self):
        self.parent.ask_open_folder.emit()
