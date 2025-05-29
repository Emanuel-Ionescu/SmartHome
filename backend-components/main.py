'''
server main program
'''

import multiprocessing as mpc
import threading as thrd
import utils
import cv2
import numpy as np
import os
import time

from utils import Server, load_faces
from model import Model
from camera import Tapo_Camera, DEFAULT_DETECTION_ACCURACY, DEFAULT_RECOGNITION_ACCURACY
from HA_controller import Controller


MASK_COMPARATIONS = 30
max_sim = DEFAULT_RECOGNITION_ACCURACY
min_sim = DEFAULT_RECOGNITION_ACCURACY

room_user = {
    "Livingroom" : "unknown",
    "Bedroom1"   : "unknown",
    "Bedroom2"   : "unknown",
    "Bathroom"   : "unknown",
    "Kitchen"    : "unknown",
    "Garage"     : "unknown"
}

color_dict = {
    "ff0000" : (  0, 100),
    "ff8000" : ( 30, 100),
    "ffff00" : ( 60, 100),
    "80ff00" : ( 90, 100),
      "ff00" : (120, 100),
      "ff80" : (150, 100),
      "ffff" : (180, 100),
      "80ff" : (210, 100),
        "ff" : (240, 100),
    "8000ff" : (270, 100),
    "ff00ff" : (300, 100),
    "ffffff" : ( -1,   1),
    "46424f" : ( -1,   0)
}


time_translate = {
    "Instant": 2,
    "30 sec" : 30,
    "1 min"  : 60,
    "5 min"  : 300, 
    "15 min" : 900, 
    "30 min" : 1800, 
    "1h"     : 3600, 
    "3h"     : 10800, 
    "Never"  : -10
}

def _face_detected_activate_lights(controller, operations, detected_sig):

    var = os.popen('ls -1 $(ls -d -1 house/*/*/)').read()[:-1]
    lights = {}

    for entry in var.split("\n\n"):
        type, devices = entry.split(":\n")
        _, location, type, _ = type.split('/')
        devices = devices.split('\n')
        
        if type == "Lights":
            lights[location] = devices

    while True:
        
        for room in operations.keys():

            if operations[room][0]: #if light automation is ON
                if detected_sig[room]: # if person is detected in room 
                        detected_sig[room] = False
                        for bulb in lights[room]: ## turn ON all the lights from that room
                            try:
                                controller.set(bulb, "ON", {"rgb_color" : operations[room][1]})
                            except: pass

                if operations[room][2] == 0: 
                    for bulb in lights[room]: ## kill all the lights from that room
                            try:
                                controller.set(bulb, "OFF")
                            except: pass

                if operations[room][2] >= 0:
                    operations[room][2] -= 0.5


        time.sleep(0.5)


'''main/main/main/main/main/main/main/main/main/main/main/main/main/main/main/main/main'''
###======================================================================================
###======================================================================================
###=================================== MAIN =============================================
###======================================================================================
###======================================================================================
'''main/main/main/main/main/main/main/main/main/main/main/main/main/main/main/main/main'''


