import cv2 as cv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import tensorflow.keras as keras
import matplotlib.patches as patches
import os
import torch
from PIL import Image
import uuid

from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, models
from tensorflow.keras.models import load_model



# Load YOLOv5 model

# Load YOLOv5s model from GitHub
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo_model.classes = [0]  # Set specific class for detection (e.g., class 0)

# Load Keras model
keras_model = load_model("/home/divya/PycharmProjects/SmartSentinel/fall_detection/model_fall.keras")

# Preferred input size for Keras model
pref_size = (128, 128)


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
            if(confidence>0.5):
                label = results.names[int(class_id)]
                class_label = class_id
                x_center = (x_min + x_max) / 2 / image_width
                y_center = (y_min + y_max) / 2 / image_height
                norm_width = (x_max - x_min) / image_width
                norm_height = (y_max - y_min) / image_height

                print(f"Labels: {x_center} {y_center} {norm_width} {norm_height} {confidence}")
                print(f"Object {i + 1}: {label} (Confidence: {confidence:.2f})")
                f.write(f"{label} {x_center} {y_center} {norm_width} {norm_height} {confidence}\n")
                temp = [x_center,y_center,norm_width,norm_height]
                boxes.append(temp)
        return boxes

# Function to draw bounding box on the detected object and print coordinates
def draw_bounding_box(img_array, object_number, x, y, x_plus_w, y_plus_h):
    color = (0, 255, 0)  # BGR
    cv.rectangle(img_array, (x, y), (x_plus_w, y_plus_h), color, 2)


# Function to perform object detection
def detect_objects(image_path):
    # Load image
    img = Image.open(image_path)

    # Convert Image object to NumPy array
    img_array = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)  # Note: Color conversion
    results = yolo_model(img, size=640)  # includes NMS
    #results.print()
    #results.show()\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    boxes  = print_and_save_bounding_boxes(results, image_path)
    # print("hi:",results.xyxy[0])
    num_bounding_boxes = len(results.xyxy[0])  # Number of bounding boxes
    print(f"Number of Objects Detected {num_bounding_boxes}")
    # Draw bounding boxes
    for i in range(num_bounding_boxes):
        x, y, x_plus_w, y_plus_h, _, _ = results.xyxy[0][i]
        draw_bounding_box(img_array, i + 1, round(x.item()), round(y.item()), round(x_plus_w.item()), round(y_plus_h.item()))

    return boxes


image_path = '/kaggle/input/trial3/WhatsApp Image 2024-02-08 at 00.53.01_1f29048a.jpg'  # replace 'your_image.jpg' with the actual image file path
def predictions (image_path):
#     img = cv.imread(image_path)
#     img = cv.resize(img, pref_size)
#     img = img / 255.0
#     img = np.expand_dims(img, axis=0)

#     for i in range(len(train_img_files)):
    img = plt.imread(image_path)
#     with open(r2+train_label_files[i],'r') as file:
#         r = file.readlines()
    bounding_boxes = detect_objects(image_path)
    # print(bounding_boxes)
#     for j in r:
#         j = j.split()
#        bounding_boxes.append([int(j[0]),float(j[1]),float(j[2]),float(j[3]),float(j[4])])
    complete_images=[]
    for box in bounding_boxes:
        image_height, image_width, _ = img.shape
        xmin, ymin, width, height = box[:]
        xmin = int(xmin * image_width)
        ymin = int(ymin * image_height)
        width = int(width * image_width)
        height = int(height * image_height)
#         complete_class.append(box[0])
        complete_images.append(img[ymin-height//2:ymin+height//2, xmin-width//2:xmin+width//2])
    for cropped_img in complete_images:
        #plt.imshow(cropped_img)
        #plt.axis('off')  # Turn off axis
        #plt.show()
#         img_n = cv.resize(img, pref_size)
#         plt.imshow(img_n)
#         plt.show()
#         print(img_n.shape)
#         img_n = img_n /255.0
#         img_n = np.expand_dims(img, axis=0)
#         predictions = model.predict(img_n)
#         print(np.argmax(predictions))
        cropped_img_resized = cv.resize(cropped_img, pref_size)
        #plt.imshow(cropped_img_resized)
        # plt.show()
        cropped_img_resized = cropped_img_resized / 255.0
        #cv.imshow(cropped_img_resized)
        cropped_img_resized = np.expand_dims(cropped_img_resized, axis=0)
        predictions = keras_model.predict(cropped_img_resized)
        k=np.argmax(predictions)
        print(np.argmax(predictions))
        if(k==0):
            print("Fall detected")
        elif(k==1):
            print("No fall detected. Person is walking or standing")
        else:
            print("No fall detected. Person is sitting.")

        return k


def fall_main(frame):
    # Your fall detection logic here
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
    cv.imwrite("image.jpg", frame)
    return predictions("image.jpg")


