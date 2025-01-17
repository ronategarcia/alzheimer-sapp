import random
import time
import warnings
from collections import deque
from tkinter import Image

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk  # Import for displaying images in Tkinter

from result_page import show_result_eyes_tracking

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

# Initialize Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
# Parameters
EAR_THRESHOLD = 0.3
EAR_CONSEC_FRAMES = 3
MOV_AVG_WINDOW_SIZE = 5
FACE_MOVE_THRESHOLD = 15  # Adjust based on your needs
EYE_MOVE_THRESHOLD = 0.15  # Adjust based on your needs


# Function to calculate Euclidean distance
def distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Function to calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye_points):
    A = distance(eye_points[1], eye_points[5])
    B = distance(eye_points[2], eye_points[4])
    C = distance(eye_points[0], eye_points[3])
    ear = (A + B) / (2.0 * C)
    return ear


def resize_frame(frame, ratio=0.5):
    height, width = frame.shape[:2]
    return cv2.resize(frame, (int(width * ratio), int(height * ratio)), interpolation=cv2.INTER_AREA)


def is_face_eyes_moving_same_direction(direction, face_direction, simultaneous_movement):
    # # Check if both eyes and face are moving in the same direction
    if face_direction == "Facing Right" and direction == "Looking Right":
        simultaneous_movement = True
    elif face_direction == "Facing Left" and direction == "Looking Left":
        simultaneous_movement = True
    else:
        simultaneous_movement = False
    return simultaneous_movement


def get_face_direction(face_direction, left_edge_of_face, nose_tip, right_edge_of_face):
    # Calculate the distances between the nose tip and the edges of the face
    distance_to_left_edge = distance(nose_tip, left_edge_of_face)
    distance_to_right_edge = distance(nose_tip, right_edge_of_face)
    # print(f"Distance to left edge: {distance_to_left_edge}")
    # print(f"Distance to right edge: {distance_to_right_edge}")
    # Determine face direction based on the distances
    if abs(distance_to_left_edge - distance_to_right_edge) < FACE_MOVE_THRESHOLD:
        face_direction = "Facing Straight"
    elif distance_to_left_edge < distance_to_right_edge:
        face_direction = "Facing Right"
    elif distance_to_right_edge < distance_to_left_edge:
        face_direction = "Facing Left"
    return face_direction


def get_eye_direction(avg_left_iris_to_inner, avg_left_iris_to_outer, avg_right_iris_to_inner, avg_right_iris_to_outer,
                      direction):
    # Determine direction using both eyes (reversed logic)
    # print(f"Avg left iris to inner: {avg_left_iris_to_inner}")
    # print(f"Avg left iris to outer: {avg_left_iris_to_outer}")
    # print(f"Avg right iris to inner: {avg_right_iris_to_inner}")
    # print(f"Avg right iris to outer: {avg_right_iris_to_outer}")
    if abs(avg_left_iris_to_inner - avg_left_iris_to_outer) <= EYE_MOVE_THRESHOLD \
            and abs(avg_right_iris_to_inner - avg_right_iris_to_outer) <= EYE_MOVE_THRESHOLD:
        direction = "Looking Straight"
    elif avg_left_iris_to_inner < avg_left_iris_to_outer and \
            avg_right_iris_to_inner < avg_right_iris_to_outer:
        direction = "Looking Left"
    elif avg_left_iris_to_outer < avg_left_iris_to_inner \
            and avg_right_iris_to_outer < avg_right_iris_to_inner:
        direction = "Looking Right"

    return direction


def calculate_eye_moving_avg(eye, iris_center):
    eye_inner = eye[1]
    eye_outer = eye[0]
    eye_width = distance(eye_inner, eye_outer)
    iris_to_inner = distance(iris_center, eye_inner)
    iris_to_outer = distance(iris_center, eye_outer)
    normalized_iris_to_inner = iris_to_inner / eye_width
    normalized_iris_to_outer = iris_to_outer / eye_width
    return normalized_iris_to_inner, normalized_iris_to_outer


def get_nose_face_edges_landmarks(frame_height, frame_width, landmarks):
    nose_tip = (landmarks[1].x * frame_width, landmarks[1].y * frame_height)
    left_edge_of_face = (
        landmarks[234].x * frame_width, landmarks[234].y * frame_height)
    right_edge_of_face = (
        landmarks[454].x * frame_width, landmarks[454].y * frame_height)
    return left_edge_of_face, nose_tip, right_edge_of_face


def get_eyes_iris_landmarks(frame_height, frame_width, landmarks):
    # Get landmarks for both eyes and iris centers
    left_eye = [(landmarks[i].x * frame_width, landmarks[i].y * frame_height) for i in
                [33, 133, 160, 159, 158, 144]]
    right_eye = [(landmarks[i].x * frame_width, landmarks[i].y * frame_height) for i in
                 [362, 263, 387, 386, 385, 373]]
    left_iris_center = (landmarks[468].x * frame_width, landmarks[468].y * frame_height)
    right_iris_center = (landmarks[473].x * frame_width, landmarks[473].y * frame_height)
    return left_eye, left_iris_center, right_eye, right_iris_center


def get_random_point(height, width):
    corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])
    boundary = 100
    if corner == 'top-left':
        x = random.randint(0, boundary)
        y = random.randint(0, boundary)
    elif corner == 'top-right':
        x = random.randint(width - boundary, width - 1)
        y = random.randint(0, boundary)
    elif corner == 'bottom-left':
        x = random.randint(0, boundary)
        y = random.randint(height - boundary, height - 1)
    elif corner == 'bottom-right':
        x = random.randint(width - boundary, width - 1)
        y = random.randint(height - boundary, height - 1)

    return x, y