def main():
    
    print("Starting...")
    start_time = time.time()

    ## matter
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTBjOWE4YzZkNzM0NzcxYTI1MjEwNGRmOTVlZDQyZiIsImlhdCI6MTcyNjAxOTIzMSwiZXhwIjoyMDQxMzc5MjMxfQ.GzAwDa2wSxRX9eJPK75soG_iZWTyW-rwnBXOB-dm9cs"
    controller = Controller(token)

    ## users
    mask_queue   = mpc.Queue(128)
    ad_fr_queue  = mpc.Queue(1)
    mask_count   = 0 
    adding_user  = False
    USERS = load_faces()
    print("users found:")
    for u in USERS.keys():
        print(u, len(USERS[u]), "masks")

    ## processes
    detection  = ''  # declared after model initialization 
    addUser    = ''  # declared when used

    ## load ML models 
    frames_queue = mpc.Queue(1)
    result_queue = mpc.Queue(1)

    model = Model()
    model.setup(use_NPU=True)

    print("ML loaded in {} secs".format(time.time() - start_time))
    print("Opening cameras...")

    ## cameras management
    frame   = {}
    light_out = {}
    frame_id = 0
    squares_2_draw = {}

    cam = {}
    cam["Livingroom"] = Tapo_Camera("192.168.1.202", "Tapo-Cam-2", "nxp12345", "Livingroom")
    cam["Bedroom1"]   = Tapo_Camera("192.168.1.201", "Tapo-Cam-1", "nxp12345", "Bedroom1")

    # detection subprocess
    detection = mpc.Process(
        target=utils.__detect_and_process, 
        args=(model, frames_queue, result_queue)
        )
    detection.start()

    # automation 
    operations = {}
    detected_sigs = {}
    for room in ["Livingroom", "Bedroom1", "Bedroom2", "Bathroom", "Kitchen", "Garage"]:
        operations[room] = [False, [255, 255, 255], "1 min"]  ##state, color, time
        detected_sigs[room] = False

    auto_light_state = operations.copy()
    auto_light_thread = thrd.Thread(target=_face_detected_activate_lights, args=(controller, auto_light_state, detected_sigs))
    auto_light_thread.start()
    
    print("Waiting for GUI & web server to connect...")

    server = utils.Server(2, 8080)
    print("2 clients connected")

    server.send(-1, os.popen('ls -1 $(ls -d -1 house/*/*/)').read())

    print("Loading finished in {} secs".format(time.time() - start_time))

    while True:

        ## getting frames from cameras
        frames_list = []
        for k in cam.keys():

            ok, frame[k] = cam[k].read()

            w, h = frame[k].shape[:2]
            b, g, r = cv2.split(frame[k][w//2 - 50 : w//2 + 50, h//2 - 50 : h//2 + 50])
            light_out[k] = not np.any(cv2.subtract(b, g) + cv2.subtract(g, r))

            if ok == False:
                frame[k] = cam[k].error_frame
            else:
                frames_list.append(frame[k])

        ## adding frames to queue for processing
        if not frames_queue.full():
            frames_queue.put((frame_id, frames_list))
            frame_id += 1

        ## adding user
        if adding_user:
            if not ad_fr_queue.full():
                ad_fr_queue.put(frame["Livingroom"])

        inp = server.recieve()
        
        ## process commands
        if inp != '':

            addr, inp = inp
            print(addr, " : ", inp.encode())
            
            ## User management
            if inp.split(':')[0] == "ADD_USER":
                username = inp.split(':')[1]
                mask_count = 0
                adding_user = True
                addUser = mpc.Process(target=utils.__add_user, args=(username, ad_fr_queue, mask_queue))
                addUser.start()

            ## Camera operations
            if inp.split(":")[0] == "CAMERA": 
                cam_name, cam_arg1 = inp.split(":")[1:3] 
                if cam_arg1 != "SET":
                    cam[cam_name].move_1(str(cam_arg1).lower())
                else:
                    cam_arg2 = inp.split(":")[3]
                    if cam_arg2 == "MANUAL": cam[cam_name].manual = True
                    if cam_arg2 == "AUTO"  : cam[cam_name].manual = False

                    if cam_arg2 == "DEBUG"   : cam[cam_name].debug = True
                    if cam_arg2 == "NODEBUG" : cam[cam_name].debug = False 
            
            ## connected devices control
            if inp.split(":")[0] == "DEVICE":
                try:
                    _type_, location, dev_name, state = inp.split(":")[1:]
                    controller.set(dev_name, state)
                except Exception as e:
                    print(e)

            ## lights control
            if inp.split(":")[0] == "BULB":
                try:
                    bulb_location, bulb_name, bulb_state = inp.split(":")[1:]
                    if bulb_state != "46424f":
                        controller.set(bulb_name, "ON", {"rgb_color" : [int(bulb_state[0:2], 16), int(bulb_state[2:4], 16), int(bulb_state[4:6], 16)]})
                    else:
                        controller.set(bulb_name, "OFF")
                except Exception as e:
                    print(e)

            ## automation control
            if inp.split(":")[0] == "AUTOMATION":
                try:
                    
                    _, a_room, auto_light, auto_light_color, auto_light_timer, camera_follow = inp.split(":")
                    cam[a_room].manual = camera_follow == "False"
                    
                    auto_light_color = [
                        int(auto_light_color[0:2], 16), 
                        int(auto_light_color[2:4], 16), 
                        int(auto_light_color[4:6], 16),]
                    operations[a_room] = [auto_light == "True", auto_light_color, time_translate[auto_light_timer]]

                except Exception as e:
                    print(e)

            inp = b''
        
        # getting result from ML models
        if not result_queue.empty():
            for key, res in zip(cam.keys(), result_queue.get()):
                if not cam[key].manual:
                    cam[key].center_face(res[0])
                
                if res[0] is not None:   

                    #server.send(-1, "FACE:{}:{}".format(key, res[0]))
                    print("FACE:{}".format(key))

                    ## send to auto light tread
                    for ky1 in auto_light_state.keys():
                        auto_light_state[ky1] = operations[ky1].copy()
                    detected_sigs[key] = True

                    if cam[key].debug:
                        squares_2_draw[key] = res[0]

                    if key == "Livingroom" and adding_user:
                        mask_count += 1
                        mask_queue.put(res[1])

                        if mask_queue == 128:
                            addUser.kill()
                            adding_user = False
                            USERS = load_faces()
                            server.send(-1, "USER_ADDED")

                    # test similarity   
                    best_user = "unknown"

                    sim = 0
                    max_sim = DEFAULT_RECOGNITION_ACCURACY
                    for username_key in USERS.keys():
                        sim = 0
                        for i in range(min(len(USERS[username_key]), MASK_COMPARATIONS)):
                            sim = max(utils.get_similarity(res[1], USERS[username_key][i]), sim)
                        
                        if sim > max_sim:
                            best_user = username_key
                            max_sim = sim

                    if best_user != "unknown":

                        for entry in room_user.keys():
                            if room_user[entry] == best_user:
                                room_user[entry] = "unknown"

                        room_user[key] = best_user

                        server.send(-1, "DETECTED:{}:{}".format(key, best_user))
                        print("DETECTED: {}:{} <-> \033[31m{}%\033[0m".format(
                                    key, best_user, int(max_sim * 100))
                                )
                        
                    
if __name__ == "__main__":
    main()