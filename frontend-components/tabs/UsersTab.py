from PySide6 import QtWidgets as Qwd
import os

class Tab(Qwd.QWidget):

    def __init__(self, parent, tab_width, tab_height, color_table, send_data_function):
        super().__init__(parent=parent)
        self.setObjectName("users_tab")
        self.setGeometry(0, 0, tab_width, tab_height)
        self.send = send_data_function


        self.ColorTable = color_table

        ##
        ## Design Rules
        ##

        self.bttn_admin_values = {
            "w" : tab_width//8,
            "h" : tab_height//10,
            "text" : "Admin ?",
            "value" : False,
            "normal-color"  : color_table["elem-backg1"],
            "checkd-color"  : color_table["active-col2"],
            "text-color" : color_table["text-light"],
            "border-color" : color_table["text-light"]
        }

        self.input_lines_values = {
            "w" : tab_width//2,
            "h" : tab_height//8,
            "back-color" : color_table["elem-backg1"],
            "text-color" : color_table["active-col1"]
        }

        self.bttn_add_remove_values = {
            "w" : tab_width//6,
            "h" : tab_height//10,
            "add-color" : color_table["active-col2"],
            "remove-color" : "#ff0000",
            "text-color" : color_table["text-light"],
            "border-color" : color_table["text-light"]
        }

        ##
        ## Graphical elements 
        ##

        self.bttn_admin = Qwd.QPushButton(parent=self)
        self.bttn_admin.setGeometry(
            (tab_width - self.bttn_admin_values["w"])//2,
            tab_height//10,
            self.bttn_admin_values["w"],
            self.bttn_admin_values["h"],
        )
        self.bttn_admin.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            border : {a2}px solid {c3};
            border-radius : {a1}px;
            font-size: {a1}px;
            """.format(
                c1 = self.bttn_admin_values["normal-color"],
                c2 = self.bttn_admin_values["text-color"],
                c3 = self.bttn_admin_values["border-color"],
                a1 = self.bttn_admin_values["h"]//3,
                a2 = self.bttn_admin_values["h"]//20
            )
        )
        self.bttn_admin.setText(self.bttn_admin_values["text"] + " No")
        self.bttn_admin.clicked.connect(self.bttn_admin_press)

        self.user_label = Qwd.QLabel(parent=self)
        self.user_label.setText("Username:")
        self.user_label.move(
            (tab_width - self.input_lines_values['w'])//2,
            tab_height//10 * 2,
            )
        self.user_label.setStyleSheet("color: {}; font-size: {}px;".format(
            self.ColorTable["active-col1"], tab_height//20))

        self.input_user = Qwd.QLineEdit(parent=self)
        self.input_user.setGeometry(
            (tab_width - self.input_lines_values['w'])//2,
            tab_height//10 * 3,
            self.input_lines_values['w'],
            self.input_lines_values['h']
        )
        self.input_user.setMaxLength(32)
        self.input_user.focusInEvent = lambda event: self.keyboard_up()
        self.input_user.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            font-size  : {a1}px;
            """.format(
                c1 = self.input_lines_values["back-color"],
                c2 = self.input_lines_values["text-color"],
                a1 = self.input_lines_values["h"]//4 * 3
            )
        )

        self.pin_label = Qwd.QLabel(parent=self)
        self.pin_label.setText("Pin:")
        self.pin_label.move(
            (tab_width - self.input_lines_values['w'])//2,
            tab_height//10 * 5,
            )
        self.pin_label.setStyleSheet("color: {}; font-size: {}px;".format(
            self.ColorTable["active-col1"], tab_height//20))


        self.input_pin = Qwd.QLineEdit(parent=self)
        self.input_pin.setGeometry(
            (tab_width - self.input_lines_values['w'])//2,
            tab_height//10 * 6,
            self.input_lines_values['w'],
            self.input_lines_values['h']
        )
        self.input_pin.setMaxLength(12)
        self.input_pin.setEchoMode(Qwd.QLineEdit.EchoMode.Password)
        self.input_pin.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            font-size  : {a1}px;
            """.format(
                c1 = self.input_lines_values["back-color"],
                c2 = self.input_lines_values["text-color"],
                a1 = self.input_lines_values["h"]//4 * 3
            )
        )

        self.bttn_add_user = Qwd.QPushButton(parent=self)
        self.bttn_add_user.setText("Add User")
        self.bttn_add_user.setGeometry(
            (tab_width - self.bttn_add_remove_values["w"])//4,
            tab_height//10 * 8,
            self.bttn_add_remove_values['w'],
            self.bttn_add_remove_values['h']
        )
        self.bttn_add_user.clicked.connect(self.bttn_add_press)
        self.bttn_add_user.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            font-size : {a1}px;
            border-radius : {a1}px;
            border : {a2}px solid {c3};
            """.format(
                c1 = self.bttn_add_remove_values["add-color"],
                c2 = self.bttn_add_remove_values["text-color"],
                c3 = self.bttn_add_remove_values["border-color"],
                a1 = self.bttn_add_remove_values['h']//3,
                a2 = self.bttn_add_remove_values['h']//20
            )
        )

        self.bttn_remove_user = Qwd.QPushButton(parent=self)
        self.bttn_remove_user.setText("Remove User")
        self.bttn_remove_user.setGeometry(
            (tab_width - self.bttn_add_remove_values["w"])//4 * 3,
            tab_height//10 * 8,
            self.bttn_add_remove_values['w'],
            self.bttn_add_remove_values['h']
        )
        self.bttn_remove_user.clicked.connect(self.bttn_remove_press)
        self.bttn_remove_user.setStyleSheet(
            """
            background : {c1};
            color : {c2};
            font-size : {a1}px;
            border-radius : {a1}px;
            border : {a2}px solid {c3};
            """.format(
                c1 = self.bttn_add_remove_values["remove-color"],
                c2 = self.bttn_add_remove_values["text-color"],
                c3 = self.bttn_add_remove_values["border-color"],
                a1 = self.bttn_add_remove_values['h']//3,
                a2 = self.bttn_add_remove_values['h']//20
            )
        )

    def bttn_admin_press(self):
        
        if self.bttn_admin_values["value"]:
            self.bttn_admin_values["value"] = False
            self.bttn_admin.setText(self.bttn_admin_values["text"] + " No")
            self.bttn_admin.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a2}px solid {c3};
                border-radius : {a1}px;
                font-size: {a1}px;
                """.format(
                    c1 = self.bttn_admin_values["normal-color"],
                    c2 = self.bttn_admin_values["text-color"],
                    c3 = self.bttn_admin_values["border-color"],
                    a1 = self.bttn_admin_values["h"]//3,
                    a2 = self.bttn_admin_values["h"]//20
                )
            )
        else:  
            self.bttn_admin_values["value"] = True
            self.bttn_admin.setText(self.bttn_admin_values["text"] + " Yes")
            self.bttn_admin.setStyleSheet(
                """
                background : {c1};
                color : {c2};
                border : {a2}px solid {c3};
                border-radius : {a1}px;
                font-size: {a1}px;
                """.format(
                    c1 = self.bttn_admin_values["checkd-color"],
                    c2 = self.bttn_admin_values["text-color"],
                    c3 = self.bttn_admin_values["border-color"],
                    a1 = self.bttn_admin_values["h"]//3,
                    a2 = self.bttn_admin_values["h"]//20
                )
            )

    def keyboard_up(self):
        print("Opening keyboard manualy...")

    def bttn_add_press(self):
        print("User= {}".format(self.input_user.text()))
        print("Pin=  {}".format(self.input_pin.text()))
        print("Admin={}".format(self.bttn_admin_values["value"]))

        self.send("ADD_USER:{}".format("emanuel"))

    def bttn_remove_press(self):
        pass