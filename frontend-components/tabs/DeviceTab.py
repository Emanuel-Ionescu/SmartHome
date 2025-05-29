from PySide6 import QtWidgets as Qwd
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

import cv2
import numpy as np

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("device_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function
        self.color_table = color_table
        self.parent = parent

        self.device_icon_values = {
            "w" : tab_height//4,
            "h" : tab_height//4
        }

        self.device_name_values = {
            "w" : tab_width//2,
            "h" : tab_height//10,
            "text" : color_table["text-light"]
        }

        self.device_location_values = {
            "w" : tab_width//2,
            "h" : tab_height//15,
            "text" : color_table["active-col1"]
        }

        self.input_bttns_value = {
            "Outlets" : ["On", "Off", ""],
            "GenericDevice" : ["", "", ""]
        }

        self.device_bttn_value = {
            "w" : tab_width//6,
            "h" : tab_height//10,
            "per-line" : 4,
            "background" : color_table["elem-backg1"],
            "text" : color_table["active-col2"]
        }

        self.device_icon = Qwd.QLabel(parent=self)
        self.device_icon.setGeometry(
            (tab_width - self.device_icon_values["w"])//2,
            tab_height//12,
            self.device_icon_values["w"],
            self.device_icon_values["h"]
        )

        self.device_name = Qwd.QLabel(parent=self)
        self.device_name.setGeometry(
            (tab_width - self.device_name_values["w"])//2,
            tab_height//12 * 4,
            self.device_name_values["w"],
            self.device_name_values["h"]
        )
        self.device_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.device_name.setStyleSheet(
            """
            color : {c1};
            font-size : {a1}px;
            """.format(
                c1 = self.device_name_values["text"],
                a1 = self.device_name_values["h"]//5*3
            )
        )

        self.device_location = Qwd.QLabel(parent=self)
        self.device_location.setGeometry(
            (tab_width - self.device_location_values["w"])//2,
            tab_height//12 * 5,
            self.device_location_values["w"],
            self.device_location_values["h"]
        )
        self.device_location.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.device_location.setStyleSheet(
            """
            color : {c1};
            font-size : {a1}px;
            """.format(
                c1 = self.device_location_values["text"],
                a1 = self.device_location_values["h"]//5*3
            )
        )

        self.input_bttns = []
        num = 3
        for i in range(num):
            self.input_bttns.append(Qwd.QPushButton(parent=self))
            self.input_bttns[i].clicked.connect(self.inputButton_press_template(i))
            self.input_bttns[i].setGeometry(
                tab_width//2 - self.device_bttn_value["w"]//4 + (i-num//2) * self.device_bttn_value["w"]//2, 
                tab_height//12 * 6,
                self.device_bttn_value["w"]//2,
                self.device_bttn_value["h"]
            )
            self.input_bttns[i].setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a1}px solid {c2};
                font-size : {a3}px;
                """.format(
                    c1 = self.device_bttn_value["background"],
                    c2 = self.device_bttn_value["text"],
                    a1 = self.device_bttn_value["h"]//32,
                    a3 = self.device_bttn_value["h"]//5
                )
            )

        self.device_bttns = []
        for type in self.parent.devices.keys() - {"Lights"}:
            for location in self.parent.devices[type]:
                for dev_name in self.parent.devices[type][location]:
                    button = Qwd.QPushButton(parent=self)
                    button.clicked.connect(
                        self.pressButton_template(
                            len(self.device_bttns)
                            )
                        )
                    button.setText(dev_name)
                    button.setGeometry(
                        tab_width//12 + (self.device_bttn_value["w"] + tab_width//24) * (len(self.device_bttns)%self.device_bttn_value["per-line"]),
                        tab_height//12 * (8 + len(self.device_bttns)//self.device_bttn_value["per-line"] * 2),
                        self.device_bttn_value["w"],
                        self.device_bttn_value["h"]
                    )
                    button.setStyleSheet(
                        """
                        background : {c1};
                        color : {c2};
                        border : {a1}px solid {c2};
                        border-radius: {a2}px;
                        font-size : {a3}px;
                        """.format(
                            c1 = self.device_bttn_value["background"],
                            c2 = self.device_bttn_value["text"],
                            a1 = self.device_bttn_value["h"]//12,
                            a2 = self.device_bttn_value["h"]//5,
                            a3 = self.device_bttn_value["h"]//5
                        )
                    )
                    self.device_bttns.append((button, (dev_name, type, location)))

        self.setDevice("Select device", "GenericDevice", "")
        
    
    def pressButton_template(self, id : int):

        def pressButton():
            button = self.device_bttns[id]
            self.setDevice(*button[1])

        return pressButton

    def setDevice(self, name : str, type : str , location : str):
        self.changeDeviceIcon(type)
        self.device_name.setText(name)
        self.device_location.setText(location)
        for i in range(len(self.input_bttns)):
            self.input_bttns[i].setText(
                self.input_bttns_value[type][i]
            )


    def changeDeviceIcon(self, device_type):
        icon_path = "./tabs/icons/{}.png".format(device_type)
        img = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
        img_a = img[:,:,3]
        img_size  = img_a.shape
        color = self.color_table["active-col1"][1:]

        img_r   = np.ones(img_size, dtype=np.uint8)
        img_g = np.ones(img_size, dtype=np.uint8)
        img_b  = np.ones(img_size, dtype=np.uint8)

        img_r[:] = int(color[0:2], 16)
        img_g[:] = int(color[2:4], 16)
        img_b[:] = int(color[4:6], 16)
        img_pixmap = cv2.merge([
            img_r,
            img_g,
            img_b,
            img_a
        ], 4)
        h, w, ch = img_pixmap.shape
        bytes_per_line = ch * w
        img_pixmap = QImage(
            img_pixmap.data, w, h, bytes_per_line, QImage.Format_RGBA8888
        )
        img_pixmap = img_pixmap.scaled(
            self.device_icon_values["w"],
            self.device_icon_values["h"],
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.device_icon.setPixmap(QPixmap.fromImage(img_pixmap))

    def inputButton_press_template(self, id):

        def func():
            option = self.input_bttns[id].text()
            location = self.device_location.text()
            device = self.device_name.text()
            type = self.device_bttns[id][1][1]

            if option != '':
                self.send("DEVICE:{}:{}:{}:{}".format(type, location, device, option))

        return func