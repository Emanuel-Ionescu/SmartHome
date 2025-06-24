import numpy as np
import cv2
import os
import tflite_runtime.interpreter as tflite
import time
import enum
import subprocess

from typing import Dict, List
from operator import itemgetter

DEFAULT_DETECTION_ACCURACY = 0.15
DEFAULT_RECOGNITION_ACCURACY = 0.81

DEFAULT_BODY_ACCURACY = 0.4

MIN_CROP_KEYPOINT_SCORE = 0.2
TORSO_EXPANSION_RATIO = 1.9
BODY_EXPANSION_RATIO = 1.2

class BodyPart(enum.Enum):
  """Enum representing human body keypoints detected by pose estimation models."""
  NOSE = 0
  LEFT_EYE = 1
  RIGHT_EYE = 2
  LEFT_EAR = 3
  RIGHT_EAR = 4
  LEFT_SHOULDER = 5
  RIGHT_SHOULDER = 6
  LEFT_ELBOW = 7
  RIGHT_ELBOW = 8
  LEFT_WRIST = 9
  RIGHT_WRIST = 10
  LEFT_HIP = 11
  RIGHT_HIP = 12
  LEFT_KNEE = 13
  RIGHT_KNEE = 14
  LEFT_ANKLE = 15
  RIGHT_ANKLE = 16


