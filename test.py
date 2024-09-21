import cv2
import numpy as np

def detect_trash(frame):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the color range for the green dustbin
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])

    # Define the color range for the blue dustbin
    lower_blue = np.array([210, 100, 100])
    upper_blue = np.array([240, 255, 255])

    # Create masks for the green and blue dustbins
    mask_green_bin = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue_bin = cv2.inRange(hsv, lower_blue, upper_blue)

    # Combine masks for both dustbins
    mask_bin = cv2.bitwise_or(mask_green_bin, mask_blue_bin)

    # Morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    mask_bin = cv2.erode(mask_bin, kernel, iterations=1)
    mask_bin = cv2.dilate(mask_bin, kernel, iterations=1)

    # Find contours for the dustbins (green or blue)
    contours, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return frame, False  # No dustbin detected

    # Get the largest contour, which should be the dustbin
    largest_contour = max(contours, key=cv2.contourArea)

    # Draw the contour for the dustbin
    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)  # Green for dustbin outline

    # Define the color range for detecting white substances
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    # Create a mask for the white substance
    mask_trash = cv2.inRange(hsv, lower_white, upper_white)

    # Find contours for white substances
    trash_contours, _ = cv2.findContours(mask_trash, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    has_trash = len(trash_contours) > 0  # True if any white substance is detected

    return frame, has_trash

url = 'http://172.18.226.67:8080/video'
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()  # Capture frame-by-frame

    if not ret:
        print("Failed to grab frame")
        break

    # Detect trash and dustbin in the frame
    result_frame, has_trash = detect_trash(frame)

    # Display the result
    if has_trash:
        cv2.putText(result_frame, "Trash Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        print("trash detected")

    else:
        cv2.putText(result_frame, "No Trash Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        print("No thrash detected")

    cv2.imshow('Trash and Dustbin Detection', result_frame)  # Show the result

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
