import numpy as np
import cv2
import os
import tflite_runtime.interpreter as tflite
import time
from multiprocessing import Queue

from operator import itemgetter
from utils import save_face, load_faces, get_similarity

DEFAULT_DETECTION_ACCURACY = 0.3
DEFAULT_RECOGNITION_ACCURACY = 0.81

class Model:

    def __init__(self, download=False):
        
        self.models = {
            "face_detector" : None,
            "face_id" : None
        }

        self.info = {
            "face_detector" : {"input": None, "output": None},
            "face_id" : {"input": None, "output": None},

        }

        self.links = {
            "models/m1.tflite" : "https://raw.githubusercontent.com/google-coral/test_data/master/ssd_mobilenet_v2_face_quant_postprocess.tflite",
            "models/m2.tflite" : "https://github.com/shubham0204/FaceRecognition_With_FaceNet_Android/raw/master/app/src/main/assets/facenet_int_quantized.tflite"
        } 

        self.delegates_path = "/usr/lib/libethosu_delegate.so"

        if download:
            try:
                os.mkdir("./models")
            except:
                pass
            
            for k in self.links.keys():
                os.system("wget -O ./" + k + " " + self.links[ k ])

        self.operating_mode = 0 # 0 - recognition | 1 - register | 2 - Wait


    def setup(self, use_NPU):

        self.use_NPU = use_NPU

        if self.use_NPU:
            self.delegates = tflite.load_delegate(self.delegates_path)

            for k1, k2 in zip(self.models.keys(), self.links.keys()):
                self.models[k1] = tflite.Interpreter(
                        model_path= k2 , num_threads=4,
                        experimental_delegates=[self.delegates]
                        )
                self.models[k1].allocate_tensors()
                self.info[k1]["input"] = self.models[k1].get_input_details()
                self.info[k1]["output"] = self.models[k1].get_output_details()

        else:
            for k1, k2 in zip(self.models.keys(), self.links.keys()):
                self.models[k1] = tflite.Interpreter(
                        model_path= k2 , num_threads=4
                        )
                self.models[k1].allocate_tensors()
                self.info[k1]["input"] = self.models[k1].get_input_details()
                self.info[k1]["output"] = self.models[k1].get_output_details()


    def getDetails(self):

        for k in self.models.keys():
            print("-----------------------------------")
            for i, e in zip(self.info[k]["input"], range(len(self.info[k]["input"]))):
                print("Input: " + str(e + 1))
                for j in i.keys(): print(str(k) + " : " + str(i[j]))
                print()

            for i, e in zip(self.info[k]["input"], range(len(self.info[k]["input"]))):
                print("Input: " + str(e + 1))
                for j in i.keys(): print(str(k) + " : " + str(i[j]))
                print()

            print("-----------------------------------")

        os.system("read p")


    def valid_face(self, face):
        """Checks if the give face bounding box falls outside the image"""
        for cord in range(4):
            if face[cord] < 0:
                return False
        return True


    def find_faces(self, frame):
        input_img = cv2.resize(frame, 
                               [
                                   self.info["face_detector"]["input"][0]["shape"][1], 
                                   self.info["face_detector"]["input"][0]["shape"][2]
                                ])
        input_img = np.expand_dims(input_img, axis=0)
        if self.info["face_detector"]["input"][0]["dtype"] == np.float32:
            input_img = np.float32(input_img) / 255
        self.models["face_detector"].set_tensor(
            self.info["face_detector"]["input"][0]["index"], 
            input_img
            )
        self.models["face_detector"].invoke()

        face_boxes = self.models["face_detector"].get_tensor(
            self.info["face_detector"]["output"][0]["index"]
        )[0]
        face_scores = self.models["face_detector"].get_tensor(
            self.info["face_detector"]["output"][2]["index"]
        )[0]
        face_total = self.models["face_detector"].get_tensor(
            self.info["face_detector"]["output"][3]["index"]
        )[0]

        output = []
        for i in range(int(face_total)):
            if self.valid_face(face_boxes[i]) and face_scores[i] >= DEFAULT_DETECTION_ACCURACY:
                output.append( (face_boxes[i], face_scores[i]) )

        if output == []:
            return None

        sorted(output, key=itemgetter(1))
        return output
    

    def id_faces(self, frame):
        input_img = cv2.resize(frame, 
                               [
                                   self.info["face_id"]["input"][0]["shape"][1], 
                                   self.info["face_id"]["input"][0]["shape"][2]
                                ])
        input_img = np.expand_dims(input_img, axis=0)
        if self.info["face_id"]["input"][0]["dtype"] == np.float32:
            input_img = np.float32(input_img) / 255
        self.models["face_id"].set_tensor(
            self.info["face_id"]["input"][0]["index"], 
            input_img
            )
        self.models["face_id"].invoke()
        face_map = self.models["face_id"].get_tensor(
            self.info["face_id"]["output"][0]["index"]
        )[0]
        return face_map
    

    