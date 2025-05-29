from PySide6 import QtWidgets as Qwd
import os

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("settings_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function