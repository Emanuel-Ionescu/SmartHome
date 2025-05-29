from PySide6 import QtWidgets as Qwd
from PySide6 import QtCore

import utils 

class RoomSelector(Qwd.QWidget):

    roomChanged = QtCore.Signal(str)

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function, parent_name):
        super().__init__(parent=parent)
        self.send = send_data_function
        self.parent_name = parent_name
        
        self.values = {
            "w" : tab_width//8,
            "h" : tab_height//2,
            "background" : color_table["elem-backg1"],
            "text" : color_table["active-col2"],
            "border-color" : color_table["active-col2"]
        }

        self.room_index = 0

        self.setGeometry(
            tab_width - self.values["w"],
            (tab_height - self.values["h"])//3,
            self.values["w"],
            self.values["h"]
        )

        self.setStyleSheet(
            """
                background : {c1};
                color : {c2};
                border: {a1}px solid {c3};
                margin: {a2}px;
                font-size: {a3}px; 
                """.format(
                    c1 = self.values["background"],
                    c2 = self.values["text"],
                    c3 = self.values["border-color"],
                    a1 = self.values["h"]//200,
                    a2 = self.values["h"]//200,
                    a3 = self.values["h"]//20
                )
        )

        self.rooms = ["Livingroom", "Bedroom1", "Bedroom2", "Bathroom", "Kitchen", "Garage"]
        self.room_bttns = [] 

        for i, r in enumerate(self.rooms):
            self.room_bttns.append(Qwd.QPushButton(parent=self, text=str(r)))
            self.room_bttns[-1].setGeometry(
                0,
                self.values['h']//len(self.rooms) * i,
                self.values['w'],
                self.values['h']//len(self.rooms)
                )
            self.room_bttns[-1].clicked.connect(self.roomClick_template(self.rooms[i]))
            
        self.setRoom("Livingroom")
        self.send("ROOM:{}:{}".format(self.parent_name, "Livingroom"))
            
    def getRoom(self):
        return self.rooms[self.room_index]
    
    def setRoom(self, arg):

        self.room_bttns[self.room_index].setStyleSheet(
            """
                background : {c1};
                color : {c2};
                border: {a1}px solid {c3};
                margin: {a2}px;
                font-size: {a3}px;            
            """.format(
                        c1 = self.values["background"],
                        c2 = self.values["text"],
                        c3 = self.values["border-color"],
                        a1 = self.values["h"]//200,
                        a2 = self.values["h"]//200,
                        a3 = self.values["h"]//20
                    ))

        if type(arg) == int:
            self.room_index = arg
        if type(arg) == str:
            self.room_index = self.rooms.index(arg)

        self.room_bttns[self.room_index].setStyleSheet(
            """
                background : {c3};
                color : {c1};
                border: {a1}px solid {c2};
                margin: {a2}px;
                font-size: {a3}px;            
            """.format(
                        c1 = self.values["background"],
                        c2 = self.values["text"],
                        c3 = self.values["border-color"],
                        a1 = self.values["h"]//200,
                        a2 = self.values["h"]//200,
                        a3 = self.values["h"]//20
                    ))

        self.roomChanged.emit(arg)

    def roomClick_template(self, arg):

        def roomClick():
            self.send("ROOM:{}:{}".format(self.parent_name, arg))
            self.setRoom(arg)

        return roomClick

