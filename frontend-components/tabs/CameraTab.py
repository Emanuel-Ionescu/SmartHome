from PySide6 import QtWidgets as Qwd
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

from RoomSelector import RoomSelector

import numpy as np
import cv2
import utils

class CameraThread(QThread):

    changePixmap = Signal(QImage)
    updateData   = Signal(int)
    removeParentData = Signal(int)

    def __init__(self, p, w, h):
        super().__init__(parent=p)
        self.width = w
        self.height = h
        self.debug = False
        self.data = []
        
        self.pipeline = 'imxcompositor_g2d name=comp sink_0::xpos=0 sink_0::ypos=0 sink_1::xpos=0 sink_1::ypos=720 ! queue ! appsink sync=false ' \
                        'rtspsrc location="rtsp://TapoCam:salut123@192.168.1.21/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ! queue ! comp. ' \
                        'rtspsrc location="rtsp://TapoCam:salut123@192.168.1.22/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ! queue ! comp. '
        self.frames = {
            "Bedroom1"   : '',
            "Livingroom" : ''
        }
        self.camera_streamed = "Livingroom"
        
        self.no_image = [np.ones((18,32,1),  dtype=np.uint8) * int('53', 16),
                         np.ones((18,32,1),  dtype=np.uint8) * int('43', 16),
                         np.ones((18,32,1),  dtype=np.uint8) * int('f3', 16),]

    def run(self):

        cam = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)

        while True:
            ok, frame = cam.read()

            if ok:

                self.updateData.emit(1)
                iterator = 0
                rect = []
                place = ''

                while iterator < len(self.data):
                    val = self.data[iterator]
                    if val.split(':')[0] == "FACE":
                        
                        try:
                            place, a = val.split(':')[1:]
                        except:
                            print("!! val splitting failed; val= {}".format(val))
                        rect = a[1:-1].split()

                        self.data.pop(iterator)
                        self.removeParentData.emit(iterator)

                        iterator = 100000

                    iterator += 1

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                for i, k in enumerate(self.frames.keys()):
                    self.frames[k] = frame[i * 720 : (i + 1) * 720, :, :]

                if place != '' and self.debug:
                    overlay = self.frames[place].copy()
                    alpha = 0.4
                    overlay = cv2.rectangle(
                        overlay, 
                        (int(float(rect[0]) * self.frames[place].shape[1]), int(float(rect[1]) * self.frames[place].shape[1])),
                        (int(float(rect[0]) * self.frames[place].shape[0]), int(float(rect[2]) * self.frames[place].shape[0])),
                        (int('53', 16), int('43', 16), int('f3', 16)),
                        -1
                        )
                    self.frames[place] = cv2.addWeighted(overlay, alpha, self.frames[place], 1 - alpha, 0)


                try:
                    frame = self.frames[self.camera_streamed]
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
                except KeyError:
                    frame = cv2.merge(
                        [*self.no_image,
                        np.random.randint(255, size=(18, 32, 1), dtype=np.uint8)],
                        4)

            else:
                frame = np.random.randint(255, size=(9, 16, 1), dtype=np.uint8)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qt_frame = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGBA8888)
            qt_frame = qt_frame.scaled(self.width, self.height, Qt.AspectRatioMode.KeepAspectRatio)
            self.changePixmap.emit(qt_frame)

    @Slot(str)
    def change_camera_streamed(self, arg):
        self.camera_streamed = arg


class Tab(Qwd.QWidget):

    respond_2_request_signal = Signal(list)


    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("camera_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.parent = parent
        self.send = send_data_function

        self.room_selector = RoomSelector(self, tab_width, tab_height, color_table, self.send, "CAMERA")

        self.camera_bttns_values = {
            "w" : tab_width//8,
            "h" : tab_height//8,
            "background" : color_table["elem-backg1"],
            "text" : color_table["active-col2"]
        }

        self.camera_view = Qwd.QLabel(parent=self)
        self.camera_view.setGeometry(
            tab_width//6,
            tab_height//9,
            tab_width//3 * 2,
            tab_height//3 * 2
        )

        self.camera_thread = CameraThread(self, tab_width//4 * 3, tab_height//4 * 3)
        self.camera_thread.changePixmap.connect(self.set_image)
        self.room_selector.roomChanged.connect(self.camera_thread.change_camera_streamed)
        self.camera_thread.updateData.connect(self.update_data)
        self.camera_thread.removeParentData.connect(self.remove_parent_data)
        self.camera_thread.start()

        self.camera_bttns = [
            Qwd.QPushButton(parent=self),
            Qwd.QPushButton(parent=self),
            Qwd.QPushButton(parent=self),
            Qwd.QPushButton(parent=self)
        ]
        self.camera_bttns_functions = ["LEFT", "UP", "DOWN", "RIGHT"]
        
        for i, b in enumerate(self.camera_bttns):
            b.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a1}px solid {c2};
                border-radius: {a2}px;
                font-size : {a3}px;
                """.format(
                    c1 = self.camera_bttns_values["background"],
                    c2 = self.camera_bttns_values["text"],
                    a1 = self.camera_bttns_values["h"]//12,
                    a2 = self.camera_bttns_values["h"]//5,
                    a3 = self.camera_bttns_values["h"]//5
                )
            )

            b.setGeometry(
                tab_width//5 * (i + 1) - self.camera_bttns_values["w"]//2,
                tab_height//10 * 8,
                self.camera_bttns_values["w"],
                self.camera_bttns_values["h"]
            )

            b.setText(self.camera_bttns_functions[i])
            b.clicked.connect( self.cam_function_template(self.camera_bttns_functions[i]) )

    @Slot(QImage)
    def set_image(self, image):
        self.camera_view.setPixmap(QPixmap.fromImage(image))

    @Slot(int)
    def update_data(self, arg):
        self.camera_thread.data = self.parent.server_data

    @Slot(int)
    def remove_parent_data(self, arg):
        pass
        #self.parent.server_data.pop(arg)


    def cam_function_template(self, value):

        def cam_func():
            self.send("CAMERA:{}:{}".format(self.room_selector.getRoom(), value))

        return cam_func
        