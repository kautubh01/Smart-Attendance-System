import face_recognition
import cv2
import numpy as np
import os
import xlrd
import xlwt
from xlwt import Workbook
from xlutils.copy import copy as xl_copy
from datetime import date

# Set up paths for images
CurrentFolder = os.getcwd()  # Current working directory
image1_path = os.path.join(CurrentFolder, 'kaustubh.png')
image2_path = os.path.join(CurrentFolder, 'sneha.png')

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

# Load the sample images and learn their face encodings
person1_name = "Kaustubh"
person2_name = "Sneha"

try:
    person1_image = face_recognition.load_image_file(image1_path)
    person1_face_encodings = face_recognition.face_encodings(person1_image)
    person1_face_encoding = person1_face_encodings[0] if person1_face_encodings else None

    person2_image = face_recognition.load_image_file(image2_path)
    person2_face_encodings = face_recognition.face_encodings(person2_image)
    person2_face_encoding = person2_face_encodings[0] if person2_face_encodings else None
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

# Check if valid encodings are available
if person1_face_encoding is None or person2_face_encoding is None:
    print("Error: Could not detect faces in one or more images.")
    exit()

# Arrays of known face encodings and their names
known_face_encodings = [person1_face_encoding, person2_face_encoding]
known_face_names = [person1_name, person2_name]

# Initialize attendance sheet
attendance_file = 'attendance_excel.xls'

# Load existing attendance file or create a new one
if os.path.exists(attendance_file):
    rb = xlrd.open_workbook(attendance_file, formatting_info=True)
    wb = xl_copy(rb)
else:
    wb = Workbook()

# Create a new sheet for the current subject
subject_name = input("Enter the current lecture subject name: ")
sheet = wb.add_sheet(subject_name)
sheet.write(0, 0, 'Name')
sheet.write(0, 1, 'Date')
sheet.write(0, 2, 'Status')
sheet.write(1, 1, str(date.today()))

# Variables to keep track of attendance
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
already_marked = set()
row_index = 2

while True:
    # Capture frame from the webcam
    ret, frame = video_capture.read()

    # Resize frame to 1/4 size for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR (OpenCV) to RGB (face_recognition)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Process every other frame
    if process_this_frame:
        # Detect faces and compute encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Compare detected faces with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

            # Mark attendance if the person is recognized and not already marked
            if name != "Unknown" and name not in already_marked:
                sheet.write(row_index, 0, name)
                sheet.write(row_index, 2, "Present")
                row_index += 1
                already_marked.add(name)
                print(f"Attendance marked for {name}.")
                wb.save(attendance_file)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back face locations to original frame size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with the name
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Show the video feed
    cv2.imshow('Video', frame)

    # Break on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting and saving data...")
        break

# Release webcam and close OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