def update_label_result(label, simultaneous_movement_list):
    result = all(simultaneous_movement_list)
    print(f"Simultaneous Movement: {result}")
    label.config(text=f"Simultaneous Movement: {result}")
    label.update()  # Ensure the label_image gets updated
    time.sleep(0.5)  # Pause for half a second to see the update


def start_tracking(window, main_window, label_image, label, video_path=0, seconds=20):
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
    # Capture video
    cap = cv2.VideoCapture(video_path)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    point_coords = get_random_point(height, width)

    # Variables
    left_iris_positions = deque(maxlen=MOV_AVG_WINDOW_SIZE)
    right_iris_positions = deque(maxlen=MOV_AVG_WINDOW_SIZE)
    nose_positions = deque(maxlen=MOV_AVG_WINDOW_SIZE)
    blink_counter = 0
    direction = "Looking Straight"
    face_direction = "Face Straight"
    simultaneous_movement = False
    
    simultaneous_movement_list = []
    label.config(text="When the video starts please look at the red dot.")

   
    current_time = time.time()
    while time.time() - current_time < seconds + 3:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame
        if video_path != 0:
            frame = resize_frame(frame)
        frame_height, frame_width = frame.shape[:2]

        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        cv2.circle(frame, point_coords, 20, (0, 0, 255), -1)  # Draw a red circle at the random point

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                try:
                    left_eye, left_iris_center, right_eye, right_iris_center = get_eyes_iris_landmarks(frame_height,
                                                                                                       frame_width,
                                                                                                       landmarks)
                    left_edge_of_face, nose_tip, right_edge_of_face = get_nose_face_edges_landmarks(frame_height,
                                                                                                    frame_width,
                                                                                                    landmarks)
                    # Calculate EAR for both eyes
                    left_ear = eye_aspect_ratio(left_eye)
                    right_ear = eye_aspect_ratio(right_eye)

                    # Check if either eye is closed (blink detected)
                    if left_ear < EAR_THRESHOLD or right_ear < EAR_THRESHOLD:
                        blink_counter += 1
                    else:
                        if blink_counter >= EAR_CONSEC_FRAMES:
                            # Ignore the iris position when blinking
                            blink_counter = 0
                        else:
                            # Calculate distances and normalize for left eye
                            normalized_left_iris_to_inner, normalized_left_iris_to_outer = calculate_eye_moving_avg(
                                left_eye, left_iris_center)

                            # Append to moving average for left eye
                            left_iris_positions.append((normalized_left_iris_to_inner, normalized_left_iris_to_outer))

                            if len(left_iris_positions) == MOV_AVG_WINDOW_SIZE:
                                avg_left_iris_to_inner, avg_left_iris_to_outer = np.mean(left_iris_positions, axis=0)

                                # Calculate distances and normalize for right eye
                                normalized_right_iris_to_inner, normalized_right_iris_to_outer = calculate_eye_moving_avg(
                                    right_eye, right_iris_center)
                                # Append to moving average for right eye
                                right_iris_positions.append(
                                    (normalized_right_iris_to_inner, normalized_right_iris_to_outer))

                                if len(right_iris_positions) == MOV_AVG_WINDOW_SIZE:
                                    avg_right_iris_to_inner, avg_right_iris_to_outer = np.mean(right_iris_positions,
                                                                                               axis=0)

                                    direction = get_eye_direction(avg_left_iris_to_inner, avg_left_iris_to_outer,
                                                                  avg_right_iris_to_inner, avg_right_iris_to_outer,
                                                                  direction)

                        face_direction = get_face_direction(face_direction, left_edge_of_face, nose_tip,
                                                            right_edge_of_face)

                    simultaneous_movement = is_face_eyes_moving_same_direction(direction, face_direction,
                                                                               simultaneous_movement)
                    simultaneous_movement_list.append(simultaneous_movement)

                    # Display direction and face movement status
                    # cv2.putText(frame, direction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    # cv2.putText(frame, face_direction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    #             cv2.LINE_AA)
                    # cv2.putText(frame, f"Simultaneous Movement: {simultaneous_movement}", (50, 150),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                except IndexError:
                    print(
                        "Landmark index out of range. Ensure you're using the correct indices for the iris and eye corners.")
        if time.time() - current_time > 3:
            window.withdraw()
            cv2.imshow('Alzheimer Eye Tracking', frame)
            
        #frame = resize_frame(frame, ratio=1.2)
        #img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        #img_tk = ImageTk.PhotoImage(image=img)

        # Update the label_image with the new image
        #label_image.img_tk = img_tk  # Keep reference to avoid garbage collection
        #label_image.config(image=img_tk)
        #window.after(10, lambda:None)
        window.update_idletasks()
        window.update()

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()
    # Call the function to update the label_image after the loop ends
    result = all(simultaneous_movement_list)
    title = "Alzheimer\'s Eye Tracking Results: Simultaneous Movement Detected"
    img_path = 'eyes.png'
    if result:
        show_result_eyes_tracking(main_window, window, "Indicators of simultaneous movement have been detected, which align "
                                         "with Alzheimer's symptoms.", title=title, img_path=img_path)
    else:
        show_result_eyes_tracking(main_window, window, "Assessment complete: No symptoms of Alzheimer's detected.",
                                  title=title, img_path=img_path)
