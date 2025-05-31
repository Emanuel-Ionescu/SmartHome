'''
version for server part (imx93)
'''

import os
import cv2
import numpy as np
import threading
import datetime
import time
import queue

import multiprocessing as mpc

from PIL import Image
from requests import get as GET

from pytapo import Tapo

ADMITED_ERROR_X = 250
ADMITED_ERROR_Y = 105

DEFAULT_DETECTION_ACCURACY = 0.3
DEFAULT_RECOGNITION_ACCURACY = 0.81

MAX_HISTORY_LEN = 250
MOVE_SENSIBILITY = 0.2

class Tapo_Camera:

    def __init__(self, host, user, password, name, quality=2):
        self.host = host
        self.user = user
        self.password = password
        self.name = name

        self.cam_link    = "rtsp://{}:{}@{}/stream{}".format(self.user, self.password, self.host, quality)
        self.error_frame = cv2.putText(
            np.ndarray((480, 640, 3), dtype=np.uint8), 
            self.name + " camera not responding", 
            (50, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        self.frame_queue = queue.Queue(1)
        self.frame       = None
        self.ok          = False

        # self.reading_thread = threading.Thread(target=self._read_on_thread, args=(self.frame_queue,))
        # self.reading_thread.start()

        self.manual    = True
        self.debug     = False
        self.MOVE_SENT = 5
        self.tapo      = Tapo(self.host, self.user, self.password)
        self.led       = 0

        time.sleep(3) # wait for connection
        # self.ok, self.frame = self.read()

        self.command_queue = queue.Queue(1)
        self.commands_subprocess = threading.Thread(
            target=self._command_on_thread
        )

        # if self.ok is False:
        #     print("Cam NOT ok")
        # else:
        #     self.width = self.frame.shape[1]
        #     self.height = self.frame.shape[0]
        #     print("Cam OK")
        #     print("Resolution: " + str(self.width) + "x" + str(self.height))
        self.commands_subprocess.start()


    def _read_on_thread(self, frame_q):

        while True:
            cam = cv2.VideoCapture(self.cam_link)
            cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*"MJPG"))

            ok, _ = cam.read()

            while ok:
                ok, frame = cam.read()

                if not frame_q.full():
                    frame_q.put((ok,frame))


    def read(self):

        if not self.frame_queue.empty():
            self.ok, self.frame = self.frame_queue.get()
        
        return self.ok, self.frame
        
    
    def _command_on_thread(self):
        while True:
            if not self.command_queue.empty():
                command_type, args = self.command_queue.get()
                try:
                    if command_type == "direction":
                        self.tapo.moveMotor(*args)
                    if command_type == "LED":
                        self.tapo.setLEDEnabled(args)
                except Exception as e:
                    print(e)
            else:
                time.sleep(0.1)


    def move_1(self, direction): # move 1D
        x = 0
        y = 0

        if direction == "up": 
            y = 1
        if direction == "down": 
            y = -1

        if direction == "right": 
            x = 1
        if direction == "left": 
            x = -1
        
        if not self.command_queue.full() and (x != 0 or y != 0):
            self.command_queue.put(
                ("direction", (self.MOVE_SENT * x, self.MOVE_SENT * y) ) 
            )


    def move(self, directionX, directionY): # move 2D
        
        x = 0
        y = 0

        if directionY == "up": 
            y = 1
        if directionY == "down": 
            y = -1

        if directionX == "right": 
            x = 1
        if directionX == "left": 
            x = -1
        
        if not self.command_queue.full() and (x != 0 or y != 0):
            self.command_queue.put(
                ("direction", (self.MOVE_SENT * x, self.MOVE_SENT * y) ) 
            )
            

    def center_face(self, face, frame=None):
        
        if face is not None:
            G = [int( (face[1] + face[3]) * 0.5 * self.width ), int( (face[0] + face[2]) * 0.5 * self.height ) ]
            directionX = None
            directionY = None

            if frame is not None:
                cv2.circle(frame, G, 3, (0,255,0), 1)
                cv2.circle(frame, G, 1, (0,255,0), 1)


            if G[0] > self.width/2 + ADMITED_ERROR_X:
                directionX = "right"
            elif G[0] < self.width/2 - ADMITED_ERROR_X:
                directionX = "left"

            if G[1] > self.height/2 + ADMITED_ERROR_Y:
                directionY = "down"
            elif G[1] < self.height/2 - ADMITED_ERROR_Y:
                directionY = "up"

            try:
                self.move(directionX, directionY)
            except Exception as e:
                print(e)