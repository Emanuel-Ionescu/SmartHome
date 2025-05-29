import requests as rq
import os

print("Trying to sync time...")
try:
    r = rq.get("https://8.8.8.8")
    date = r.headers["Date"].split(',')[1]
    os.system("sudo date -s '{}'".format(date))
    print("Succeed", date)
except Exception as e:
    print("Time sync failed: {}".format(e))


from PySide6 import QtWidgets as Qwd
from PySide6.QtCore import Slot, Signal, QThread

from color_table import ColorTableDarkPurple as ColorTable

import multiprocessing as mpc
import sys
import time

sys.path.insert(0, "./tabs")
import UsersTab as UT
import HomeTab as HT
import LightsTab as LT
#import MusicTab as MT
import TempTab as TT
import CameraTab as CT
import DeviceTab as DT
import SecurityTab as ST
import AutomationTab as AT
#import SettingsTab as XT
import utils

sys.path.insert(1, './web-server')
import web_server

SERVER_IP = "192.168.1.12"
SERVER_PORT = 8080 

web = mpc.Process(target=web_server.main, args=(SERVER_IP,))
web.start()

TABS_DICT = {
    #"Settings" : XT,
    "Users" : UT,
    "Home"  : HT,
    "Lights": LT,
    "Temperature" : TT,
    #"Music" : MT, removed and changed with automation tab
    "Camera" : CT,
    "Automation" : AT, 
    "Devices" : DT,
    "Security" : ST,
}   

class MainLoop(QThread):

    got_response = Signal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent

    def run(self):

        while True:
            time.sleep(0.3)
            
            inp = self.parent.client.recieve()

            if inp != '':
                print("> {}".format(inp))
                self.got_response.emit(inp)

        

class MainWindow(Qwd.QMainWindow):

    def __init__(self):
        super().__init__()
        
        ok = False
        iterator = 1
        while ok is False:
            try:
                self.client = utils.Client(SERVER_IP, SERVER_PORT)
                ok = True
            except:
                for i in range(10):
                    print(" "*100, end="\r")
                    print("Connection refused {} time(s), trying again{}".format(iterator, ' '*(i) + '<=>'), end="\r")
                    time.sleep(0.5)
                iterator+=1

        print("Connected", " "*100, end="\r")
        self.client.send("Hello I'm GUI!")
        time.sleep(1)
        var = self.client.recieve()[:-1]
        self.devices = {}

        for entry in var.split("\n\n"):
            type, devices = entry.split(":\n")
            _, location, type, _ = type.split('/')
            devices = devices.split('\n')


            if not type in self.devices.keys(): 
                self.devices[type] = {}

            self.devices[type][location] = devices

        self.server_data = []

        self.main_loop_on_thread = MainLoop(self)
        self.main_loop_on_thread.got_response.connect(self.update_server_data)
        self.main_loop_on_thread.start()

        self.width  = 1920
        self.height = 1080

        self.setGeometry(0, 0, self.width, self.height)
        self.setWindowTitle("SmartHome")
        self.DrawElements()
        self.setCentralWidget(self.centralwidget)
        self.showFullScreen()

    def DrawElements(self):
        self.centralwidget = Qwd.QWidget(parent = self)
        self.tabbar = Qwd.QTabWidget(parent=self.centralwidget)
        self.tabbar.setGeometry(0, 0, self.width, self.height)
        self.setStyleSheet("background: {};".format(ColorTable["background1"]))
        self.centralwidget.setStyleSheet("""
            QTabWidget::tab-bar {alignment: center;}
            QTabWidget::pane {
                border-top: 0px solid #FFFFFF;
                position: absolute;
                top: -0.5em;
                }
        """)
        self.tabbar.setStyleSheet(
            """
            QTabBar::tab {{
                background-color:{c1}; 
                color: {c3}; 
                height: {a1}px; 
                font-size: {a2}px; 
                padding-left:  {a3}px;
                padding-right: {a3}px;
                }}
            QTabBar::tab::selected {{background-color:{c2}; color: {c1};}}
            """.format(
                c1 = ColorTable["active-col2"],
                c2 = ColorTable["background1"],
                c3 = ColorTable["active-col1"],
                a1 = self.height//10,
                a2 = self.height//35,
                a3 = self.width//40
            )
        )

        for tab_name in TABS_DICT.keys():
            self.tabbar.addTab(
                TABS_DICT[tab_name].Tab(
                    self, self.width, self.height//10 * 9, 
                    ColorTable, self.client.send),
                tab_name)
        self.tabbar.setCurrentIndex(1)


    @Slot(str)
    def update_server_data(self, arg):
        if len(self.server_data) == 50:
            self.server_data.pop(0)

        self.server_data.append(arg)


if __name__ == "__main__":

    app = Qwd.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())