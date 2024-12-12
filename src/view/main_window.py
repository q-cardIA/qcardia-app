from pathlib import Path

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog, QMainWindow

from view.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):

    load_button_signal = Signal(str)
    seg_button_signal = Signal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.folder_selected = False

        self.ui.load_button.clicked.connect(self.select_folder)
        self.ui.seg_button.clicked.connect(self.emit_segmentation_signal)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_selected = True
            self.load_button_signal.emit(folder_path)

    def has_folder_been_selected(self):
        return self.folder_selected

    def emit_segmentation_signal(self):
        if self.has_folder_been_selected():
            self.seg_button_signal.emit()
