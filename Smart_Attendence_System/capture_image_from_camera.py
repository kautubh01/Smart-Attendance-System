import cv2

# Initialize the camera
cam_port = 1  # Camera index (try 0 if 1 doesn't work)
cam = cv2.VideoCapture(cam_port)

if not cam.isOpened():
    print("Error: Camera not found or cannot be accessed.")
    exit()

# Prompt for person's name
inp = input("Enter the person's name: ").strip()

if not inp:
    print("Error: Name cannot be empty.")
    exit()

print("Press 's' to capture the image, or 'q' to quit.")

while True:
    # Read a frame from the camera
    ret, frame = cam.read()
    
    if not ret:
        print("Error: Unable to read from camera.")
        break

    # Display the live video feed
    cv2.imshow("Camera Feed", frame)

    # Wait for user input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Press 's' to save the image
        file_name = f"{inp}.png"
        cv2.imwrite(file_name, frame)
        print(f"Image saved as {file_name}")
        break
    elif key == ord('q'):  # Press 'q' to quit
        print("Exiting without saving.")
        break

# Release resources and close the window
cam.release()
cv2.destroyAllWindows()
