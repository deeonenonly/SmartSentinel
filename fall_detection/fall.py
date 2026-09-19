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

# Load YOLOv5 model

yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo_model.classes = [0]
model = models.load_model("model.keras")
pref_size = (128,128)

def print_and_save_bounding_boxes(results, img):
    # Extract image width and height
    #img = Image.open(image_path)
    image_width, image_height, _ = img.shape
    #img_filename = os.path.splitext(os.path.basename(image_path))[0]  # Get filename without path or extension
    random_uuid = uuid.uuid4()
    # Create filename for text file
    filename = f"{random_uuid}.txt"
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
    cv2.rectangle(img_array, (x, y), (x_plus_w, y_plus_h), color, 2)
    

# Function to perform object detection
def detect_objects(img):
    # Load image
    #img = Image.open(image_path)

    # Convert Image object to NumPy array
    img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Note: Color conversion
    results = yolo_model(img, size=640)  # includes NMS
    #results.print()  
    #results.show()
    boxes  = print_and_save_bounding_boxes(results, np.array(img))
    # print("hi:",results.xyxy[0])
    num_bounding_boxes = len(results.xyxy[0])  # Number of bounding boxes
    print(f"Number of Objects Detected {num_bounding_boxes}")
    # Draw bounding boxes
    for i in range(num_bounding_boxes):
        x, y, x_plus_w, y_plus_h, _, _ = results.xyxy[0][i]
        draw_bounding_box(img_array, i + 1, round(x.item()), round(y.item()), round(x_plus_w.item()), round(y_plus_h.item()))

    return boxes


#image_path = r'C:\Users\Divya M\Downloads\archive (1)\fall_dataset\images\val\fall004.jpg'  # replace 'your_image.jpg' with the actual image file path
def predictions (frame):

    #img = plt.imread(image_path)

    img =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    bounding_boxes = detect_objects(img)
    print(bounding_boxes)


    complete_images=[]
    for box in bounding_boxes:
        image_height, image_width, _ = img.shape
        xmin, ymin, width, height = box[:]
        xmin = int(xmin * image_width)
        ymin = int(ymin * image_height)
        width = int(width * image_width)
        height = int(height * image_height)

        complete_images.append(img[ymin-height//2:ymin+height//2, xmin-width//2:xmin+width//2])
    for cropped_img in complete_images:
        #plt.imshow(cropped_img)
        #plt.axis('off')  # Turn off axis
        #plt.show()

        cropped_img_resized = cv2.resize(cropped_img, pref_size)
        #plt.imshow(cropped_img_resized)
        #plt.show()
        cropped_img_resized = cropped_img_resized / 255.0
        
        cropped_img_resized = np.expand_dims(cropped_img_resized, axis=0)
        predictions = model.predict(cropped_img_resized)
        k=np.argmax(predictions)
        print(np.argmax(predictions))
        if(k==0):
            print("Fall detected")
        elif(k==1):
            print("No fall detected. Person is walking or standing")
        else:
            print("No fall detected. Person is sitting.")
#predictions (image_path)

import cv2

# Open the default camera
cam = cv2.VideoCapture(0)

# Get the default frame width and height
#frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
#frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
#fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

while True:
    ret, frame = cam.read()

    # Write the frame to the output file
    # out.write(frame)
    # cv2.imwrite("image.jpg", frame)
    predictions(frame)

    # Display the captured frame
    # cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
#     if cv2.waitKey(1) == ord('q'):
#         break

# # Release the capture and writer objects
# cam.release()
# #out.release()
# cv2.destroyAllWindows()
   