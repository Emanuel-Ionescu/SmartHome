from PySide6 import QtWidgets as Qwd
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Slot

from RoomSelector import RoomSelector

import cv2
import numpy as np
import utils
import os

COLORS = [
    '46424f',
    'ffffff',
    'ff0000',
    'ff8000',
    'ffff00',
    '80ff00',
    '00ff00',
    '00ff80',
    '00ffff',
    '0080ff',
    '0000ff',
    '8000ff',
    'ff00ff'
]

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("lights_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function

        self.parent = parent

        self.room_selector = RoomSelector(self, tab_width, tab_height, color_table, self.send, "LIGHTS")
        self.room_selector.roomChanged.connect(self.update_bulb_selecotr)

        img = cv2.imread("tabs/icons/bulb.png", cv2.IMREAD_UNCHANGED)

        self.bulb_image_alpha = img[:,:,3]
        self.bulb_image_size  = self.bulb_image_alpha.shape

        self.bulb_image_red   = np.ones(self.bulb_image_size, dtype=np.uint8)
        self.bulb_image_green = np.ones(self.bulb_image_size, dtype=np.uint8)
        self.bulb_image_blue  = np.ones(self.bulb_image_size, dtype=np.uint8)


        self.bulb_image_values = {
            "w" : tab_height//2,
            "h" : tab_height//2
        }

        self.color_bttns_values = {
            "w" : tab_height//10,
            "h" : tab_height//10,
            "text" : color_table["text-light"]
        }

        self.bulb_selector_values = {
            "w" : tab_width//3,
            "h" : tab_height//10,
            "background" : color_table["active-col1"],
            "text" : color_table["text-light"]
        }

        self.bulb_image = Qwd.QLabel(parent=self)
        self.bulb_image.setGeometry(
            (tab_width - self.bulb_image_values["w"])//2,
            tab_height//10,
            self.bulb_image_values["w"],
            self.bulb_image_values["h"]
        )
        self.setBulb_image(color_table["elem-backg2"])

        self.color_bttns = []
        for i, color in enumerate(COLORS):
            self.color_bttns.append(Qwd.QPushButton(parent=self))
            self.color_bttns[i].setStyleSheet(
                "background: #{c1}; border: 1px solid black".format( #border: {a1}px solid {c2}; border-radius: {a2}px; margin: {a1}px".format(
                    c1 = color,
                    c2 = self.color_bttns_values["text"],
                    a1 = self.color_bttns_values["h"]//10,
                    a2 = self.color_bttns_values["h"]//10
                ) 
                )
            self.color_bttns[i].setGeometry(
                (tab_width - self.color_bttns_values["w"] * len(COLORS))//2 + self.color_bttns_values["w"] * i,
                tab_height//11 * 9,
                self.color_bttns_values["w"],
                self.color_bttns_values["h"]
            )
            self.color_bttns[i].clicked.connect(self.setBulbColor_template(color))
            
        self.bulb_selector = Qwd.QPushButton(parent=self)
        self.bulb_selector_options = self.parent.devices["Lights"]["Livingroom"]
        self.bulb_selector_index = 0
        self.bulb_selector.setStyleSheet("background: {c1}; color: {c2}; font-size: {a1}px; border: 0px solid black".format(
            c1 = self.bulb_selector_values["background"],
            c2 = self.bulb_selector_values["text"],
            a1 = self.bulb_selector_values["h"]//2
        ))
        self.bulb_selector.setText("Bulb: " + self.bulb_selector_options[self.bulb_selector_index])
        self.bulb_selector.clicked.connect(self.changeBulb)
        self.bulb_selector.setGeometry(
            (tab_width - self.bulb_selector_values["w"])//2,
            tab_height//10 * 7,
            self.bulb_selector_values["w"],
            self.bulb_selector_values["h"]
        )


    def setBulb_image(self, color):
        if color[0] == '#': 
            color = color[1:]
        self.bulb_image_red[:]   = int(color[0:2], 16)
        self.bulb_image_green[:] = int(color[2:4], 16)
        self.bulb_image_blue[:]  = int(color[4:6], 16)
        self.bulb_image_pixmap = cv2.merge([
            self.bulb_image_red,
            self.bulb_image_green,
            self.bulb_image_blue,
            self.bulb_image_alpha
        ], 4)
        h, w, ch = self.bulb_image_pixmap.shape
        bytes_per_line = ch * w
        self.bulb_image_pixmap = QImage(
            self.bulb_image_pixmap.data, w, h, bytes_per_line, QImage.Format_RGBA8888
        )
        self.bulb_image_pixmap = self.bulb_image_pixmap.scaled(
            self.bulb_image_values["w"], 
            self.bulb_image_values["h"], 
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.bulb_image.setPixmap(QPixmap.fromImage(self.bulb_image_pixmap))


    def setBulbColor(self, color):
        self.setBulb_image(color)
        self.send("BULB:{}:{}:{}".format(
            self.room_selector.getRoom(),
            self.bulb_selector_options[self.bulb_selector_index], 
            color
            )
        )


    def setBulbColor_template(self, color):
        def template():
            self.setBulbColor(color)
        return template


    def changeBulb(self):
        self.bulb_selector_index = (self.bulb_selector_index + 1) % len(self.bulb_selector_options) 
        self.bulb_selector.setText("Bulb: " + self.bulb_selector_options[self.bulb_selector_index])

    @Slot(str)
    def update_bulb_selecotr(self, arg):
        self.bulb_selector_options = self.parent.devices["Lights"][arg]
        self.bulb_selector_index = 0
        self.bulb_selector.setText("Bulb: " + self.bulb_selector_options[self.bulb_selector_index])
