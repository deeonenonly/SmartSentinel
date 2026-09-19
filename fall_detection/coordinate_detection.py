import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import tensorflow.keras as keras
import matplotlib.patches as patches
import os
import cv2
import torch
from PIL import Image
import uuid

from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, models


yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo_model.classes = [0]
model = models.load_model(r"model.keras")
pref_size = (128,128)


def print_and_save_bounding_boxes(results, image_path):
    # Extract image width and height
    img = Image.open(image_path)
    image_width, image_height = img.size
    img_filename = os.path.splitext(os.path.basename(image_path))[0]  # Get filename without path or extension

    # Create filename for text file
    filename = f"{img_filename}.txt"
    with open(filename, "w") as f:
        boxes =[]
        for i, detection in enumerate(results.pandas().xyxy[0].values):  # Use .values to access data
            x_min, y_min, x_max, y_max, confidence, class_id, *extra_values = detection.tolist()
            if(confidence>0):
                label = results.names[int(class_id)]
                class_label = class_id
                x_center = (x_min + x_max) / 2 / image_width
                x_center_rounded = round(x_center, 6)
                y_center = (y_min + y_max) / 2 / image_height
                y_center_rounded = round(y_center, 6)
                norm_width = (x_max - x_min) / image_width
                norm_width_rounded = round(norm_width , 6)
                norm_height = (y_max - y_min) / image_height
                norm_height_rounded = round(norm_height, 6)

                print(f"Labels: {x_center_rounded} {y_center_rounded} {norm_width_rounded} {norm_height_rounded} {confidence}")
                print(f"Object {i + 1}: {label} (Confidence: {confidence:.2f})")
                f.write(f"{label} {x_center} {y_center} {norm_width} {norm_height} {confidence}\n")
                temp = [x_center,y_center,norm_width,norm_height]
                boxes.append(temp)
        return boxes


image_path =r"/home/divya/PycharmProjects/SmartSentinel/fall_dataset/images/train/not fallen0069.jpg"
img = Image.open(image_path)



# Convert Image object to NumPy array
img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Note: Color conversion
results = yolo_model(img, size=640)  # includes NMS
#results.print()  
results.show()
boxes  = print_and_save_bounding_boxes(results, image_path)
# print("hi:",results.xyxy[0])
num_bounding_boxes = len(results.xyxy[0])  # Number of bounding boxes
print(f"Number of Objects Detected {num_bounding_boxes}")