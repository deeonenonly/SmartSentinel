import cv2
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array

# Load the fall detection model
try:
    model = load_model("model.keras")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Print model input shape for debugging
print("Model input shape:", model.input_shape)

# Open the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Preprocess the frame to match the input size of your model
def preprocess_frame(frame):
    # Resize frame to model input size (128x128)
    frame = cv2.resize(frame, (128, 128))
    # Convert to array and add batch dimension
    frame = img_to_array(frame)
    frame = np.expand_dims(frame, axis=0)
    # Normalize pixel values if necessary
    frame = frame / 255.0  # Adjust if your model expects different scaling
    print("Preprocessed frame shape:", frame.shape)
    return frame

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    preprocessed_frame = preprocess_frame(frame)

    try:
        prediction = model.predict(preprocessed_frame)
        print("Prediction:", prediction)
    except Exception as e:
        print(f"Error during prediction: {e}")
        break

    fall_detected = prediction[0][0] > 0.5

    label = "Fall Detected" if fall_detected else "No Fall"
    color = (0, 0, 255) if fall_detected else (0, 255, 0)
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('Fall Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
