'''
version for server components (imx93)
'''

import os
import numpy as np
import cv2
import datetime
import socket
import queue
import time
import threading
import multiprocessing as mpc

from model import Model

class Server:

    def __init__(self, num, SERVER_PORT):
        self.TCP_socket = socket.socket()
        self.TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.TCP_socket.bind(("", SERVER_PORT))
        self.TCP_socket.listen(num)

        self.TCP_connections = []
        self.TCP_addresses   = []
        self.recieve_treads  = []
        
        self.recieved_msg = queue.Queue(20)

        for i in range(num):
            con, addr = self.TCP_socket.accept()
            self.TCP_connections.append(con)
            self.TCP_addresses.append(addr)
            self.recieve_treads.append(threading.Thread(target=self._get_recieved_on_thread, args=(con, self.recieved_msg)))
            self.recieve_treads[-1].start()

    def _get_recieved_on_thread(self, con, recieved_msg):
        stop = False
        
        while stop is False:
            try:
                inp = con.recv(1024).decode()
                if not recieved_msg.full():
                    recieved_msg.put((con.getsockname()[0], inp))
                if inp == b'':
                    stop = True
            except (ConnectionResetError, BrokenPipeError):
                print("Client disconnected. Killing listening...")
                stop = True
        
        print("Thread stopped")

    def send(self,con_num, msg):
        
        if con_num == -1:
            for con in self.TCP_connections:
                con.send(msg.encode())
        else:
            self.TCP_connections[con_num].send(msg.encode())

    def recieve(self):
        msg = ''
        if not self.recieved_msg.empty():
            msg = self.recieved_msg.get()
    
        return msg
    
    def destroy(self):
        for con in self.TCP_connections:
            con.close()
        self.TCP_socket.close()


def load_faces():
    users = {}
    for key in os.listdir("./users_data"):
        if ".face" in os.listdir("./users_data/" + key):

            file = open("./users_data/" + key + "/.face")
            raw_data = file.read()
            file.close()
            masks = raw_data.split('\n')
            for i in range(len(masks)):
                masks[i] = masks[i].split(',')
                masks[i].pop(-1)
                for e in range(len(masks[i])):
                    masks[i][e] = np.float32(masks[i][e])

            masks.pop(-1)
            users[key] = masks

    return users
            

def save_face(username, masks):
    
    file = open("./users_data/" + username + "/.face", 'w')

    for mask in masks:
        for m in mask:
            file.write(str(m) + ',')
        file.write('\n')
    
    file.close()


def get_similarity(face_a, face_b):
        """Finds the similarity between two masks
        This is done by taking the vectors in the face mask and finding the
        cosine similarity between them. The formula to find this is:

                                  f(a[n] * b[n])
        sim (a[],b[]) = -----------------------------------
                         sqrt(f(a[n]^2)) * sqrt(f(b[n]^2))

        where:
        - a[] and b[] both represent the array of values of a single face mask
        - f(n) is the sum of values where n is 0 through the length of a[]
          minus 1
        - a[] and b[] have equal lengths and equal indexes map to the same
          points on the face mask

        The idea behind this method is that vectors that have smaller
        vectors between them (independent of magnitude) should in theory be
        similar.
        """
        dot = 0
        a_sum = 0
        b_sum = 0
        for count in range(128):
            dot = dot + (face_a[count] * face_b[count])
            a_sum = a_sum + (face_a[count] * face_a[count])
            b_sum = b_sum + (face_b[count] * face_b[count])
        sim = dot / (np.sqrt(a_sum) * np.sqrt(b_sum))
        return sim


def __add_user(username, frames_queue, mask_queue):
    masks = []

    iterations = 0
    while iterations < 128:
        if frames_queue.empty():
            time.sleep(0.1)
            continue

        frame = frames_queue.get()
        ok = False

        if not mask_queue.empty():
            iterations += 1
            masks.append(mask_queue.get())
            ok = True

    save_face(username, masks)
    
def __detect_and_process(frames_queue : mpc.Queue, results_queue : mpc.Queue): 
    """
    Add in results queue a tuple of detected face and the generated mask
    """
    start_time = time.time()

    try:
        model = Model(False, True)
    except:
        model = Model(True, True)

    # warm up the NPU
    model.find_faces(np.zeros((300, 300, 3), dtype=np.uint8))
    model.id_face(np.zeros((300, 300, 3), dtype=np.uint8))

    print("ML loaded in {} secs".format(time.time() - start_time))


    def __process_frame(frame, id):
        face_info = model.find_faces(frame)

        if face_info is None:       
            return (None, None, None)
        
        face = face_info[0][0]
        original_face = face.copy()

        face[0] *= frame.shape[0] # height
        face[1] *= frame.shape[1] # width
        face[2] *= frame.shape[0]
        face[3] *= frame.shape[1]

        G = [(face[0]+face[2]) * .5, (face[1]+face[3]) * .5]
        dist = min(face[2] - face[0], face[3] - face[1]) * .5

        face[0] = G[0] - dist
        face[1] = G[1] - dist
        face[2] = G[0] + dist
        face[3] = G[1] + dist

        face = np.array(face, np.int16)

        cropped_frame = frame[face[0] : face[2], face[1] : face[3]]
        mask = model.id_face(cropped_frame)

        return [original_face, mask, id]


    while True:

        if frames_queue.empty():
            time.sleep(0.1)
            continue
        
        frame_id, frames = frames_queue.get() # list of frames, one for each camera 
        print("DETECT SUBPROCESS: Frames readed", frames[0].shape, frames[1].shape)

        results = []

        for frame in frames:
            res = __process_frame(frame, frame_id)
            if res[0] is None:
                h = frame.shape[0] # height
                w = frame.shape[1] # width
                h2 = h//2
                w2 = w//2
                #split frame in 5
                slices = [
                    (frame[0 :h2, 0 :w2], (0.0, 0.0)),
                    (frame[0 :h2, w2: w], (0.0, 0.5)),
                    (frame[h2: h, 0 :w2], (0.5, 0.0)),
                    (frame[h2: h, w2: w], (0.5, 0.5)),
                    (frame[h2//2 : 3*h2//2, w2//2: 3*w2//2] ,(0.25, 0.25))
                ]
                i = 1
                for s in slices:
                    res = __process_frame(s[0], frame_id + i/10)
                    if res[0] is not None:
                        res[0][0] = res[0][0] * 0.5 + s[1][0]
                        res[0][1] = res[0][1] * 0.5 + s[1][1]
                        res[0][2] = res[0][2] * 0.5 + s[1][0]
                        res[0][3] = res[0][3] * 0.5 + s[1][1]
                        break
                    i+=1


            results.append(res)

        print("DETECT SUBPROCESS: Results Ready")
        if not results_queue.full():
            results_queue.put(results)

