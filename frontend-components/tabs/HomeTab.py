from PySide6 import QtWidgets as Qwd
from PySide6 import QtGui
from PySide6.QtCore import Qt, QTimer

import datetime as dt
import qrcode

from PIL.ImageQt import ImageQt

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("home_tab")
        self.setGeometry(0, 0, tab_width, tab_height)

        self.label = Qwd.QLabel(parent=self)
        self.canvas = QtGui.QPixmap(tab_height//4 * 3, tab_height//4 * 3)
        self.canvas.fill(Qt.GlobalColor.transparent)
        self.label.setPixmap(self.canvas)
        self.label.setGeometry((tab_width - tab_height//4 * 3)//2, 
            tab_height//8, 
            tab_height//4 * 3, tab_height//4 * 3)
        
        self.c_size = tab_height//4 * 3
        self.p_size = tab_height//40

        self.hour_pen = QtGui.QPen()
        self.hour_pen.setColor(QtGui.QColor(color_table["active-col2"]))
        self.hour_pen.setWidth(self.p_size)

        self.min_pen = QtGui.QPen()
        self.min_pen.setColor(QtGui.QColor(color_table["active-col1"]))
        self.min_pen.setWidth(self.p_size//2)

        self.sec_pen = QtGui.QPen()
        self.sec_pen.setColor(QtGui.QColor(color_table["text-light"]))
        self.sec_pen.setWidth(self.p_size//3)

        self.font = QtGui.QFont("Consolas", 40, 1)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start()

        qr = qrcode.QRCode(version=1)
        qr.add_data("http://192.168.1.11:5000")
        img = qr.make_image(fill_color=color_table["active-col2"], back_color=color_table["background1"])
        img = ImageQt(img)
        
        img = QtGui.QPixmap.fromImage(img).scaled(tab_width//8, tab_width//8, Qt.AspectRatioMode.KeepAspectRatio)

        self.qr_display = Qwd.QLabel(parent=self)
        self.qr_display.setGeometry(
            tab_width//5 * 4,
            tab_height//5,
            tab_width//8,
            tab_width//8
        )
        self.qr_display.setPixmap(img)


    def update_clock(self):                

        date = dt.datetime.now()

        self.canvas = QtGui.QPixmap(self.c_size, self.c_size)
        self.canvas.fill(Qt.GlobalColor.transparent)

        self.painter = QtGui.QPainter(self.canvas)
        self.painter.setPen(self.hour_pen)
        self.painter.drawArc(3*self.p_size, 3*self.p_size, self.c_size - 6*self.p_size, self.c_size - 6*self.p_size, 90 * 16, -int((date.hour)%12/11 * 360 * 16))
        self.painter.setPen(self.min_pen)
        self.painter.drawArc(2*self.p_size, 2*self.p_size, self.c_size - 4*self.p_size, self.c_size - 4*self.p_size, 90 * 16, -int((date.minute)/60 * 360 * 16))
        self.painter.setPen(self.sec_pen)
        self.painter.drawArc(1*self.p_size, 1*self.p_size, self.c_size - 2*self.p_size, self.c_size - 2*self.p_size, 90 * 16, -int((date.second)/60 * 360 * 16))

        self.painter.setFont(self.font)
        self.painter.drawText(self.c_size//11*4, self.c_size//2, "{:02d}:{:02d}:{:02d}".format(date.hour, date.minute, date.second))

        self.painter.end()
        self.label.setPixmap(self.canvas)