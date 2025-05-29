from PySide6 import QtWidgets as Qwd

from RoomSelector import RoomSelector

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("temperature_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function

        self.room_selector = RoomSelector(self, tab_width, tab_height, color_table, self.send, "TEMPERATURE")
        self.room_selector.roomChanged.connect(self.updateRoom)

        self.temp_display_values = {
            "w" : tab_width//3,
            "h" : tab_height//8,
            "background" : color_table["active-col1"],
            "text" : color_table["text-light"]
        }

        self.temp_up_down_bttn_values = {
            "w" : tab_width//4,
            "h" : tab_height//10,
            "background" : color_table["elem-backg1"],
            "text" : color_table["active-col2"]
        }

        self.fan_control_values = {
            "w" : tab_height//10,
            "h" : tab_height//10,
            "on" : color_table["active-col2"],
            "off" : color_table["elem-backg1"]
        }

        self.temp_display = Qwd.QLabel(parent=self)
        
        self.temp_up_bttn   = Qwd.QPushButton(parent=self)
        self.temp_down_bttn = Qwd.QPushButton(parent=self)

        self.fan_control = []

        num = 10
        for i in range(num):
            bttn = Qwd.QPushButton(parent=self)
            bttn.clicked.connect(self.fan_bttn_template(i))

            self.fan_control.append(bttn)


    def updateRoom(self):
        pass

    def fan_bttn_template(self, id):

        def func():
            pass

        return func