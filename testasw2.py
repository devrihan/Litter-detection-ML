import cv2
import numpy as np
import os
import boto3
import time
from datetime import datetime
import geocoder

# Set AWS credentials environment variable if needed
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA57VDL5JMW75OVYA6'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
s3 = boto3.client('s3')
bucket_name = 'thrash-bin'

def detect_trash(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the color ranges for green and blue dustbins
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    lower_blue = np.array([210, 100, 100])
    upper_blue = np.array([240, 255, 255])

    # Create masks for the dustbins
    mask_green_bin = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue_bin = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_bin = cv2.bitwise_or(mask_green_bin, mask_blue_bin)

    # Erode and dilate to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask_bin = cv2.erode(mask_bin, kernel, iterations=1)
    mask_bin = cv2.dilate(mask_bin, kernel, iterations=1)

    contours, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return frame, False

    largest_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask_trash = cv2.inRange(hsv, lower_white, upper_white)

    trash_contours, _ = cv2.findContours(mask_trash, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    has_trash = len(trash_contours) > 0
    return frame, has_trash

# Function to get the geolocation
def get_location():
    g = geocoder.ip('me')
    return g.latlng

url = 'http://192.0.0.4:8080/video'
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    result_frame, has_trash = detect_trash(frame)
    
    if has_trash:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"trash_detected_{timestamp}.jpg"
        location = get_location()
        
        # Save the image locally
        cv2.imwrite(image_filename, result_frame)
        
        # Upload image to S3 with metadata (location and timestamp)
        s3.upload_file(
            image_filename, 
            bucket_name, 
            image_filename, 
            ExtraArgs={
                'Metadata': {
                    'timestamp': timestamp,
                    'location': f"{location[0]},{location[1]}"
                }
            }
        )
        print(f"Trash detected! Image uploaded to S3 as: {image_filename} with location {location}.")

    cv2.imshow('Trash and Dustbin Detection', result_frame)
    time.sleep(60)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