class Model:

    def __init__(self, download=False, use_NPU=False, delegates = None):
        
        # Get platform
        self.platform = subprocess.check_output(
            ["cat", "/sys/devices/soc0/soc_id"]
        ).decode("utf-8")[:-1]

        self.models = {
            "face_detector"    : None,
            "face_id"          : None,
            "pose_estimation" : None
        }
        self.info = {
            "face_detector"    : {"input": None, "output": None},
            "face_id"          : {"input": None, "output": None},
            "pose_estimation" : {"input": None, "output": None}
        }

        if self.platform == "i.MX93":
            delegates = "/usr/lib/libethosu_delegate.so"
            self.links = {
                "optimised_models/m1.tflite" : "https://raw.githubusercontent.com/google-coral/test_data/master/ssd_mobilenet_v2_face_quant_postprocess.tflite",
                "optimised_models/m2.tflite" : "https://github.com/shubham0204/FaceRecognition_With_FaceNet_Android/raw/master/app/src/main/assets/facenet_int_quantized.tflite",
                "optimised_models/m3.tflite" : "https://github.com/nxp-imx-support/nxp-demo-experience-assets/raw/lf-6.6.36_2.1.0/models/movenet_quant.tflite"
            } 
        else:
            self.links = {
                "models/m1.tflite" : "https://raw.githubusercontent.com/google-coral/test_data/master/ssd_mobilenet_v2_face_quant_postprocess.tflite",
                "models/m2.tflite" : "https://github.com/shubham0204/FaceRecognition_With_FaceNet_Android/raw/master/app/src/main/assets/facenet_int_quantized.tflite",
                "models/m3.tflite" : "https://github.com/nxp-imx-support/nxp-demo-experience-assets/raw/lf-6.6.36_2.1.0/models/movenet_quant.tflite"
            } 
            if delegates is None:
                delegates = "/usr/lib/libvx_delegate.so" # for imx8mp

        self.delegates_path = delegates
        if download:
            try:
                os.mkdir("./models")
                if self.platform == "i.MX93":
                    os.mkdir("./optimised_models")
            except:
                pass
            for k in self.links.keys():
                model_name = k.split('/')[1]
                os.system("wget -O ./models/"+ model_name + " " + self.links[ k ])
                if self.platform == "i.MX93":
                    os.system("vela ./models/" + model_name + " --output-dir ./optimised_models")
                    os.system("mv ./optimised_models/" + model_name.split('.')[0] + "*.tflite ./optimised_models/" + model_name)

        if use_NPU:
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


        self._crop_region = None

    def getDetails(self):
        for k in self.models.keys():
            print("-----------------------------------")
            print("Name", k)
            for i, e in zip(self.info[k]["input"], range(len(self.info[k]["input"]))):
                print("Input: " + str(e + 1))
                for j in i.keys(): print(str(k) + " : " + str(i[j]))
                print()

            for i, e in zip(self.info[k]["output"], range(len(self.info[k]["output"]))):
                print("Output: " + str(e + 1))
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
        print(face_scores)
        for i in range(int(face_total)):
            if self.valid_face(face_boxes[i]) and face_scores[i] >= DEFAULT_DETECTION_ACCURACY:
                output.append( (face_boxes[i], face_scores[i]) )

        if output == []:
            return None

        sorted(output, key=itemgetter(1))
        return output
    

    def id_face(self, frame):
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
        return self.models["face_id"].get_tensor(
            self.info["face_id"]["output"][0]["index"]
        )[0]

    # ==================================================================================
    #  FROM GOOGLE 
    # ==================================================================================

    # Copyright 2021 The TensorFlow Authors. All Rights Reserved.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    """Code to run a pose estimation with a TFLite MoveNet model."""

    def init_crop_region(self, image_height: int,
                       image_width: int) -> Dict[(str, float)]:
        """Defines the default crop region.

        The function provides the initial crop region (pads the full image from
        both sides to make it a square image) when the algorithm cannot reliably
        determine the crop region from the previous frame.

        Args:
        image_height (int): The input image width
        image_width (int): The input image height

        Returns:
        crop_region (dict): The default crop region.
        """
        if image_width > image_height:
            x_min = 0.0
            box_width = 1.0
            # Pad the vertical dimension to become a square image.
            y_min = (image_height / 2 - image_width / 2) / image_height
            box_height = image_width / image_height
        else:
            y_min = 0.0
            box_height = 1.0
            # Pad the horizontal dimension to become a square image.
            x_min = (image_width / 2 - image_height / 2) / image_width
            box_width = image_height / image_width

        return {
            'y_min': y_min,
            'x_min': x_min,
            'y_max': y_min + box_height,
            'x_max': x_min + box_width,
            'height': box_height,
            'width': box_width
        }

    def _torso_visible(self, keypoints: np.ndarray) -> bool:
        """Checks whether there are enough torso keypoints.

        This function checks whether the model is confident at predicting one of
        the shoulders/hips which is required to determine a good crop region.

        Args:
        keypoints: Detection result of Movenet model.

        Returns:
        True/False
        """
        left_hip_score = keypoints[BodyPart.LEFT_HIP.value, 2]
        right_hip_score = keypoints[BodyPart.RIGHT_HIP.value, 2]
        left_shoulder_score = keypoints[BodyPart.LEFT_SHOULDER.value, 2]
        right_shoulder_score = keypoints[BodyPart.RIGHT_SHOULDER.value, 2]

        left_hip_visible = left_hip_score > MIN_CROP_KEYPOINT_SCORE
        right_hip_visible = right_hip_score > MIN_CROP_KEYPOINT_SCORE
        left_shoulder_visible = left_shoulder_score > MIN_CROP_KEYPOINT_SCORE
        right_shoulder_visible = right_shoulder_score > MIN_CROP_KEYPOINT_SCORE

        return ((left_hip_visible or right_hip_visible) and
                (left_shoulder_visible or right_shoulder_visible))

    def _determine_torso_and_body_range(self, keypoints: np.ndarray,
                                      target_keypoints: Dict[(str, float)],
                                      center_y: float,
                                      center_x: float) -> List[float]:
        """Calculates the maximum distance from each keypoints to the center.

        The function returns the maximum distances from the two sets of keypoints:
        full 17 keypoints and 4 torso keypoints. The returned information will
        be used to determine the crop size. See determine_crop_region for more
        details.

        Args:
        keypoints: Detection result of Movenet model.
        target_keypoints: The 4 torso keypoints.
        center_y (float): Vertical coordinate of the body center.
        center_x (float): Horizontal coordinate of the body center.

        Returns:
        The maximum distance from each keypoints to the center location.
        """
        torso_joints = [
            BodyPart.LEFT_SHOULDER, BodyPart.RIGHT_SHOULDER, BodyPart.LEFT_HIP,
            BodyPart.RIGHT_HIP
        ]
        max_torso_yrange = 0.0
        max_torso_xrange = 0.0
        for joint in torso_joints:
            dist_y = abs(center_y - target_keypoints[joint][0])
            dist_x = abs(center_x - target_keypoints[joint][1])
            if dist_y > max_torso_yrange:
                max_torso_yrange = dist_y
            if dist_x > max_torso_xrange:
                max_torso_xrange = dist_x

        max_body_yrange = 0.0
        max_body_xrange = 0.0
        for idx in range(len(BodyPart)):
            if keypoints[BodyPart(idx).value, 2] < MIN_CROP_KEYPOINT_SCORE:
                continue
            dist_y = abs(center_y - target_keypoints[joint][0])
            dist_x = abs(center_x - target_keypoints[joint][1])
            if dist_y > max_body_yrange:
                max_body_yrange = dist_y

            if dist_x > max_body_xrange:
                max_body_xrange = dist_x

        return [
            max_torso_yrange, max_torso_xrange, max_body_yrange, max_body_xrange
        ]

    def _determine_crop_region(self, keypoints: np.ndarray, image_height: int,
                             image_width: int) -> Dict[(str, float)]:
        """Determines the region to crop the image for the model to run inference on.

        The algorithm uses the detected joints from the previous frame to
        estimate the square region that encloses the full body of the target
        person and centers at the midpoint of two hip joints. The crop size is
        determined by the distances between each joints and the center point.
        When the model is not confident with the four torso joint predictions,
        the function returns a default crop which is the full image padded to
        square.

        Args:
        keypoints: Detection result of Movenet model.
        image_height (int): The input image width
        image_width (int): The input image height

        Returns:
        crop_region (dict): The crop region to run inference on.
        """
        # Convert keypoint index to human-readable names.
        target_keypoints = {}
        for idx in range(len(BodyPart)):
            target_keypoints[BodyPart(idx)] = [
                keypoints[idx, 0] * image_height, keypoints[idx, 1] * image_width
            ]

        # Calculate crop region if the torso is visible.
        if self._torso_visible(keypoints):
            center_y = (target_keypoints[BodyPart.LEFT_HIP][0] +
                        target_keypoints[BodyPart.RIGHT_HIP][0]) / 2
            center_x = (target_keypoints[BodyPart.LEFT_HIP][1] +
                        target_keypoints[BodyPart.RIGHT_HIP][1]) / 2

            (max_torso_yrange, max_torso_xrange, max_body_yrange,
            max_body_xrange) = self._determine_torso_and_body_range(
                keypoints, target_keypoints, center_y, center_x)

            crop_length_half = np.amax([
                max_torso_xrange * TORSO_EXPANSION_RATIO,
                max_torso_yrange * TORSO_EXPANSION_RATIO,
                max_body_yrange * BODY_EXPANSION_RATIO,
                max_body_xrange * BODY_EXPANSION_RATIO
            ])

            # Adjust crop length so that it is still within the image border
            distances_to_border = np.array(
                [center_x, image_width - center_x, center_y, image_height - center_y])
            crop_length_half = np.amin(
                [crop_length_half, np.amax(distances_to_border)])

            # If the body is large enough, there's no need to apply cropping logic.
            if crop_length_half > max(image_width, image_height) / 2:
                return self.init_crop_region(image_height, image_width)
            # Calculate the crop region that nicely covers the full body.
            else:
                crop_length = crop_length_half * 2
            crop_corner = [center_y - crop_length_half, center_x - crop_length_half]
            return {
                'y_min':
                    crop_corner[0] / image_height,
                'x_min':
                    crop_corner[1] / image_width,
                'y_max': (crop_corner[0] + crop_length) / image_height,
                'x_max': (crop_corner[1] + crop_length) / image_width,
                'height': (crop_corner[0] + crop_length) / image_height -
                            crop_corner[0] / image_height,
                'width': (crop_corner[1] + crop_length) / image_width -
                        crop_corner[1] / image_width
            }
            # Return the initial crop regsion if the torso isn't visible.
        else:
            return self.init_crop_region(image_height, image_width)

    def _crop_and_resize(
        self, image: np.ndarray, crop_region: Dict[(str, float)],
        crop_size: (int, int)) -> np.ndarray:
        """Crops and resize the image to prepare for the model input."""
        y_min, x_min, y_max, x_max = [
            crop_region['y_min'], crop_region['x_min'], crop_region['y_max'],
            crop_region['x_max']
        ]

        crop_top = int(0 if y_min < 0 else y_min * image.shape[0])
        crop_bottom = int(image.shape[0] if y_max >= 1 else y_max * image.shape[0])
        crop_left = int(0 if x_min < 0 else x_min * image.shape[1])
        crop_right = int(image.shape[1] if x_max >= 1 else x_max * image.shape[1])

        padding_top = int(0 - y_min * image.shape[0] if y_min < 0 else 0)
        padding_bottom = int((y_max - 1) * image.shape[0] if y_max >= 1 else 0)
        padding_left = int(0 - x_min * image.shape[1] if x_min < 0 else 0)
        padding_right = int((x_max - 1) * image.shape[1] if x_max >= 1 else 0)

        # Crop and resize image
        output_image = image[crop_top:crop_bottom, crop_left:crop_right]
        output_image = cv2.copyMakeBorder(output_image, padding_top, padding_bottom,
                                        padding_left, padding_right,
                                        cv2.BORDER_CONSTANT)
        output_image = cv2.resize(output_image, (crop_size[0], crop_size[1]))

        return output_image

    def _run_detector(
        self, image: np.ndarray, crop_region: Dict[(str, float)],
        crop_size: (int, int)) -> np.ndarray:
        """Runs model inference on the cropped region.

        The function runs the model inference on the cropped region and updates
        the model output to the original image coordinate system.

        Args:
        image: The input image.
        crop_region: The region of interest to run inference on.
        crop_size: The size of the crop region.

        Returns:
        An array of shape [17, 3] representing the keypoint absolute coordinates
        and scores.
        """

        input_image = self._crop_and_resize(image, crop_region, crop_size=crop_size)
        # input_image = input_image.astype(dtype=np.uint8)

        input_image = cv2.resize(input_image, 
            [
                self.info["pose_estimation"]["input"][0]["shape"][1], 
                self.info["pose_estimation"]["input"][0]["shape"][2]
            ])
        #input_image = np.expand_dims(input_image, axis=0)
        if self.info["pose_estimation"]["input"][0]["dtype"] == np.int32:
            input_image = np.int32(input_image) #added by me

        self.models["pose_estimation"].set_tensor(
            self.info["pose_estimation"]["input"][0]["index"], 
            np.expand_dims(input_image, axis=0)
            )
        self.models["pose_estimation"].invoke()

        keypoints_with_scores = self.models["pose_estimation"].get_tensor(
            self.info["pose_estimation"]["output"][0]["index"]
        )
        keypoints_with_scores = np.squeeze(keypoints_with_scores)

        # Update the coordinates.
        for idx in range(len(BodyPart)):
            keypoints_with_scores[idx, 0] = crop_region[
                'y_min'] + crop_region['height'] * keypoints_with_scores[idx, 0]
            keypoints_with_scores[idx, 1] = crop_region[
                'x_min'] + crop_region['width'] * keypoints_with_scores[idx, 1]

        return keypoints_with_scores

    def find_body(self,
                input_image: np.ndarray,
                reset_crop_region: bool = False) -> list:
        
        """Run detection on an input image.

        Args:
        input_image: A [height, width, 3] RGB image. Note that height and width
            can be anything since the image will be immediately resized according to
            the needs of the model within this function.
        reset_crop_region: Whether to use the crop region inferred from the
            previous detection result to improve accuracy. Set to True if this is a
            frame from a video. Set to False if this is a static image. Default
            value is True.

        Returns:
        An array of shape [17, 3] representing the keypoint coordinates and
        scores.
        """
        image_height, image_width, _ = input_image.shape
        if (self._crop_region is None) or reset_crop_region:
            # Set crop region for the first frame.
            self._crop_region = self.init_crop_region(image_height, image_width)

        # Detect pose using the crop region inferred from the detection result in
        # the previous frame
        keypoint_with_scores = self._run_detector(
            input_image,
            self._crop_region,
            crop_size=(
                        self.info["face_id"]["input"][0]["shape"][1], 
                        self.info["face_id"]["input"][0]["shape"][2]
                    )
                )
        # Calculate the crop region for the next frame
        self._crop_region = self._determine_crop_region(keypoint_with_scores,
                                                        image_height, image_width)

        # Convert the keypoints with scores to a Person data type

        if (keypoint_with_scores[:,2]).mean() >= DEFAULT_BODY_ACCURACY:
            return [
                        keypoint_with_scores[:,0] * image_height, 
                        keypoint_with_scores[:,1] * image_width, 
                        keypoint_with_scores[:,2]
                    ]
        else:
            return None
