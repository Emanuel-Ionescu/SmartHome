from PySide6 import QtWidgets as Qwd
from PySide6.QtCore import Qt
from RoomSelector import RoomSelector
import os

COLORS = [
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
        self.setObjectName("automation_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function
        self.color_table = color_table

        self.room_selector = RoomSelector(self, tab_width, tab_height, color_table, self.send, "AUTOMATION")
        self.room_selector.roomChanged.connect(self.load_automation_options)

        self.saves = {}
        for room in ["Livingroom", "Bedroom1", "Bedroom2", "Bathroom", "Kitchen", "Garage"]:
            self.saves[room] = dict({
                "pers_det_light" : {"color" : COLORS[0], "timer-index" : 0, "state" : False},
                "camera_follow"  : {"state" : False}
                }).copy()
            
        self.toggle_values = {
            "w" : tab_width // 5,
            "h" : tab_height // 10,
            "background-off" : color_table["elem-backg1"],
            "background-on" : color_table["active-col2"],
            "text-off" : color_table["active-col2"],
            "text-on"  : color_table["elem-backg1"],
        }

        self.color_values = {
            "w" : tab_height//10,
            "h" : tab_height//10,
            "text" : color_table["text-light"]
        }

        self.timer_values = {
            "w" : tab_width//5,
            "h" : tab_height//10,
            "text" : color_table["text-light"],
            "background" : color_table["active-col1"]
        }

        self.save_bttn_values = {
            "w" : tab_width//10,
            "h" : tab_height//10,
            "background" : color_table["active-col2"],
            "text" : color_table["active-col1"]
        }

        ### Face activated light

        self.toggle_button1 = Qwd.QPushButton(parent=self)
        self.toggle_button1.setGeometry(
            tab_width//20,
            tab_height//10,
            self.toggle_values["w"],
            self.toggle_values["h"]
        )
        self.toggle_state1 = True  #after function call it will pe set to False
        self.toggle1_on_color = COLORS[0]
        self.toggle_button1.clicked.connect(self.det_pers_light_press)

        self.color_bttns = []
        for i, color in enumerate(COLORS):
            self.color_bttns.append(Qwd.QPushButton(parent=self))
            self.color_bttns[i].setStyleSheet("background: #{c1}; border: 0px solid black".format(c1 = color))
            self.color_bttns[i].setGeometry(
                tab_width//20 + self.color_values["w"] * i,
                tab_height//10 * 2 + tab_height//20,
                self.color_values["w"],
                self.color_values["h"]
            )
            self.color_bttns[i].clicked.connect(self.setAutoColor_template(color))

        self.text1 = Qwd.QLabel(parent=self, text="Turn off after:")
        self.text1.setGeometry(
            tab_width//20 + self.toggle_values["w"],
            tab_height//10,
            tab_width//5,
            tab_height//10
        )
        self.text1.setStyleSheet(
            """
            color : {c1};
            font-size : {a1}px;
            """.format(
                c1 = color_table["text-light"],
                a1 = tab_height//20
            )
        )
        self.text1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_button = Qwd.QPushButton(parent=self)
        self.timer_options = ["Instant", "30 sec", "1 min", "5 min", "15 min", "30 min", "1h", "3h", "Never"]
        self.timer_index = 0
        self.timer_button.setGeometry(
            tab_width//20 + self.toggle_values["w"] + tab_width//5,
            tab_height//10,
            self.timer_values["w"],
            self.timer_values["h"]
        )
        self.timer_button.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            font-size : {a1}px;
            border : 0px solid black;
            border-radius : {a2}px
            """.format(
                c1 = self.timer_values["background"],
                c2 = self.timer_values["text"],
                a1 = self.timer_values["h"]//10 * 6,
                a2 = self.timer_values["h"]//10
            )
        )
        self.timer_button.clicked.connect(self.timer_press)
        self.timer_button.setText(self.timer_options[self.timer_index])
        self.det_pers_light_press()

        ### camera follow

        self.toggle_button2 = Qwd.QPushButton(parent=self)
        self.toggle_state2 = False
        self.toggle_button2.setGeometry(
            tab_width//20,
            tab_height//10 * 5,
            tab_width//5,
            tab_height//10
        )
        self._camera_follow_set()
        self.toggle_button2.clicked.connect(self.camera_follow)

        ### save button

        self.save_bttn = Qwd.QPushButton(parent=self)
        self.save_bttn.setGeometry(
            tab_width//20,
            tab_height//10 * 8,
            self.save_bttn_values["w"],
            self.save_bttn_values["h"]
        )
        self.save_bttn.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            border-radius : {a1}px;
            font-size : {a2}px;
            """.format(
                c1 = self.save_bttn_values["background"],
                c2 = self.save_bttn_values["text"],
                a1 = self.save_bttn_values["h"]//2,
                a2 = self.save_bttn_values["h"]//3
            )
        )
        self.save_bttn.setText("Save")
        self.save_bttn.clicked.connect(self.save_options_press)


    def det_pers_light_press(self):
        self.toggle_state1 = not self.toggle_state1
        self._det_pers_light_set()


    def _det_pers_light_set(self):

        if self.toggle_state1 is False:
            self.toggle_button1.setText("Person detection activated\nlight? NO")
            self.toggle_button1.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a1}px solid {c2};
                font-size : {a2}px;
                border-radius : {a3}px;
                """.format(
                    c1 = self.toggle_values["background-off"],
                    c2 = self.toggle_values["text-off"],
                    a1 = self.toggle_values["h"]//20,
                    a2 = self.toggle_values["h"]//4,
                    a3 = self.toggle_values["h"]//10
                )
            )
        else:
            self.toggle_button1.setText("Person detection activated\nlight? YES")
            self.toggle_button1.setStyleSheet(
                """
                background : #{c1};
                color : {c2};
                border : {a1}px solid {c2};
                font-size : {a2}px;
                border-radius : {a3}px;
                """.format(
                    c1 = self.toggle1_on_color,
                    c2 = self.toggle_values["text-on"],
                    a1 = self.toggle_values["h"]//20,
                    a2 = self.toggle_values["h"]//4,
                    a3 = self.toggle_values["h"]//10
                )
            )
        self.timer_button.setText(self.timer_options[self.timer_index])


    def setAutoColor_template(self, color):
        
        def func():
            self.toggle1_on_color = color
            self._det_pers_light_set()
            
        return func


    def timer_press(self):
        self.timer_index = (self.timer_index + 1 ) % len(self.timer_options)
        self.timer_button.setText(self.timer_options[self.timer_index])


    def camera_follow(self):
        self.toggle_state2 = not self.toggle_state2
        self._camera_follow_set()


    def _camera_follow_set(self):
        if self.toggle_state2 is False:
            self.toggle_button2.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a1}px solid {c2};
                font-size: {a2}px;
                border-radius : {a3}px;
                """.format(
                    c1 = self.toggle_values["background-off"],
                    c2 = self.toggle_values["text-off"],
                    a1 = self.toggle_values["h"]//20,
                    a2 = self.toggle_values["h"]//4,
                    a3 = self.toggle_values["h"]//10
                )
                )
            self.toggle_button2.setText("Move camera after faces?\nNO")
        else:
            self.toggle_button2.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a1}px solid {c2};
                font-size: {a2}px;
                border-radius : {a3}px;
                """.format(
                    c1 = self.toggle_values["background-on"],
                    c2 = self.toggle_values["text-on"],
                    a1 = self.toggle_values["h"]//20,
                    a2 = self.toggle_values["h"]//4,
                    a3 = self.toggle_values["h"]//10
                )
                )
            self.toggle_button2.setText("Move camera after faces?\nYES")


    def load_automation_options(self):
        room = self.room_selector.getRoom() 
        self.toggle_state1 = self.saves[room]["pers_det_light"]["state"]
        self.toggle1_on_color_color = self.saves[room]["pers_det_light"]["color"]
        self.timer_index = self.saves[room]["pers_det_light"]["timer-index"]
        self.toggle_state2 = self.saves[room]["camera_follow"]["state"]

        self._det_pers_light_set()
        self._camera_follow_set()


    def save_options_press(self):
        room = self.room_selector.getRoom() 
        self.saves[room]["pers_det_light"]["state"]       = self.toggle_state1
        self.saves[room]["pers_det_light"]["color"]       = self.toggle1_on_color
        self.saves[room]["pers_det_light"]["timer-index"] = self.timer_index
        self.saves[room]["camera_follow"]["state"]        =  self.toggle_state2

        self.send("AUTOMATION:{}:{}:{}:{}:{}".format(
            room,
            self.toggle_state1,
            self.toggle1_on_color,
            self.timer_options[self.timer_index],
            self.toggle_state2,
            ))
